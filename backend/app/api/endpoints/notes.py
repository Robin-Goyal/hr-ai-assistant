from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import User
from ...models.schemas import Note, NoteCreate, NoteUpdate
from ...services.auth_service import get_current_active_user
from ...services.note_service import (
    create_note, get_note, get_notes,
    update_note, delete_note
)

router = APIRouter()

@router.get("/", response_model=List[Note])
def read_notes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    candidate_id: Optional[int] = None,
    note_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve notes, optionally filtered by candidate or type.
    """
    return get_notes(db, skip=skip, limit=limit, candidate_id=candidate_id, note_type=note_type)

@router.post("/", response_model=Note)
def create_new_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new note.
    """
    # Set created_by if not provided
    if not note_data.created_by:
        note_data_dict = note_data.dict()
        note_data_dict["created_by"] = current_user.username
        note_data = NoteCreate(**note_data_dict)
    
    return create_note(db, note_data)

@router.get("/{note_id}", response_model=Note)
def read_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get note by ID.
    """
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{note_id}", response_model=Note)
def update_note_data(
    note_id: int,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a note.
    """
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    updated_note = update_note(db, note_id, note_data)
    if not updated_note:
        raise HTTPException(status_code=400, detail="Failed to update note")
    
    return updated_note

@router.delete("/{note_id}", response_model=Note)
def delete_note_data(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a note.
    """
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if delete_note(db, note_id):
        return note
    
    raise HTTPException(status_code=400, detail="Failed to delete note") 