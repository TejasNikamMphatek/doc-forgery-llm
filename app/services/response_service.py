import json
import re
from pydantic import BaseModel
from typing import List

class ForgeryAnalysis(BaseModel):
    classification: str
    confidence: int
    visual_evidence: List[str]
    logical_evidence: List[str]
    summary: str
    def verify_confidence(self, threshold: int = 90):
        """
        Stricter verification to protect original documents.
        """
        # If it's a "Hunch" (low confidence) with no Logical/Math error, it's likely a False Positive.
        if self.classification in ["SUSPICIOUS", "FORGED"]:
            
            # 1. Hard Logic: If there is a math error or software metadata, keep it as FORGED.
            has_hard_proof = len(self.logical_evidence) > 0 or "software" in str(self.visual_evidence).lower()
            
            if has_hard_proof:
                return self
            
            # 2. Threshold: If confidence is below 90% and there's no hard proof, mark as Original.
            if self.confidence < threshold:
                self.classification = "ORIGINAL"
                self.summary = f"AI Analysis (Confidence {self.confidence}%) suggested anomalies, but they did not meet the forensic threshold for forgery."
        
        return self
   
def parse_llm_response(raw_response: str) -> ForgeryAnalysis:
    """
    Parses the raw LLM string into a ForgeryAnalysis object.
    """
    try:
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in response")
            
        data = json.loads(match.group(0))

        # Flatten nested 'analysis' keys if present
        if "analysis" in data and isinstance(data["analysis"], dict):
            data = data["analysis"]
            
        # Standardize field names
        field_mapping = {
            "visual_forensic_evidence": "visual_evidence",
            "logical_audit_evidence": "logical_evidence"
        }
        for old_key, new_key in field_mapping.items():
            if old_key in data and new_key not in data:
                data[new_key] = data[old_key]

        # Returns the actual class instance
        return ForgeryAnalysis(**data)

    except Exception as exc:
        print(f"PARSING ERROR: {str(exc)}")
        return ForgeryAnalysis(
            classification="ERROR",
            confidence=0,
            visual_evidence=["Parsing Error"],
            logical_evidence=[f"Details: {str(exc)}"],
            summary="The system failed to parse the AI response format."
        )