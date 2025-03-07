from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

from ..core.config import settings

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hr_assistant.db")

# Create database engine
engine = create_engine(
    DATABASE_URL,
    # echo=True,  # Uncomment for SQL logging
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency for getting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 