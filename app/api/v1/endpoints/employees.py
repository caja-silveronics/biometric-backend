from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, SQLModel
from typing import List, Optional, Any
from app.core.db import get_session
from app.models.models import Employee, EmployeeBase, Branch

router = APIRouter()

class EmployeeUpsert(SQLModel):
    employee_number: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    work_schedule: Optional[Any] = None
    photo_url: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    face_embedding: Optional[List[float]] = None

@router.post("/", response_model=Employee)
def create_or_update_employee(employee: EmployeeUpsert, branch_id: int, session: Session = Depends(get_session)):
    branch = session.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Check if employee exists
    statement = select(Employee).where(Employee.employee_number == employee.employee_number)
    existing_employee = session.exec(statement).first()
    
    if existing_employee:
        # Update existing employee - Only update provided fields
        if employee.first_name is not None: existing_employee.first_name = employee.first_name
        if employee.last_name is not None: existing_employee.last_name = employee.last_name
        if employee.position is not None: existing_employee.position = employee.position
        if employee.department is not None: existing_employee.department = employee.department
        if employee.work_schedule is not None: existing_employee.work_schedule = employee.work_schedule
        if employee.photo_url is not None: existing_employee.photo_url = employee.photo_url
        if employee.phone is not None: existing_employee.phone = employee.phone
        if employee.is_active is not None: existing_employee.is_active = employee.is_active
        if employee.face_embedding is not None: existing_employee.face_embedding = employee.face_embedding
        
        # Always update branch if provided
        existing_employee.branch_id = branch_id
        
        session.add(existing_employee)
        session.commit()
        session.refresh(existing_employee)
        return existing_employee

    # For new creation, ensure required fields are present
    if not employee.first_name or not employee.last_name:
        raise HTTPException(status_code=422, detail="first_name and last_name are required for new employees")

    # Create new employee
    # We must explicitly map from Upsert model to Employee model
    new_employee_data = employee.dict(exclude_unset=True)
    db_employee = Employee(**new_employee_data)
    db_employee.branch_id = branch_id
    
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee

@router.get("/", response_model=List[Employee])
def read_employees(branch_id: int = None, session: Session = Depends(get_session)):
    query = select(Employee)
    if branch_id:
        query = query.where(Employee.branch_id == branch_id)
    employees = session.exec(query).all()
    return employees

@router.get("/{employee_id}", response_model=Employee)
def read_employee(employee_id: int, session: Session = Depends(get_session)):
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, session: Session = Depends(get_session)):
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    session.delete(employee)
    session.commit()
    return {"ok": True}
