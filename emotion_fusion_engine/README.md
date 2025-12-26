# Emotion Fusion Engine

Flask-based multimodal emotion analysis API with a Hertz-style oscillation layer.

## Quick start

Install optional dependencies:

```
pip install -r requirements-emotion.txt
```

Run the service:

```
python -m emotion_fusion_engine.app
```

## API

`POST /analyze/text`

```
{
  "text": "Hello",
  "history": ["neutral", "happy"]
}
```

`POST /analyze/image`

Multipart form-data with `file` and optional `history` (comma-separated or JSON list).

`POST /analyze/audio`

Multipart form-data with `file` and optional `history` (comma-separated or JSON list).

## Notes

- Text analysis uses transformers if installed; otherwise a simple rule-based fallback.
- Image and audio analysis use DeepFace and SpeechBrain when available; otherwise fallback output.
