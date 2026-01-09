from fastapi import APIRouter, UploadFile, File
from app.services.file_service import extract_text
from app.services.prompt_service import build_forgery_prompt
from app.services.llm_service import call_llm
from app.services.response_service import parse_llm_response

router = APIRouter()

@router.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    document_text = extract_text(file)

    prompt = build_forgery_prompt(document_text)

    raw_llm_response = call_llm(prompt)

    result = parse_llm_response(raw_llm_response)

    return {
        "filename": file.filename,
        "analysis": result
    }
