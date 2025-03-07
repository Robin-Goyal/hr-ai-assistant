from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import User, Candidate as CandidateModel, Skill as SkillModel
from ...models.schemas import (
    Candidate, CandidateCreate, CandidateDetail, CandidateUpdate,
    Skill, Note, NoteCreate, SkillOut, SkillNameList
)
from ...services.auth_service import get_current_active_user
from ...services.candidate_service import (
    create_candidate, get_candidate, get_candidates,
    update_candidate, delete_candidate, add_skill_to_candidate,
    remove_skill_from_candidate, update_candidate_status
)
from ...services.note_service import create_note, get_candidate_notes
from ...services.skill_service import get_skill, get_or_create_skills
from pydantic import BaseModel

router = APIRouter()

# Add a Pydantic model for the skills request
class SkillNamesRequest(BaseModel):
    skill_names: List[str]

@router.get("/", response_model=List[CandidateDetail])
def read_candidates(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    position_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve candidates, optionally filtered by position or status.
    """
    return get_candidates(db, skip=skip, limit=limit, position_id=position_id, status=status)

@router.post("/", response_model=Candidate)
async def create_new_candidate(
    db: Session = Depends(get_db),
    *,
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    position_id: Optional[int] = Form(None),
    status: str = Form("New"),
    resume: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new candidate.
    """
    candidate_data = CandidateCreate(
        name=name,
        email=email,
        phone=phone,
        position_id=position_id,
        status=status
    )
    
    return await create_candidate(db, candidate_data, resume)

@router.get("/{candidate_id}", response_model=CandidateDetail)
def read_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get candidate by ID.
    """
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@router.put("/{candidate_id}", response_model=Candidate)
def update_candidate_data(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a candidate.
    """
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    updated_candidate = update_candidate(db, candidate_id, candidate_data.dict(exclude_unset=True))
    return updated_candidate

@router.delete("/{candidate_id}", response_model=Candidate)
def delete_candidate_data(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a candidate.
    """
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not delete_candidate(db, candidate_id):
        raise HTTPException(status_code=400, detail="Failed to delete candidate")
    
    return candidate

@router.put("/{candidate_id}/status", response_model=Candidate)
def update_candidate_status_endpoint(
    candidate_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a candidate's status.
    """
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    updated_candidate = update_candidate_status(db, candidate_id, status)
    if not updated_candidate:
        raise HTTPException(status_code=400, detail="Failed to update candidate status")
    
    return updated_candidate

@router.post("/{candidate_id}/skills", response_model=List[SkillOut])
def add_skills_to_candidate(
    candidate_id: int,
    skill_request: SkillNamesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add skills to a candidate by providing skill names
    """
    candidate = db.query(CandidateModel).filter(CandidateModel.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Create a list to store added skills
    added_skills = []
    
    # Process each skill name
    for skill_name in skill_request.skill_names:
        # Check if skill exists
        skill = db.query(SkillModel).filter(SkillModel.name == skill_name).first()
        
        # If skill doesn't exist, create it
        if not skill:
            skill = SkillModel(name=skill_name, category="General")
            db.add(skill)
            db.commit()
            db.refresh(skill)
        
        # Check if candidate already has this skill
        if skill not in candidate.skills:
            candidate.skills.append(skill)
            added_skills.append(skill)
    
    # Commit changes if any skills were added
    if added_skills:
        db.commit()
    
    return added_skills

@router.delete("/{candidate_id}/skills/{skill_id}", response_model=CandidateDetail)
def remove_skill_from_candidate_endpoint(
    candidate_id: int,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Remove a skill from a candidate.
    """
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    skill = get_skill(db, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    if not remove_skill_from_candidate(db, candidate_id, skill_id):
        raise HTTPException(status_code=400, detail="Failed to remove skill from candidate")
    
    return get_candidate(db, candidate_id)

@router.post("/{candidate_id}/notes", response_model=Note)
def add_note_to_candidate(
    candidate_id: int,
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Add a note to a candidate.
    """
    # Check if candidate exists
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Override candidate_id just to be safe
    note_data_with_candidate = NoteCreate(
        candidate_id=candidate_id,
        content=note_data.content,
        note_type=note_data.note_type,
        created_by=note_data.created_by or current_user.username
    )
    
    # Create note
    return create_note(db, note_data_with_candidate)

@router.get("/{candidate_id}/notes", response_model=List[Note])
def get_notes_for_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get all notes for a candidate.
    """
    # Check if candidate exists
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return get_candidate_notes(db, candidate_id) 