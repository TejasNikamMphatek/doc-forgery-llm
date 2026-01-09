from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_service import (
    extract_text_from_bytes, 
    convert_pdf_to_images, 
    get_image_bytes,
    extract_metadata  # Ensure you import your new metadata service
)
from app.services.prompt_service import build_forgery_prompt
from app.services.llm_service import call_llm_with_vision
from app.services.response_service import parse_llm_response

router = APIRouter()

@router.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    # 1. Read file bytes once to avoid pointer issues
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")

    # 2. Extract Metadata (Our new 1st layer of security)
    metadata = extract_metadata(content, file.content_type)

    image_bytes_for_llm = None
    
    # 3. Handle Branching Logic for PDF vs Image
    if file.content_type == "application/pdf":
        # Extract Text
        document_text = extract_text_from_bytes(content, "application/pdf")
        # Convert first page to image for Vision analysis
        pdf_pages = convert_pdf_to_images(content)
        if pdf_pages:
            image_bytes_for_llm = get_image_bytes(pdf_pages[0])
            
    elif file.content_type.startswith("image/"):
        # Extract Text (OCR)
        document_text = extract_text_from_bytes(content, file.content_type)
        # Use raw bytes directly
        image_bytes_for_llm = content
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # 4. Check if we have an image to send
    if not image_bytes_for_llm:
        raise HTTPException(status_code=500, detail="Could not process image for analysis")

    # 5. Build the forensic prompt (NOW PASSING METADATA)
    prompt = build_forgery_prompt(document_text, metadata)

    # 6. Call Vision LLM with prompt + image
    raw_llm_response = call_llm_with_vision(prompt, image_bytes_for_llm)

    # 7. Parse the structured JSON response
    result = parse_llm_response(raw_llm_response)

    return {
        "filename": file.filename,
        "metadata_raw": metadata, # Optional: return raw metadata for transparency
        "analysis": result
    }