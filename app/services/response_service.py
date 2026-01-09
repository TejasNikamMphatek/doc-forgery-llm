import json
import re


def parse_llm_response(raw_response: str) -> dict:
    """
    Parses and validates the LLM JSON response safely.
    """

    try:
        # Remove markdown formatting if present
        cleaned = re.sub(r"```json|```", "", raw_response).strip()

        data = json.loads(cleaned)

        # Basic validation
        required_keys = {"classification", "confidence", "reasons", "summary"}
        if not required_keys.issubset(data.keys()):
            raise ValueError("Missing required keys in LLM response")

        return data

    except Exception as exc:
        return {
            "classification": "SUSPICIOUS",
            "confidence": 50,
            "reasons": ["LLM response could not be parsed reliably"],
            "summary": f"Fallback response due to parsing error: {str(exc)}"
        }
