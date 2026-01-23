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
    
    # Process images (Limit to first 3 pages to save tokens if it's a large PDF)
    for img_bytes in image_list[:3]:
        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        content_payload.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "high"
            }
        })

    # UPDATED SCHEMA to match the new 2-step Logic
    json_schema = {
        "name": "forgery_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "visual_analysis": {
                    "type": "object",
                    "properties": {
                        "is_tampered": {"type": "boolean"},
                        "confidence_score": {"type": "integer"},
                        "specific_artifacts": {"type": "array", "items": {"type": "string"}},
                        "quality_check": {"type": "string", "description": "Describe image quality (e.g. Blurry, HD, Grainy)"}
                    },
                    "required": ["is_tampered", "confidence_score", "specific_artifacts", "quality_check"],
                    "additionalProperties": False
                },
                "logical_analysis": {
                    "type": "object",
                    "properties": {
                        "has_contradictions": {"type": "boolean"},
                        "confidence_score": {"type": "integer"},
                        "math_errors": {"type": "array", "items": {"type": "string"}},
                        "date_issues": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["has_contradictions", "confidence_score", "math_errors", "date_issues"],
                    "additionalProperties": False
                },
                "final_classification": {"type": "string", "enum": ["ORIGINAL", "SUSPICIOUS", "FORGED"]},
                "final_confidence": {"type": "integer"},
                "summary": {"type": "string"}
            },
            "required": ["visual_analysis", "logical_analysis", "final_classification", "final_confidence", "summary"],
            "additionalProperties": False
        }
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a forensic document expert."},
            {"role": "user", "content": content_payload}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": json_schema
        },
        "temperature": 0.1  # Low temperature for strict analysis
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