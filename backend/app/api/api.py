from fastapi import APIRouter

from .endpoints import candidates, departments, positions, skills, applications, notes, users, auth, documents, ai

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(positions.router, prefix="/positions", tags=["positions"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(skills.router, prefix="/skills", tags=["skills"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"]) 