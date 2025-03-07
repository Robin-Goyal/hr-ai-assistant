from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.models import Department
from ..models.schemas import DepartmentCreate, DepartmentUpdate

def create_department(db: Session, department_data: DepartmentCreate) -> Department:
    """Create a new department."""
    # Check if department with same name already exists
    existing_department = db.query(Department).filter(
        Department.name == department_data.name
    ).first()
    
    if existing_department:
        raise HTTPException(
            status_code=400, 
            detail=f"Department '{department_data.name}' already exists"
        )
    
    # Create the department
    db_department = Department(
        name=department_data.name,
        description=department_data.description
    )
    
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    
    return db_department

def get_department(db: Session, department_id: int) -> Optional[Department]:
    """Get a department by ID."""
    return db.query(Department).filter(Department.id == department_id).first()

def get_departments(db: Session, skip: int = 0, limit: int = 100) -> List[Department]:
    """Get all departments."""
    return db.query(Department).offset(skip).limit(limit).all()

def update_department(db: Session, department_id: int, department_data: DepartmentUpdate) -> Optional[Department]:
    """Update a department's information."""
    db_department = get_department(db, department_id)
    
    if not db_department:
        return None
    
    # Check for name conflict if name is being changed
    update_data = department_data.dict(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_department.name:
        existing_department = db.query(Department).filter(
            Department.name == update_data["name"]
        ).first()
        
        if existing_department:
            raise HTTPException(
                status_code=400, 
                detail=f"Department '{update_data['name']}' already exists"
            )
    
    # Update fields
    for key, value in update_data.items():
        setattr(db_department, key, value)
    
    db.commit()
    db.refresh(db_department)
    
    return db_department

def delete_department(db: Session, department_id: int) -> bool:
    """Delete a department."""
    db_department = get_department(db, department_id)
    
    if not db_department:
        return False
    
    # Check if department has any positions
    if db_department.positions and len(db_department.positions) > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete department with associated positions"
        )
    
    db.delete(db_department)
    db.commit()
    
    return True

def get_department_positions(db: Session, department_id: int) -> List:
    """Get all positions in a department."""
    department = get_department(db, department_id)
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return department.positions 