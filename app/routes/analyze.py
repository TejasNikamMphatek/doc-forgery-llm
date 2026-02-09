from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_service import (
    extract_text_from_bytes, 
    extract_metadata
)
from app.services.prompt_service import build_forgery_prompt
from app.services.llm_service import call_gemini_forensics
# Note: We now import the modified enforce_phase_discipline
from app.services.response_service import parse_llm_response, enforce_phase_discipline

router = APIRouter()

@router.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")

    # 1. Gather Metadata and OCR text
    metadata = extract_metadata(content, file.content_type)
    document_text = extract_text_from_bytes(content, file.content_type)

    # 2. Build the forensic prompt with Temporal Sync rules
    prompt = build_forgery_prompt(document_text, metadata)

    try:
        # 3. Call Gemini (Native bytes for visual/logical analysis)
        raw_llm_response = call_gemini_forensics(prompt, content, file.content_type)
        
        # 4. Parse JSON
        analysis_obj = parse_llm_response(raw_llm_response)
        
        # 5. NEW: Apply Forensic Discipline with "Hard-Stop" Text Override
        # We pass document_text to catch the April/Mei trap manually
        analysis_obj = enforce_phase_discipline(analysis_obj, document_text)
        
        # 6. Final confidence verification
        analysis_obj = analysis_obj.verify_confidence(threshold=90)
        
        final_result = analysis_obj.model_dump()

        return {
            "filename": file.filename,
            "document_type": final_result.get("document_type", "Unknown"),
            "analysis": final_result 
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")