from fastapi import FastAPI
from app.routes.analyze import router as analyze_router
from config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(analyze_router, prefix="/api")

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME
    }
