from __future__ import annotations

import json
from typing import List

from flask import Flask, jsonify, request

from emotion_fusion_engine.analyzers.audio_analyzer import AudioEmotionAnalyzer
from emotion_fusion_engine.analyzers.image_analyzer import ImageEmotionAnalyzer
from emotion_fusion_engine.analyzers.text_analyzer import TextEmotionAnalyzer
from emotion_fusion_engine.emotion_oscillation_calculator import (
    EmotionOscillationCalculator,
)


app = Flask(__name__)

text_analyzer = TextEmotionAnalyzer()
image_analyzer = ImageEmotionAnalyzer()
audio_analyzer = AudioEmotionAnalyzer()


def _parse_history(value: str | None) -> List[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except json.JSONDecodeError:
        pass
    return [item.strip() for item in value.split(",") if item.strip()]


def _make_response(label: str, confidence: float, history: List[str], engine: str):
    metrics = EmotionOscillationCalculator.calculate_oscillation(label, confidence, history)
    return {
        "emotion": {
            "label": label,
            "confidence": confidence,
            "engine": engine,
        },
        "oscillation": metrics,
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/analyze/text")
def analyze_text():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    history = payload.get("history", [])
    if isinstance(history, str):
        history = _parse_history(history)
    result = text_analyzer.analyze(text)
    response = _make_response(
        result["label"], float(result["confidence"]), history, result["engine"]
    )
    return jsonify(response)


@app.post("/analyze/image")
def analyze_image():
    file = request.files.get("file")
    history = _parse_history(request.form.get("history"))
    if not file:
        return jsonify({"error": "file is required"}), 400
    result = image_analyzer.analyze(file.read())
    response = _make_response(
        result["label"], float(result["confidence"]), history, result["engine"]
    )
    return jsonify(response)


@app.post("/analyze/audio")
def analyze_audio():
    file = request.files.get("file")
    history = _parse_history(request.form.get("history"))
    if not file:
        return jsonify({"error": "file is required"}), 400
    result = audio_analyzer.analyze(file.read())
    response = _make_response(
        result["label"], float(result["confidence"]), history, result["engine"]
    )
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
