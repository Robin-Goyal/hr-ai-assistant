from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.api import api_router
from .core.config import settings
from .db.database import engine
from .models import models
from .core.seed_data import seed_data

# Create database tables
try:
    models.Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    
    # Seed the database with initial data if needed
    seed_data()
except Exception as e:
    print(f"Error creating database tables: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    """
    Root endpoint.
    """
    return {
        "message": "Welcome to the HR Assistant API",
        "docs": f"{settings.API_V1_STR}/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 