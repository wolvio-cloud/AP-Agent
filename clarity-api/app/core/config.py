from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "ClarityAP API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/clarityap"

    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Google Cloud
    GCS_BUCKET_NAME: str = "clarityap-invoices"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # Gemini AI
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
