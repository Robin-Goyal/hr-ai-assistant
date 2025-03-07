from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import User
from ...models.schemas import Application, ApplicationCreate, ApplicationDetail, ApplicationUpdate
from ...services.auth_service import get_current_active_user
from ...services.application_service import (
    create_application, get_application, get_applications,
    update_application, delete_application, update_application_status,
    add_interview_date
)

router = APIRouter()

@router.get("/", response_model=List[Application])
def read_applications(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    candidate_id: Optional[int] = None,
    position_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve applications, optionally filtered by candidate, position, or status.
    """
    return get_applications(
        db, 
        skip=skip, 
        limit=limit, 
        candidate_id=candidate_id, 
        position_id=position_id, 
        status=status
    )

@router.post("/", response_model=Application)
def create_new_application(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new application.
    """
    return create_application(db, application_data)

@router.get("/{application_id}", response_model=ApplicationDetail)
def read_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get application by ID.
    """
    application = get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

@router.put("/{application_id}", response_model=Application)
def update_application_data(
    application_id: int,
    application_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update an application.
    """
    application = get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    updated_application = update_application(db, application_id, application_data)
    if not updated_application:
        raise HTTPException(status_code=400, detail="Failed to update application")
    
    return updated_application

@router.delete("/{application_id}", response_model=Application)
def delete_application_data(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete an application.
    """
    application = get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if delete_application(db, application_id):
        return application
    
    raise HTTPException(status_code=400, detail="Failed to delete application")

@router.put("/{application_id}/status", response_model=Application)
def update_application_status_endpoint(
    application_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update an application's status.
    """
    application = get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    updated_application = update_application_status(db, application_id, status)
    if not updated_application:
        raise HTTPException(status_code=400, detail="Failed to update application status")
    
    return updated_application

@router.put("/{application_id}/interview-date", response_model=Application)
def add_interview_date_endpoint(
    application_id: int,
    interview_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Add an interview date to an application.
    """
    application = get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    updated_application = add_interview_date(db, application_id, interview_date)
    if not updated_application:
        raise HTTPException(status_code=400, detail="Failed to add interview date")
    
    return updated_application 