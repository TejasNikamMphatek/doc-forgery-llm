import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "Document Forgery Detection (LLM)"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4o-mini"
    TEMPERATURE = 0.2

settings = Settings()
