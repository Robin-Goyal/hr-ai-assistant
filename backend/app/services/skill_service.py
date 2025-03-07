from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.models import Skill
from ..models.schemas import SkillCreate, SkillUpdate

def create_skill(db: Session, skill_data: SkillCreate) -> Skill:
    """Create a new skill."""
    # Check if skill with same name already exists
    existing_skill = db.query(Skill).filter(
        Skill.name == skill_data.name
    ).first()
    
    if existing_skill:
        raise HTTPException(
            status_code=400, 
            detail=f"Skill '{skill_data.name}' already exists"
        )
    
    # Create the skill
    db_skill = Skill(
        name=skill_data.name,
        category=skill_data.category
    )
    
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    
    return db_skill

def get_skill(db: Session, skill_id: int) -> Optional[Skill]:
    """Get a skill by ID."""
    return db.query(Skill).filter(Skill.id == skill_id).first()

def get_skills(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None
) -> List[Skill]:
    """Get all skills, optionally filtered by category."""
    query = db.query(Skill)
    
    if category:
        query = query.filter(Skill.category == category)
    
    return query.offset(skip).limit(limit).all()

def update_skill(db: Session, skill_id: int, skill_data: SkillUpdate) -> Optional[Skill]:
    """Update a skill's information."""
    db_skill = get_skill(db, skill_id)
    
    if not db_skill:
        return None
    
    # Check for name conflict if name is being changed
    update_data = skill_data.dict(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_skill.name:
        existing_skill = db.query(Skill).filter(
            Skill.name == update_data["name"]
        ).first()
        
        if existing_skill:
            raise HTTPException(
                status_code=400, 
                detail=f"Skill '{update_data['name']}' already exists"
            )
    
    # Update fields
    for key, value in update_data.items():
        setattr(db_skill, key, value)
    
    db.commit()
    db.refresh(db_skill)
    
    return db_skill

def delete_skill(db: Session, skill_id: int) -> bool:
    """Delete a skill."""
    db_skill = get_skill(db, skill_id)
    
    if not db_skill:
        return False
    
    # Check if skill is associated with any candidates
    if db_skill.candidates and len(db_skill.candidates) > 0:
        # Option 1: Prevent deletion
        raise HTTPException(
            status_code=400,
            detail="Cannot delete skill that is associated with candidates"
        )
        
        # Option 2: Remove associations and then delete
        # for candidate in db_skill.candidates:
        #     candidate.skills.remove(db_skill)
    
    db.delete(db_skill)
    db.commit()
    
    return True

def get_skills_by_names(db: Session, skill_names: List[str]) -> List[Skill]:
    """Get skills by their names."""
    return db.query(Skill).filter(Skill.name.in_(skill_names)).all()

def get_or_create_skills(db: Session, skill_names: List[str]) -> List[Skill]:
    """Get or create skills by their names."""
    result = []
    
    for name in skill_names:
        # Check if skill exists
        skill = db.query(Skill).filter(Skill.name == name).first()
        
        if not skill:
            # Create new skill
            skill = Skill(name=name, category="Other")
            db.add(skill)
            db.commit()
            db.refresh(skill)
        
        result.append(skill)
    
    return result 