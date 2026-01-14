import requests
import base64
import json
from config import settings

def call_llm_with_vision(prompt: str, image_list: list) -> str:
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    content_payload = [{"type": "text", "text": prompt}]

    for img_bytes in image_list:
        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        content_payload.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "high"
            }
        })

    # This schema MUST match your Pydantic ForgeryAnalysis model exactly
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a professional forensic document examiner."},
            {"role": "user", "content": content_payload}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "forgery_detection",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "classification": {"type": "string", "enum": ["ORIGINAL", "SUSPICIOUS", "FORGED"]},
                        "confidence": {"type": "integer"},
                        "visual_evidence": {"type": "array", "items": {"type": "string"}},
                        "logical_evidence": {"type": "array", "items": {"type": "string"}},
                        "summary": {"type": "string"}
                    },
                    "required": ["classification", "confidence", "visual_evidence", "logical_evidence", "summary"],
                    "additionalProperties": False
                }
            }
        },
        "temperature": 0
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=180
    )

    if response.status_code != 200:
        raise Exception(f"API Error: {response.text}")

    return response.json()["choices"][0]["message"]["content"]