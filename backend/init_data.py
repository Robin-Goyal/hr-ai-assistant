#!/usr/bin/env python3
"""
Script to initialize the database with seed data
"""
import logging
from app.db.database import SessionLocal
from app.db.init_db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()
    try:
        init_db(db)
        logger.info("Initial data created")
    finally:
        db.close()

if __name__ == "__main__":
    main() 