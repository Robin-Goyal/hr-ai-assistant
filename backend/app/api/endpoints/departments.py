from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import User
from ...models.schemas import Department, DepartmentCreate, DepartmentUpdate, Position
from ...services.auth_service import get_current_active_user
from ...services.department_service import (
    create_department, get_department, get_departments,
    update_department, delete_department, get_department_positions
)

router = APIRouter()

@router.get("/", response_model=List[Department])
def read_departments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve departments.
    """
    return get_departments(db, skip=skip, limit=limit)

@router.post("/", response_model=Department)
def create_new_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new department.
    """
    return create_department(db, department_data)

@router.get("/{department_id}", response_model=Department)
def read_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get department by ID.
    """
    department = get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@router.put("/{department_id}", response_model=Department)
def update_department_data(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a department.
    """
    department = get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    updated_department = update_department(db, department_id, department_data)
    if not updated_department:
        raise HTTPException(status_code=400, detail="Failed to update department")
    
    return updated_department

@router.delete("/{department_id}", response_model=Department)
def delete_department_data(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a department.
    """
    department = get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    try:
        if delete_department(db, department_id):
            return department
        raise HTTPException(status_code=400, detail="Failed to delete department")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{department_id}/positions", response_model=List[Position])
def read_department_positions(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get all positions in a department.
    """
    department = get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return get_department_positions(db, department_id) 