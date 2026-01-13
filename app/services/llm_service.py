import requests
import base64
from config import settings

def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')

def call_llm_with_vision(prompt: str, image_bytes: bytes) -> str:
    base64_image = encode_image(image_bytes)

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Standard Chat Completions Payload (Most Compatible)
    payload = {
        "model": "gpt-4o",  # Use the flagship gpt-4o for forensic IQ
        "messages": [
            {
                "role": "system",
                "content": "You are a professional forensic document examiner. Respond ONLY in JSON."
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
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"  # This forces the pixel-level analysis
                        }
                    }
                ]
            }
        ],
        "temperature": 0, # Remove randomness for forensics
        "response_format": { "type": "json_object" } # Forces JSON output at the model level
    }

    # Use the standard completions URL
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        # If this fails, the error message in your terminal will be very clear
        print(f"DEBUG ERROR: {response.text}")
        response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]