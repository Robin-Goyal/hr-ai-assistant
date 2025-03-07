import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session, joinedload
import sqlalchemy

from ..models.models import Candidate, Skill, Position
from ..models.schemas import CandidateCreate
from ..core.config import RESUME_DIR

async def save_resume_file(file: UploadFile, destination: Path) -> Path:
    """Save an uploaded resume file to the specified destination."""
    destination_path = destination / file.filename
    
    # Ensure the destination directory exists
    destination.mkdir(parents=True, exist_ok=True)
    
    # Save the file
    with open(destination_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return destination_path

async def create_candidate(
    db: Session, 
    candidate_data: CandidateCreate,
    resume_file: Optional[UploadFile] = None
) -> Candidate:
    """Create a new candidate record and save the uploaded resume if provided."""
    # Check if candidate with email already exists
    existing_candidate = db.query(Candidate).filter(Candidate.email == candidate_data.email).first()
    if existing_candidate:
        raise HTTPException(status_code=400, detail="Candidate with this email already exists")
    
    # Create database record
    db_candidate = Candidate(
        name=candidate_data.name,
        email=candidate_data.email,
        phone=candidate_data.phone,
        position_id=candidate_data.position_id,
        status=candidate_data.status
    )
    
    # Save resume if provided
    if resume_file:
        file_path = await save_resume_file(resume_file, RESUME_DIR)
        db_candidate.resume_path = str(file_path)
        
        # Extract content from the file (simplified)
        try:
            with open(file_path, "r", errors="ignore") as f:
                db_candidate.resume_content = f.read()
        except:
            db_candidate.resume_content = "Failed to extract content from resume"
    
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    
    return db_candidate

def get_candidate(db: Session, candidate_id: int) -> Optional[Candidate]:
    """Get a candidate by ID."""
    return db.query(Candidate).filter(Candidate.id == candidate_id).first()

def get_candidates(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    position_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Candidate]:
    """Get all candidates, optionally filtered by position or status."""
    query = db.query(Candidate)
    
    if position_id:
        query = query.filter(Candidate.position_id == position_id)
    
    if status:
        query = query.filter(Candidate.status == status)
    
    # Eagerly load the skills relationship to include it in the response
    return query.options(
        sqlalchemy.orm.joinedload(Candidate.skills)
    ).offset(skip).limit(limit).all()

def update_candidate(
    db: Session, 
    candidate_id: int, 
    candidate_data: dict
) -> Optional[Candidate]:
    """Update a candidate's information."""
    db_candidate = get_candidate(db, candidate_id)
    
    if not db_candidate:
        return None
    
    # Update fields
    for key, value in candidate_data.items():
        if hasattr(db_candidate, key):
            setattr(db_candidate, key, value)
    
    db.commit()
    db.refresh(db_candidate)
    
    return db_candidate

def delete_candidate(db: Session, candidate_id: int) -> bool:
    """Delete a candidate and their resume file."""
    db_candidate = get_candidate(db, candidate_id)
    
    if not db_candidate:
        return False
    
    # Delete the resume file if it exists
    if db_candidate.resume_path:
        file_path = Path(db_candidate.resume_path)
        if file_path.exists():
            file_path.unlink()
    
    # Delete from database
    db.delete(db_candidate)
    db.commit()
    
    return True

def add_skill_to_candidate(db: Session, candidate_id: int, skill_id: int) -> bool:
    """Add a skill to a candidate."""
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        return False
    
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        return False
    
    # Check if candidate already has this skill
    if skill in candidate.skills:
        return True
    
    candidate.skills.append(skill)
    db.commit()
    
    return True

def remove_skill_from_candidate(db: Session, candidate_id: int, skill_id: int) -> bool:
    """Remove a skill from a candidate."""
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        return False
    
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill or skill not in candidate.skills:
        return False
    
    candidate.skills.remove(skill)
    db.commit()
    
    return True

def update_candidate_status(db: Session, candidate_id: int, status: str) -> Optional[Candidate]:
    """Update a candidate's status."""
    valid_statuses = ["New", "Reviewing", "Interview", "Offer", "Rejected", "Hired"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    return update_candidate(db, candidate_id, {"status": status}) 