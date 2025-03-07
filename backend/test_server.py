from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import List, Dict, Any, Optional
import uvicorn

app = FastAPI(
    title="HR Assistant API Test",
    description="A test server for the HR Assistant frontend",
    version="0.1.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def root():
    """
    Root endpoint.
    """
    return {
        "message": "Welcome to the HR Assistant API Test Server",
        "docs": "/docs",
    }

@app.post("/api/v1/auth/login")
def login(username: str, password: str):
    """
    Login endpoint.
    """
    return {
        "access_token": "dummy_token",
        "token_type": "bearer",
    }

@app.get("/api/v1/candidates")
def get_candidates(token: str = Depends(oauth2_scheme)):
    """
    Get candidates endpoint.
    """
    return {
        "items": [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "status": "new",
                "skills": [
                    {"id": 1, "name": "Python", "category": "Programming"},
                    {"id": 2, "name": "React", "category": "Frontend"},
                ]
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "987-654-3210",
                "status": "interview",
                "skills": [
                    {"id": 3, "name": "JavaScript", "category": "Programming"},
                    {"id": 4, "name": "Node.js", "category": "Backend"},
                ]
            }
        ],
        "total": 2
    }

@app.get("/api/v1/positions")
def get_positions(token: str = Depends(oauth2_scheme)):
    """
    Get positions endpoint.
    """
    return {
        "items": [
            {
                "id": 1,
                "title": "Software Engineer",
                "department_id": 1,
                "department_name": "Engineering",
                "location": "San Francisco, CA",
                "salary_range": "$100,000 - $150,000",
                "status": True,
            },
            {
                "id": 2,
                "title": "Product Manager",
                "department_id": 2,
                "department_name": "Product",
                "location": "New York, NY",
                "salary_range": "$120,000 - $180,000",
                "status": True,
            }
        ],
        "total": 2
    }

@app.get("/api/v1/departments")
def get_departments(token: str = Depends(oauth2_scheme)):
    """
    Get departments endpoint.
    """
    return {
        "items": [
            {
                "id": 1,
                "name": "Engineering",
                "description": "Software development and engineering",
            },
            {
                "id": 2,
                "name": "Product",
                "description": "Product management and design",
            }
        ],
        "total": 2
    }

@app.get("/api/v1/documents")
def get_documents(token: str = Depends(oauth2_scheme)):
    """
    Get documents endpoint.
    """
    return [
        {
            "id": 1,
            "title": "Employee Handbook",
            "category": "HR",
            "created_at": "2023-01-01T00:00:00Z",
            "offline_available": True,
            "file_path": "/documents/employee_handbook.pdf",
        },
        {
            "id": 2,
            "title": "Onboarding Guide",
            "category": "HR",
            "created_at": "2023-02-01T00:00:00Z",
            "offline_available": False,
            "file_path": "/documents/onboarding_guide.pdf",
        }
    ]

@app.post("/api/v1/ai/chat")
def chat(message: str, conversation_id: Optional[str] = None):
    """
    Chat endpoint.
    """
    return {
        "message": f"You said: {message}. This is a test response from the server.",
        "conversation_id": conversation_id or "new_conversation_id",
    }

@app.post("/api/v1/ai/questions")
def generate_questions(position_id: int, difficulty: str, count: int, categories: List[str]):
    """
    Generate questions endpoint.
    """
    return {
        "questions": [
            {
                "id": 1,
                "content": "What is your experience with Python?",
                "difficulty": difficulty,
                "category": categories[0] if categories else "Technical",
            },
            {
                "id": 2,
                "content": "How do you handle tight deadlines?",
                "difficulty": difficulty,
                "category": categories[0] if categories else "Behavioral",
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 