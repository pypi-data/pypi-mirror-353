from dataclasses import dataclass
from pathlib import Path
import time
from typing import Generator, Tuple, Optional
import numpy as np

import librosa
import torch
import perth
import torch.nn.functional as F
from huggingface_hub import hf_hub_download

from .models.t3 import T3
from .models.s3tokenizer import S3_SR, drop_invalid_tokens
from .models.s3gen import S3GEN_SR, S3Gen
from .models.tokenizers import EnTokenizer
from .models.voice_encoder import VoiceEncoder
from .models.t3.modules.cond_enc import T3Cond


REPO_ID = "ResembleAI/chatterbox"


def punc_norm(text: str) -> str:
    """
        Quick cleanup func for punctuation from LLMs or
        containing chars not seen often in the dataset
    """
    if len(text) == 0:
        return "You need to add some text for me to talk."

    # Capitalise first letter
    if text[0].islower():
        text = text[0].upper() + text[1:]

    # Remove multiple space chars
    text = " ".join(text.split())

    # Replace uncommon/llm punc
    punc_to_replace = [
        ("...", ", "),
        ("…", ", "),
        (":", ","),
        (" - ", ", "),
        (";", ", "),
        ("—", "-"),
        ("–", "-"),
        (" ,", ","),
        ("“", "\""),
        ("”", "\""),
        ("‘", "'"),
        ("’", "'"),
    ]
    for old_char_sequence, new_char in punc_to_replace:
        text = text.replace(old_char_sequence, new_char)

    # Add full stop if no ending punc
    text = text.rstrip(" ")
    sentence_enders = {".", "!", "?", "-", ","}
    if not any(text.endswith(p) for p in sentence_enders):
        text += "."

    return text


@dataclass
class Conditionals:
    """
    Conditionals for T3 and S3Gen
    - T3 conditionals:
        - speaker_emb
        - clap_emb
        - cond_prompt_speech_tokens
        - cond_prompt_speech_emb
        - emotion_adv
    - S3Gen conditionals:
        - prompt_token
        - prompt_token_len
        - prompt_feat
        - prompt_feat_len
        - embedding
    """
    t3: T3Cond
    gen: dict

    def to(self, device):
        self.t3 = self.t3.to(device=device)
        for k, v in self.gen.items():
            if torch.is_tensor(v):
                self.gen[k] = v.to(device=device)
        return self

    def save(self, fpath: Path):
        arg_dict = dict(
            t3=self.t3.__dict__,
            gen=self.gen
        )
        torch.save(arg_dict, fpath)

    @classmethod
    def load(cls, fpath, map_location="cpu"):
        if isinstance(map_location, str):
            map_location = torch.device(map_location)
        kwargs = torch.load(fpath, map_location=map_location, weights_only=True)
        return cls(T3Cond(**kwargs['t3']), kwargs['gen'])


@dataclass
class StreamingMetrics:
    """Metrics for streaming TTS generation"""
    latency_to_first_chunk: Optional[float] = None
    rtf: Optional[float] = None
    total_generation_time: Optional[float] = None
    total_audio_duration: Optional[float] = None
    chunk_count: int = 0


class ChatterboxTTS:
    ENC_COND_LEN = 6 * S3_SR
    DEC_COND_LEN = 10 * S3GEN_SR

    def __init__(
        self,
        t3: T3,
        s3gen: S3Gen,
        ve: VoiceEncoder,
        tokenizer: EnTokenizer,
        device: str,
        conds: Conditionals = None,
    ):
        self.sr = S3GEN_SR  # sample rate of synthesized audio
        self.t3 = t3
        self.s3gen = s3gen
        self.ve = ve
        self.tokenizer = tokenizer
        self.device = device
        self.conds = conds
        self.watermarker = perth.PerthImplicitWatermarker()

    @classmethod
    def from_local(cls, ckpt_dir, device) -> 'ChatterboxTTS':
        ckpt_dir = Path(ckpt_dir)

        # Always load to CPU first for non-CUDA devices to handle CUDA-saved models
        if device in ["cpu", "mps"]:
            map_location = torch.device('cpu')
        else:
            map_location = None

        ve = VoiceEncoder()
        ve.load_state_dict(
            torch.load(ckpt_dir / "ve.pt", map_location=map_location)
        )
        ve.to(device).eval()

        t3 = T3()
        t3_state = torch.load(ckpt_dir / "t3_cfg.pt", map_location=map_location)
        if "model" in t3_state.keys():
            t3_state = t3_state["model"][0]
        t3.load_state_dict(t3_state)
        t3.to(device).eval()

        s3gen = S3Gen()
        s3gen.load_state_dict(
            torch.load(ckpt_dir / "s3gen.pt", map_location=map_location)
        )
        s3gen.to(device).eval()

        tokenizer = EnTokenizer(
            str(ckpt_dir / "tokenizer.json")
        )

        conds = None
        if (builtin_voice := ckpt_dir / "conds.pt").exists():
            conds = Conditionals.load(builtin_voice, map_location=map_location).to(device)

        return cls(t3, s3gen, ve, tokenizer, device, conds=conds)

    @classmethod
    def from_pretrained(cls, device) -> 'ChatterboxTTS':
        # Check if MPS is available on macOS
        if device == "mps" and not torch.backends.mps.is_available():
            if not torch.backends.mps.is_built():
                print("MPS not available because the current PyTorch install was not built with MPS enabled.")
            else:
                print("MPS not available because the current MacOS version is not 12.3+ and/or you do not have an MPS-enabled device on this machine.")
            device = "cpu"
        
        for fpath in ["ve.pt", "t3_cfg.pt", "s3gen.pt", "tokenizer.json", "conds.pt"]:
            local_path = hf_hub_download(repo_id=REPO_ID, filename=fpath)

        return cls.from_local(Path(local_path).parent, device)

    def prepare_conditionals(self, wav_fpath, exaggeration=0.5):
        ## Load reference wav
        s3gen_ref_wav, _sr = librosa.load(wav_fpath, sr=S3GEN_SR)

        ref_16k_wav = librosa.resample(s3gen_ref_wav, orig_sr=S3GEN_SR, target_sr=S3_SR)

        s3gen_ref_wav = s3gen_ref_wav[:self.DEC_COND_LEN]
        s3gen_ref_dict = self.s3gen.embed_ref(s3gen_ref_wav, S3GEN_SR, device=self.device)

        # Speech cond prompt tokens
        if plen := self.t3.hp.speech_cond_prompt_len:
            s3_tokzr = self.s3gen.tokenizer
            t3_cond_prompt_tokens, _ = s3_tokzr.forward([ref_16k_wav[:self.ENC_COND_LEN]], max_len=plen)
            t3_cond_prompt_tokens = torch.atleast_2d(t3_cond_prompt_tokens).to(self.device)

        # Voice-encoder speaker embedding
        ve_embed = torch.from_numpy(self.ve.embeds_from_wavs([ref_16k_wav], sample_rate=S3_SR))
        ve_embed = ve_embed.mean(axis=0, keepdim=True).to(self.device)

        t3_cond = T3Cond(
            speaker_emb=ve_embed,
            cond_prompt_speech_tokens=t3_cond_prompt_tokens,
            emotion_adv=exaggeration * torch.ones(1, 1, 1),
        ).to(device=self.device)
        self.conds = Conditionals(t3_cond, s3gen_ref_dict)

    def generate(
        self,
        text,
        audio_prompt_path=None,
        exaggeration=0.5,
        cfg_weight=0.5,
        temperature=0.8,
    ):
        if audio_prompt_path:
            self.prepare_conditionals(audio_prompt_path, exaggeration=exaggeration)
        else:
            assert self.conds is not None, "Please `prepare_conditionals` first or specify `audio_prompt_path`"

        # Update exaggeration if needed
        if exaggeration != self.conds.t3.emotion_adv[0, 0, 0]:
            _cond: T3Cond = self.conds.t3
            self.conds.t3 = T3Cond(
                speaker_emb=_cond.speaker_emb,
                cond_prompt_speech_tokens=_cond.cond_prompt_speech_tokens,
                emotion_adv=exaggeration * torch.ones(1, 1, 1),
            ).to(device=self.device)

        # Norm and tokenize text
        text = punc_norm(text)
        text_tokens = self.tokenizer.text_to_tokens(text).to(self.device)
        text_tokens = torch.cat([text_tokens, text_tokens], dim=0)  # Need two seqs for CFG

        sot = self.t3.hp.start_text_token
        eot = self.t3.hp.stop_text_token
        text_tokens = F.pad(text_tokens, (1, 0), value=sot)
        text_tokens = F.pad(text_tokens, (0, 1), value=eot)

        with torch.inference_mode():
            speech_tokens = self.t3.inference(
                t3_cond=self.conds.t3,
                text_tokens=text_tokens,
                max_new_tokens=1000,  # TODO: use the value in config
                temperature=temperature,
                cfg_weight=cfg_weight,
            )
            # Extract only the conditional batch.
            speech_tokens = speech_tokens[0]

            # TODO: output becomes 1D
            speech_tokens = drop_invalid_tokens(speech_tokens)
            speech_tokens = speech_tokens.to(self.device)

            wav, _ = self.s3gen.inference(
                speech_tokens=speech_tokens,
                ref_dict=self.conds.gen,
            )
            wav = wav.squeeze(0).detach().cpu().numpy()
            watermarked_wav = self.watermarker.apply_watermark(wav, sample_rate=self.sr)
        return torch.from_numpy(watermarked_wav).unsqueeze(0)

    # ────────────────────────────────────────────────────────────────────────
    # Streaming speech-token generator (EOS-aware, position-safe)
    # ────────────────────────────────────────────────────────────────────────
    def inference_stream(
        self,
        *,
        t3_cond: T3Cond,
        text_tokens: torch.Tensor,
        max_new_tokens: int = 1000,
        temperature: float = 0.8,
        cfg_weight: float = 0.5,
        chunk_size: int = 4,
    ) -> Generator[torch.Tensor, None, None]:
        """
        Yield newly generated speech tokens in (1, N) LongTensors.
        Terminates immediately after emitting the first EOS token.
        Guaranteed never to request a positional embedding beyond the model’s
        pre-computed range, avoiding padding-size errors.
        """
        from transformers.generation.logits_process import (
            TopPLogitsWarper,
            RepetitionPenaltyLogitsProcessor,
        )

        text_tokens = torch.atleast_2d(text_tokens).to(dtype=torch.long,
                                                       device=self.device)

        # BOS speech token
        bos_tok = torch.tensor([[self.t3.hp.start_speech_token]],
                               dtype=torch.long, device=self.device)

        # Conditional + text embeds
        embeds, _ = self.t3.prepare_input_embeds(
            t3_cond=t3_cond,
            text_tokens=text_tokens,
            speech_tokens=bos_tok,
        )
        if embeds.size(0) == 1:                        # duplicate for CFG
            embeds = torch.cat([embeds, embeds], dim=0)

        bos_emb = self.t3.speech_emb(bos_tok)
        bos_emb += self.t3.speech_pos_emb.get_fixed_embedding(0)
        bos_emb = torch.cat([bos_emb, bos_emb], dim=0)  # CFG dup

        inputs_embeds = torch.cat([embeds, bos_emb], dim=1)

        # Compile T3 ⇢ HF wrapper once
        if not self.t3.compiled:
            from .models.t3.inference.alignment_stream_analyzer import (
                AlignmentStreamAnalyzer,
            )
            from .models.t3.inference.t3_hf_backend import (
                T3HuggingfaceBackend,
            )

            ana = AlignmentStreamAnalyzer(
                self.t3.tfmr,
                None,
                text_tokens_slice=(embeds.size(1),
                                   embeds.size(1) + text_tokens.size(-1)),
                alignment_layer_idx=9,
                eos_idx=self.t3.hp.stop_speech_token,
            )
            self.t3.patched_model = T3HuggingfaceBackend(
                config=self.t3.cfg,
                llama=self.t3.tfmr,
                speech_enc=self.t3.speech_emb,
                speech_head=self.t3.speech_head,
                alignment_stream_analyzer=ana,
            )
            self.t3.compiled = True

        # Maximum position the pre-calculated table supports
        max_pos = getattr(self.t3.speech_pos_emb, "weight", None)
        max_pos = max_pos.size(0) - 1 if max_pos is not None else None

        generated = bos_tok.clone()                     # (1, 1)
        top_p     = TopPLogitsWarper(top_p=0.8)
        rep_pen   = RepetitionPenaltyLogitsProcessor(penalty=2.0)

        out  = self.t3.patched_model(inputs_embeds=inputs_embeds,
                                     use_cache=True,
                                     return_dict=True)
        past = out.past_key_values
        buf: list[torch.Tensor] = []

        for _ in range(max_new_tokens):
            # logits for conditional & unconditional batch
            logits = out.logits[:, -1, :]               # (2, vocab)
            logits = logits[0:1] + cfg_weight * (logits[0:1] - logits[1:2])
            logits = logits / temperature
            logits = rep_pen(generated, logits)
            logits = top_p(generated, logits)

            probs    = torch.softmax(logits, dim=-1)
            next_tok = torch.multinomial(probs, 1)      # (1, 1)

            generated = torch.cat([generated, next_tok], dim=1)
            buf.append(next_tok)

            eos = next_tok.item() == self.t3.hp.stop_speech_token
            if eos or len(buf) >= chunk_size:
                yield torch.cat(buf, dim=1)             # (1, N)
                buf = []
                if eos:                                 # ← stop right here
                    break

            # Positional embedding with safe index
            pos_idx = generated.size(1) - 1             # 0-based within stream
            if max_pos is not None and pos_idx > max_pos:
                pos_idx = max_pos                       # clamp

            pos_emb = self.t3.speech_pos_emb.get_fixed_embedding(pos_idx)
            tok_emb = self.t3.speech_emb(next_tok) + pos_emb
            tok_emb = torch.cat([tok_emb, tok_emb], dim=0)  # CFG dup

            out = self.t3.patched_model(inputs_embeds=tok_emb,
                                        past_key_values=past,
                                        use_cache=True,
                                        return_dict=True)
            past = out.past_key_values

        # Flush remainder (only if EOS never hit and buffer non-empty)
        if buf:
            yield torch.cat(buf, dim=1)




    # ────────────────────────────────────────────────────────────────────────────────
    # 2. Token → audio converter with exact bookkeeping + cross-fade support
    # ────────────────────────────────────────────────────────────────────────────────
    def _tokens_to_audio(
        self,
        new_tokens: torch.Tensor,
        *,
        fade_samples: int,
        token_sample_map: list[int],
    ) -> np.ndarray:
        """
        Convert *only* `new_tokens` (1-D LongTensor) to a NumPy waveform segment.
        Updates `token_sample_map` in-place so each entry equals cumulative samples
        after that token.
        """
        new_tokens = drop_invalid_tokens(new_tokens).to(self.device)
        if new_tokens.numel() == 0:
            return np.zeros(0, dtype=np.float32)

        wav, _ = self.s3gen.inference(speech_tokens=new_tokens,
                                    ref_dict=self.conds.gen)
        wav = wav.squeeze(0).detach().cpu().numpy()

        # per-token sample offsets
        samples_per = len(wav) / new_tokens.shape[-1]
        base = token_sample_map[-1] if token_sample_map else 0
        for _ in range(new_tokens.shape[-1]):
            base += int(round(samples_per))
            token_sample_map.append(base)

        # throw away initial overlap (already yielded previously)
        if len(token_sample_map) > new_tokens.shape[-1]:
            wav = wav[fade_samples:]

        return wav

    def generate_stream(
        self,
        text: str,
        audio_prompt_path: Optional[str] = None,
        exaggeration: float = 0.5,
        cfg_weight: float = 0.5,
        temperature: float = 0.8,
        chunk_size: int = 25,
        fade_ms: float = 1.0,
        print_metrics: bool = True,
    ) -> Generator[Tuple[torch.Tensor, StreamingMetrics], None, None]:
        """
        Stream audio chunks (shape = (1, n_samples)) together with live metrics.
        Terminates right after the first stop-speech token – no “extra batches”.
        """
        start_time = time.time()
        metrics = StreamingMetrics()

        # ── conditionals ──────────────────────────────────────────────────────
        if audio_prompt_path:
            self.prepare_conditionals(audio_prompt_path,
                                      exaggeration=exaggeration)
        elif self.conds is None:
            raise RuntimeError("prepare_conditionals first or pass audio_prompt_path")

        if exaggeration != float(self.conds.t3.emotion_adv[0, 0, 0]):
            c = self.conds.t3
            self.conds.t3 = T3Cond(
                speaker_emb=c.speaker_emb,
                cond_prompt_speech_tokens=c.cond_prompt_speech_tokens,
                emotion_adv=torch.ones(1, 1, 1, device=self.device) * exaggeration,
            )

        # ── text → tokens (CFG dup) ───────────────────────────────────────────
        text = punc_norm(text)
        txt = self.tokenizer.text_to_tokens(text).to(self.device)
        txt = torch.cat([txt, txt], dim=0)
        txt = F.pad(txt, (1, 0), value=self.t3.hp.start_text_token)
        txt = F.pad(txt, (0, 1), value=self.t3.hp.stop_text_token)

        # ── streaming vars ────────────────────────────────────────────────────
        fade_samples = int(round(fade_ms * 1e-3 * self.sr))
        token_sample_map: list[int] = []
        prev_tail = np.zeros(0, dtype=np.float32)
        total_audio_sec = 0.0
        stop_token = self.t3.hp.stop_speech_token

        # ── main loop ─────────────────────────────────────────────────────────
        with torch.inference_mode():
            for tok_chunk in self.inference_stream(
                t3_cond=self.conds.t3,
                text_tokens=txt,
                max_new_tokens=1000,
                temperature=temperature,
                cfg_weight=cfg_weight,
                chunk_size=chunk_size,
            ):
                tok_chunk = tok_chunk[0]                      # conditional batch

                # Strip EOS if present and remember we’re done
                eos_hit = (tok_chunk == stop_token).any()
                tok_chunk = tok_chunk[tok_chunk != stop_token]

                # Nothing but EOS? → leave the loop, but after flushing metrics
                if tok_chunk.numel() == 0:
                    break

                # Tokens → audio
                audio_seg = self._tokens_to_audio(
                    tok_chunk,
                    fade_samples=fade_samples,
                    token_sample_map=token_sample_map,
                )
                if audio_seg.size == 0:
                    break  # defensive – should not happen

                # ── cross-fade with previous tail ────────────────────────────
                if prev_tail.size:
                    overlap = min(fade_samples, len(prev_tail), len(audio_seg))
                    tail = prev_tail[-overlap:] * _linear_fade(overlap, False)
                    head =  audio_seg[:overlap] * _linear_fade(overlap, True)
                    prefix = prev_tail[:-overlap] if len(prev_tail) > overlap else np.empty(0, np.float32)
                    audio_seg = np.concatenate([prefix, tail + head, audio_seg[overlap:]])

                prev_tail = audio_seg[-fade_samples:].copy()

                # ── watermark & yield ───────────────────────────────────────
                chunk_tensor = torch.from_numpy(
                    self.watermarker.apply_watermark(audio_seg, sample_rate=self.sr)
                ).unsqueeze(0)

                if metrics.chunk_count == 0:
                    metrics.latency_to_first_chunk = time.time() - start_time
                    if print_metrics:
                        print(f"Latency to first chunk: {metrics.latency_to_first_chunk:.3f}s")

                metrics.chunk_count += 1
                total_audio_sec += len(audio_seg) / self.sr
                yield chunk_tensor, metrics

                if eos_hit:           # stop right after yielding the last audio
                    break

        # ── final stats ───────────────────────────────────────────────────────
        metrics.total_generation_time = time.time() - start_time
        metrics.total_audio_duration = total_audio_sec
        metrics.rtf = (metrics.total_generation_time / total_audio_sec) if total_audio_sec else None
        if print_metrics:
            print(f"Generated {total_audio_sec:.2f}s audio "
                  f"in {metrics.total_generation_time:.2f}s "
                  f"(RTF={metrics.rtf:.2f})  "
                  f"chunks={metrics.chunk_count}")


# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────
import numpy as np
import torch
import torch.nn.functional as F
from typing import Generator, Tuple, Optional

def _linear_fade(length: int, fade_in: bool = True) -> np.ndarray:
    """
    Return a 1-D linear fade curve of `length` samples.
    """
    ramp = np.linspace(0.0, 1.0, num=length, dtype=np.float32)
    return ramp if fade_in else 1.0 - ramp
