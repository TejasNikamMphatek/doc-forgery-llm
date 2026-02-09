import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "Document Forgery Detection (LLM)"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    #OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash"
    #OPENAI_MODEL = "gpt-4.1"
    #REASONING_EFFORT = "high"
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

settings = Settings()
