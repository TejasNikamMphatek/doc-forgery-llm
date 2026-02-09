from google import genai
from google.genai import types
from config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def call_gemini_forensics(prompt: str, file_content: bytes, mime_type: str) -> str:
    document_part = types.Part.from_bytes(data=file_content, mime_type=mime_type)

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "visual_analysis": {
                "type": "OBJECT",
                "properties": {
                    "is_tampered": {"type": "BOOLEAN"},
                    "confidence_score": {"type": "INTEGER"},
                    "specific_artifacts": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "quality_check": {"type": "STRING"}
                },
                "required": ["is_tampered", "confidence_score", "specific_artifacts", "quality_check"]
            },
            "logical_analysis": {
                "type": "OBJECT",
                "properties": {
                    "has_contradictions": {"type": "BOOLEAN"},
                    "confidence_score": {"type": "INTEGER"},
                    "math_errors": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "date_issues": {"type": "ARRAY", "items": {"type": "STRING"}}
                },
                "required": ["has_contradictions", "confidence_score", "math_errors", "date_issues"]
            },
            "classification": {"type": "STRING"},
            "confidence": {"type": "INTEGER"},
            "summary": {"type": "STRING"},
            "reasoning": {"type": "STRING"}
        },
        "required": ["visual_analysis", "logical_analysis", "classification", "confidence", "summary"]
    }

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[document_part, prompt],
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=response_schema,
        )
    )
    return response.text