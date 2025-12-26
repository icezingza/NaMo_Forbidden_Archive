from __future__ import annotations

from typing import Dict


class AudioEmotionAnalyzer:
    """Analyze audio emotion using SpeechBrain if available."""

    def __init__(self) -> None:
        self._speechbrain = None

    def _ensure_backend(self) -> None:
        if self._speechbrain is not None:
            return
        try:
            from speechbrain.pretrained import EncoderClassifier  # type: ignore
        except Exception:
            self._speechbrain = False
            return
        self._speechbrain = EncoderClassifier.from_hparams(
            source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
            savedir="pretrained_models/emotion-recognition",
        )

    def analyze(self, audio_bytes: bytes) -> Dict[str, object]:
        """Return label and confidence for the most likely emotion."""
        if not audio_bytes:
            return {"label": "neutral", "confidence": 0.2, "engine": "fallback"}

        self._ensure_backend()
        if self._speechbrain and self._speechbrain is not False:
            try:
                import torch
            except Exception:
                return {"label": "neutral", "confidence": 0.2, "engine": "fallback"}
            import io
            import torchaudio

            waveform, sample_rate = torchaudio.load(io.BytesIO(audio_bytes))
            if sample_rate != 16000:
                waveform = torchaudio.functional.resample(waveform, sample_rate, 16000)
            predictions = self._speechbrain.classify_batch(waveform)
            scores = predictions[1].softmax(dim=-1)
            score, index = torch.max(scores, dim=-1)
            label = predictions[3][index.item()]
            return {"label": str(label).lower(), "confidence": float(score), "engine": "speechbrain"}

        return {"label": "neutral", "confidence": 0.3, "engine": "fallback"}
