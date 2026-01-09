import requests
import base64
from config import settings

OPENAI_URL = "https://api.openai.com/v1/chat/completions"

def encode_image(image_bytes: bytes) -> str:
    """
    Encodes raw image bytes into a base64 string.
    """
    return base64.b64encode(image_bytes).decode('utf-8')

def call_llm_with_vision(prompt: str, image_bytes: bytes) -> str:
    """
    Sends a combined text and image prompt to GPT-4o-mini.
    """
    base64_image = encode_image(image_bytes)

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # The Vision API uses a specific content list structure
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "You are a professional forensic document examiner."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": settings.TEMPERATURE,
        "max_tokens": 1000
    }

    response = requests.post(
        OPENAI_URL,
        headers=headers,
        json=payload,
        timeout=60 # Vision requests can take longer to process
    )

    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]