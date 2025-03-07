import os
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import dotenv for loading environment variables
from dotenv import load_dotenv

from pydantic import AnyHttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings

# Load .env file
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "HR Assistant API"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",  # Vite default port
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "HR Assistant"
    DESCRIPTION: str = "HR Assistant API for managing candidates, positions, and applications"
    VERSION: str = "0.1.0"
    
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    SQLITE_DATABASE_URI: Optional[str] = "sqlite:///./hr_assistant.db"
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if v:
            return v
        # Use SQLite by default
        return values.get("SQLITE_DATABASE_URI")

    class Config:
        case_sensitive = True
        env_file = "../.env"
        env_file_encoding = "utf-8"


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Directory for storing uploaded resumes
RESUME_DIR = BASE_DIR / "uploads" / "resumes"

# Ensure the upload directories exist
RESUME_DIR.mkdir(parents=True, exist_ok=True)

# Create settings
settings = Settings()

# Export settings
__all__ = ["settings", "BASE_DIR", "RESUME_DIR"]

# File Storage
UPLOAD_DIR = Path("./uploads")
DOCUMENT_DIR = UPLOAD_DIR / "documents"

# Ensure directories exist
DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)

# AI Service - read from environment with dotenv loaded
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
INDEX_NAME = os.getenv("INDEX_NAME", "hr-assistant")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2") 