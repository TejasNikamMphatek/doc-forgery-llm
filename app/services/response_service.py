from pydantic import BaseModel
from typing import List, Optional
import json
import re

class VisualAnalysis(BaseModel):
    is_tampered: bool
    confidence_score: int
    specific_artifacts: List[str]  # e.g. ["Mismatched fonts", "Digital smear"]
    quality_check: str  # e.g. "Low resolution - Grain is consistent"

class LogicalAnalysis(BaseModel):
    has_contradictions: bool
    confidence_score: int
    math_errors: List[str]
    date_issues: List[str]

class ForgeryAnalysis(BaseModel):
    visual_analysis: VisualAnalysis
    logical_analysis: LogicalAnalysis
    final_classification: str  # "ORIGINAL" | "SUSPICIOUS" | "FORGED"
    final_confidence: int
    summary: str

    def verify_confidence(self, threshold: int = 90):
        """
        Applies the strict 'Low Quality != Forgery' rule.
        """
        # RULE: If the image is low quality but NO hard logical/visual evidence exists, force ORIGINAL
        is_low_quality = "low" in self.visual_analysis.quality_check.lower()
        has_hard_evidence = (
            self.logical_analysis.has_contradictions or 
            (self.visual_analysis.is_tampered and self.visual_analysis.confidence_score > threshold)
        )

        if is_low_quality and not has_hard_evidence:
            self.final_classification = "ORIGINAL"
            self.summary = "Image quality is low, but no digital manipulation or logical errors were found."
            self.final_confidence = 100
            
        return self

def parse_llm_response(raw_response: str) -> ForgeryAnalysis:
    try:
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if not match:
            raise ValueError("No JSON found")
        data = json.loads(match.group(0))
        return ForgeryAnalysis(**data)
    except Exception as e:
        # Return a safe error object
        return ForgeryAnalysis(
            visual_analysis=VisualAnalysis(is_tampered=False, confidence_score=0, specific_artifacts=[], quality_check="Error"),
            logical_analysis=LogicalAnalysis(has_contradictions=False, confidence_score=0, math_errors=[], date_issues=[]),
            final_classification="ERROR",
            final_confidence=0,
            summary=f"Parsing Error: {str(e)}"
        )
    
def enforce_phase_discipline(result: ForgeryAnalysis) -> ForgeryAnalysis:
    """
    Enforces forensic discipline:
    - FORGED is not allowed without confirmed visual tampering
    - Logical-only issues cannot escalate to FORGED
    """
    has_visual_tampering = (
        result.visual_analysis.is_tampered and
        result.visual_analysis.confidence_score >= 85
    )

    has_logical_only = (
        result.logical_analysis.has_contradictions and
        not has_visual_tampering
    )

    # Illegal FORGED → downgrade
    if result.final_classification == "FORGED" and not has_visual_tampering:
        result.final_classification = "SUSPICIOUS"
        result.final_confidence = min(result.final_confidence, 70)
        result.summary += (
            " Final decision downgraded: no confirmed visual tampering detected."
        )

    # Logical-only issues → SUSPICIOUS
    if has_logical_only:
        result.final_classification = "SUSPICIOUS"
        result.final_confidence = min(result.final_confidence, 75)

    return result
