import json
import re
from pydantic import BaseModel, Field, ValidationError
from typing import List

class ForgeryAnalysis(BaseModel):
    # These MUST match the keys in your prompt exactly
    classification: str
    confidence: int
    visual_evidence: List[str]
    logical_evidence: List[str]
    summary: str

def parse_llm_response(raw_response: str) -> dict:
    try:
        # 1. Strip Markdown and find the first '{' and last '}'
        # This is safer than just replacing "```json"
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in response")
            
        cleaned_json = match.group(0)
        data = json.loads(cleaned_json)

        # 2. Validate with Pydantic
        validated_data = ForgeryAnalysis(**data)
        return validated_data.model_dump()

    except Exception as exc:
        # If parsing fails, we return a detailed error so you know WHY it failed
        return {
            "classification": "ERROR",
            "confidence": 0,
            "visual_evidence": ["System Parsing Error"],
            "logical_evidence": [f"Technical Details: {str(exc)}"],
            "summary": "The AI response could not be processed. Please check logs."
        }