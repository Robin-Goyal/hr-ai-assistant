from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.models import Position, Department
from ..models.schemas import PositionCreate, PositionUpdate

def create_position(db: Session, position_data: PositionCreate) -> Position:
    """Create a new position."""
    # Check if department exists
    department = db.query(Department).filter(Department.id == position_data.department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if position with same title already exists in the department
    existing_position = db.query(Position).filter(
        Position.title == position_data.title,
        Position.department_id == position_data.department_id
    ).first()
    
    if existing_position:
        raise HTTPException(
            status_code=400, 
            detail=f"Position '{position_data.title}' already exists in this department"
        )
    
    # Create the position
    db_position = Position(
        title=position_data.title,
        description=position_data.description,
        requirements=position_data.requirements,
        responsibilities=position_data.responsibilities,
        location=position_data.location,
        salary_range=position_data.salary_range,
        is_active=position_data.is_active,
        department_id=position_data.department_id
    )
    
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    
    return db_position

def get_position(db: Session, position_id: int) -> Optional[Position]:
    """Get a position by ID."""
    return db.query(Position).filter(Position.id == position_id).first()

def get_positions(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[Position]:
    """Get all positions, optionally filtered by department or active status."""
    query = db.query(Position)
    
    if department_id:
        query = query.filter(Position.department_id == department_id)
    
    if is_active is not None:
        query = query.filter(Position.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

def update_position(db: Session, position_id: int, position_data: PositionUpdate) -> Optional[Position]:
    """Update a position's information."""
    db_position = get_position(db, position_id)
    
    if not db_position:
        return None
    
    # Update field values
    update_data = position_data.dict(exclude_unset=True)
    
    # If department_id is being updated, check if the department exists
    if "department_id" in update_data:
        department = db.query(Department).filter(Department.id == update_data["department_id"]).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
    
    for key, value in update_data.items():
        setattr(db_position, key, value)
    
    db.commit()
    db.refresh(db_position)
    
    return db_position

def delete_position(db: Session, position_id: int) -> bool:
    """Delete a position."""
    db_position = get_position(db, position_id)
    
    if not db_position:
        return False
    
    # Check if position has any associated candidates
    if db_position.candidates and len(db_position.candidates) > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete position with associated candidates"
        )
    
    db.delete(db_position)
    db.commit()
    
    return True

def toggle_position_status(db: Session, position_id: int) -> Optional[Position]:
    """Toggle a position's active status."""
    db_position = get_position(db, position_id)
    
    if not db_position:
        return None
    
    db_position.is_active = not db_position.is_active
    db.commit()
    db.refresh(db_position)
    
    return db_position 