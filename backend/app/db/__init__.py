from .database import Base, engine, SessionLocal, get_db

# Initialize database tables
Base.metadata.create_all(bind=engine)
