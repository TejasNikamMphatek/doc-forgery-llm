import pdfplumber
import pytesseract
from PIL import Image
from io import BytesIO
from fastapi import UploadFile


def extract_text(file: UploadFile) -> str:
    """
    Entry point for extracting text from uploaded documents.
    Supports PDF and image files.
    """
    content = file.file.read()
    file.file.seek(0)

    if file.content_type == "application/pdf":
        return _extract_text_from_pdf(content)

    elif file.content_type.startswith("image/"):
        return _extract_text_from_image(content)

    else:
        return ""


def _extract_text_from_pdf(content: bytes) -> str:
    text = ""
    with pdfplumber.open(BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def _extract_text_from_image(content: bytes) -> str:
    image = Image.open(BytesIO(content))
    return pytesseract.image_to_string(image).strip()
