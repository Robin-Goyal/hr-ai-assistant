from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.models import Application, Candidate, Position
from ..models.schemas import ApplicationCreate, ApplicationUpdate

def create_application(db: Session, application_data: ApplicationCreate) -> Application:
    """Create a new application."""
    # Check if candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == application_data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Check if position exists
    position = db.query(Position).filter(Position.id == application_data.position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    # Check if position is active
    if not position.is_active:
        raise HTTPException(status_code=400, detail="Cannot apply for inactive position")
    
    # Check if candidate already applied for this position
    existing_application = db.query(Application).filter(
        Application.candidate_id == application_data.candidate_id,
        Application.position_id == application_data.position_id
    ).first()
    
    if existing_application:
        raise HTTPException(
            status_code=400, 
            detail="Candidate has already applied for this position"
        )
    
    # Create the application
    db_application = Application(
        candidate_id=application_data.candidate_id,
        position_id=application_data.position_id,
        status=application_data.status or "New",
        applied_date=datetime.now(),
        notes=application_data.notes
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    return db_application

def get_application(db: Session, application_id: int) -> Optional[Application]:
    """Get an application by ID."""
    return db.query(Application).filter(Application.id == application_id).first()

def get_applications(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    candidate_id: Optional[int] = None,
    position_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Application]:
    """Get all applications, optionally filtered."""
    query = db.query(Application)
    
    if candidate_id:
        query = query.filter(Application.candidate_id == candidate_id)
    
    if position_id:
        query = query.filter(Application.position_id == position_id)
    
    if status:
        query = query.filter(Application.status == status)
    
    return query.offset(skip).limit(limit).all()

def update_application(db: Session, application_id: int, application_data: ApplicationUpdate) -> Optional[Application]:
    """Update an application's information."""
    db_application = get_application(db, application_id)
    
    if not db_application:
        return None
    
    # Update fields
    update_data = application_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_application, key, value)
    
    # If status is changing, update status date
    if "status" in update_data:
        db_application.status_updated_date = datetime.now()
    
    db.commit()
    db.refresh(db_application)
    
    return db_application

def delete_application(db: Session, application_id: int) -> bool:
    """Delete an application."""
    db_application = get_application(db, application_id)
    
    if not db_application:
        return False
    
    db.delete(db_application)
    db.commit()
    
    return True

def update_application_status(db: Session, application_id: int, status: str) -> Optional[Application]:
    """Update an application's status."""
    valid_statuses = ["New", "Reviewing", "Interview", "Offer", "Rejected", "Hired"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    db_application = get_application(db, application_id)
    
    if not db_application:
        return None
    
    db_application.status = status
    db_application.status_updated_date = datetime.now()
    
    db.commit()
    db.refresh(db_application)
    
    return db_application

def add_interview_date(db: Session, application_id: int, interview_date: datetime) -> Optional[Application]:
    """Add an interview date to an application."""
    db_application = get_application(db, application_id)
    
    if not db_application:
        return None
    
    db_application.interview_date = interview_date
    
    if db_application.status not in ["Interview", "Offer", "Hired"]:
        db_application.status = "Interview"
        db_application.status_updated_date = datetime.now()
    
    db.commit()
    db.refresh(db_application)
    
    return db_application 