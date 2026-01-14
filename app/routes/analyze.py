from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_service import (
    extract_text_from_bytes, 
    convert_pdf_to_images, 
    get_image_bytes,
    extract_metadata
)
from app.services.prompt_service import build_forgery_prompt
from app.services.llm_service import call_llm_with_vision
from app.services.response_service import parse_llm_response, ForgeryAnalysis

router = APIRouter()

@router.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")

    metadata = extract_metadata(content, file.content_type)
    image_list_for_llm = []
    document_text = ""

    # Process PDF vs Image
    if file.content_type == "application/pdf":
        document_text = extract_text_from_bytes(content, "application/pdf")
        pdf_pages = convert_pdf_to_images(content)
        for page in pdf_pages[:10]: 
            image_list_for_llm.append(get_image_bytes(page))
            
    elif file.content_type.startswith("image/"):
        document_text = extract_text_from_bytes(content, file.content_type)
        image_list_for_llm.append(content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if not image_list_for_llm:
        raise HTTPException(status_code=500, detail="Could not process images for analysis")

    # 1. Build universal forensic prompt
    prompt = build_forgery_prompt(document_text, metadata)

    # 2. Call Multi-Vision LLM
    raw_llm_response = call_llm_with_vision(prompt, image_list_for_llm)
    
    # 3. Parse directly into the Pydantic Object (Corrected line)
    analysis_obj = parse_llm_response(raw_llm_response)
    
    # 4. Apply the Confidence Threshold
    final_result = analysis_obj.verify_confidence(threshold=85).model_dump()

    return {
        "filename": file.filename,
        "page_count": len(image_list_for_llm),
        "analysis": final_result 
    }