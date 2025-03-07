from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.models import Note, Candidate
from ..models.schemas import NoteCreate, NoteUpdate

def create_note(db: Session, note_data: NoteCreate) -> Note:
    """Create a new note for a candidate."""
    # Check if candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == note_data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Create the note
    db_note = Note(
        candidate_id=note_data.candidate_id,
        content=note_data.content,
        note_type=note_data.note_type,
        created_date=datetime.now(),
        created_by=note_data.created_by
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return db_note

def get_note(db: Session, note_id: int) -> Optional[Note]:
    """Get a note by ID."""
    return db.query(Note).filter(Note.id == note_id).first()

def get_notes(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    candidate_id: Optional[int] = None,
    note_type: Optional[str] = None
) -> List[Note]:
    """Get all notes, optionally filtered by candidate or type."""
    query = db.query(Note)
    
    if candidate_id:
        query = query.filter(Note.candidate_id == candidate_id)
    
    if note_type:
        query = query.filter(Note.note_type == note_type)
    
    return query.order_by(Note.created_date.desc()).offset(skip).limit(limit).all()

def update_note(db: Session, note_id: int, note_data: NoteUpdate) -> Optional[Note]:
    """Update a note's information."""
    db_note = get_note(db, note_id)
    
    if not db_note:
        return None
    
    # Update fields
    update_data = note_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_note, key, value)
    
    # Set updated fields
    db_note.updated_date = datetime.now()
    
    db.commit()
    db.refresh(db_note)
    
    return db_note

def delete_note(db: Session, note_id: int) -> bool:
    """Delete a note."""
    db_note = get_note(db, note_id)
    
    if not db_note:
        return False
    
    db.delete(db_note)
    db.commit()
    
    return True

def get_candidate_notes(db: Session, candidate_id: int, note_types: Optional[List[str]] = None) -> List[Note]:
    """Get all notes for a candidate, optionally filtered by note types."""
    query = db.query(Note).filter(Note.candidate_id == candidate_id)
    
    if note_types:
        query = query.filter(Note.note_type.in_(note_types))
    
    return query.order_by(Note.created_date.desc()).all()

def add_interview_note(db: Session, candidate_id: int, content: str, created_by: str) -> Note:
    """Add an interview note for a candidate."""
    note_data = NoteCreate(
        candidate_id=candidate_id,
        content=content,
        note_type="Interview",
        created_by=created_by
    )
    
    return create_note(db, note_data) 