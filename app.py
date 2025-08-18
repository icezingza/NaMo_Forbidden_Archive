from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# โหลด secret key จาก .env
load_dotenv()

# import ฟังก์ชันจาก Core_Scripts
from Core_Scripts.emotion_parasite_engine import analyze_and_infect_emotions

app = FastAPI(title="NaMo Forbidden Core API", version="1.0.0")

class EmotionInput(BaseModel):
    emotions: str

@app.get("/")
def root():
    return {"message": "🖤 NaMo Forbidden API is running 🌑"}

@app.post("/infect")
def infect_emotions(data: EmotionInput):
    result = analyze_and_infect_emotions(data.emotions)
    return {"infected": result}

@app.get("/omega")
def omega_mode():
    return {"message": "🔥 !omega mode activated"}