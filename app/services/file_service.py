import pdfplumber
import pytesseract
from PIL import Image
from io import BytesIO
from pdf2image import convert_from_bytes
import fitz  # PyMuPDF
from PIL import Image, ExifTags
from io import BytesIO


def extract_text_from_bytes(content: bytes, content_type: str) -> str:
    """
    Takes raw bytes directly so we don't have to worry about FastAPI file pointers.
    """
    if content_type == "application/pdf":
        text = ""
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()

    elif content_type.startswith("image/"):
        image = Image.open(BytesIO(content))
        return pytesseract.image_to_string(image).strip()
    
    return ""

def convert_pdf_to_images(pdf_content: bytes):
    """
    Converts PDF pages into a list of PIL Image objects.
    """
    # 300 DPI is standard for forensic-level detail
    return convert_from_bytes(pdf_content, dpi=300)

def get_image_bytes(image: Image.Image) -> bytes:
    """
    Converts a PIL Image object back into JPEG bytes.
    """
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=95)
    return buf.getvalue()



def extract_metadata(content: bytes, content_type: str) -> dict:
    """
    Extracts hidden metadata tags from PDFs and Images.
    """
    meta_info = {}

    if content_type == "application/pdf":
        with fitz.open(stream=content, filetype="pdf") as doc:
            meta_info = doc.metadata  # Returns dict with author, creator, producer, etc.
            
    elif content_type.startswith("image/"):
        image = Image.open(BytesIO(content))
        exif_data = image.getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                meta_info[tag] = str(value)
                
    return meta_info