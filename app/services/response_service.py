import json
import re
from pydantic import BaseModel, Field, ValidationError
from typing import List

# This class defines exactly what a "Forgery Result" looks like
class ForgeryAnalysis(BaseModel):
    classification: str = Field(description="ORIGINAL, SUSPICIOUS, or FORGED")
    confidence: int = Field(ge=0, le=100)
    visual_evidence: List[str] = Field(default_factory=list)
    logical_evidence: List[str] = Field(default_factory=list)
    summary: str

def parse_llm_response(raw_response: str) -> dict:
    try:
        # 1. Clean markdown artifacts
        cleaned = re.sub(r"```json|```", "", raw_response).strip()
        data = json.loads(cleaned)

        # 2. Use Pydantic to validate the data shape
        validated_data = ForgeryAnalysis(**data)
        return validated_data.model_dump()

    except (ValidationError, json.JSONDecodeError) as exc:
        return {
            "classification": "SUSPICIOUS",
            "confidence": 0,
            "visual_evidence": ["Parsing Error"],
            "logical_evidence": [str(exc)],
            "summary": "The AI response was malformed. Please try again."
        }