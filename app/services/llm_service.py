import requests
from config import settings


OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def call_llm(prompt: str) -> str:
    """
    Sends prompt to ChatGPT and returns raw response text.
    """

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a document fraud analysis engine."},
            {"role": "user", "content": prompt}
        ],
        "temperature": settings.TEMPERATURE
    }

    response = requests.post(
        OPENAI_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]
