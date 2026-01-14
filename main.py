import os
import requests
from fastapi import FastAPI

app = FastAPI()

HF_API_KEY = os.getenv("HF_API_KEY")

HF_MODEL_URL = (
    "https://api-inference.huggingface.co/models/"
    "mrm8488/bert-tiny-finetuned-sms-spam-detection"
)

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

@app.post("/detect_sms")
def detect_sms(message: str):
    payload = {"inputs": message}

    response = requests.post(
        HF_MODEL_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    result = response.json()

    scores = {
        item["label"]: item["score"]
        for item in result[0]
    }

    spam_score = scores.get("spam", 0)

    return {
        "message": message,
        "spam_probability": round(spam_score * 100, 2),
        "status": "BLOCKED" if spam_score > 0.6 else "SAFE"
    }
