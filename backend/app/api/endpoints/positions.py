from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import User
from ...models.schemas import Position, PositionCreate, PositionDetail, PositionUpdate
from ...services.auth_service import get_current_active_user
from ...services.position_service import (
    create_position, get_position, get_positions,
    update_position, delete_position, toggle_position_status
)

router = APIRouter()

@router.get("/", response_model=List[Position])
def read_positions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve positions, optionally filtered by department or active status.
    """
    return get_positions(db, skip=skip, limit=limit, department_id=department_id, is_active=is_active)

@router.post("/", response_model=Position)
def create_new_position(
    position_data: PositionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new position.
    """
    return create_position(db, position_data)

@router.get("/{position_id}", response_model=PositionDetail)
def read_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get position by ID.
    """
    position = get_position(db, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position

@router.put("/{position_id}", response_model=Position)
def update_position_data(
    position_id: int,
    position_data: PositionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a position.
    """
    position = get_position(db, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    updated_position = update_position(db, position_id, position_data)
    if not updated_position:
        raise HTTPException(status_code=400, detail="Failed to update position")
    
    return updated_position

@router.delete("/{position_id}", response_model=Position)
def delete_position_data(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a position.
    """
    position = get_position(db, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    try:
        if delete_position(db, position_id):
            return position
        raise HTTPException(status_code=400, detail="Failed to delete position")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{position_id}/toggle-status", response_model=Position)
def toggle_position_status_endpoint(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Toggle a position's active status.
    """
    position = get_position(db, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    updated_position = toggle_position_status(db, position_id)
    if not updated_position:
        raise HTTPException(status_code=400, detail="Failed to toggle position status")
    
    return updated_position 