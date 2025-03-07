from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import User
from ...models.schemas import Skill, SkillCreate, SkillUpdate
from ...services.auth_service import get_current_active_user
from ...services.skill_service import (
    create_skill, get_skill, get_skills,
    update_skill, delete_skill, get_skills_by_names
)

router = APIRouter()

@router.get("/", response_model=List[Skill])
def read_skills(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve skills, optionally filtered by category.
    """
    return get_skills(db, skip=skip, limit=limit, category=category)

@router.post("/", response_model=Skill)
def create_new_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new skill.
    """
    return create_skill(db, skill_data)

@router.get("/{skill_id}", response_model=Skill)
def read_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get skill by ID.
    """
    skill = get_skill(db, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@router.put("/{skill_id}", response_model=Skill)
def update_skill_data(
    skill_id: int,
    skill_data: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a skill.
    """
    skill = get_skill(db, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    updated_skill = update_skill(db, skill_id, skill_data)
    if not updated_skill:
        raise HTTPException(status_code=400, detail="Failed to update skill")
    
    return updated_skill

@router.delete("/{skill_id}", response_model=Skill)
def delete_skill_data(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a skill.
    """
    skill = get_skill(db, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    try:
        if delete_skill(db, skill_id):
            return skill
        raise HTTPException(status_code=400, detail="Failed to delete skill")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/search", response_model=List[Skill])
def search_skills_by_names(
    skill_names: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Search for skills by their names.
    """
    return get_skills_by_names(db, skill_names) 