from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.analyze import router as analyze_router
from config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Forensic Analysis API for Document and Image Forgery Detection",
    version="1.1.0"
)

# Add CORS so a web browser can call your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api", tags=["Forensics"])

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "active",
        "engine": "GPT-4o-Mini-Vision",
        "service": settings.APP_NAME
    }