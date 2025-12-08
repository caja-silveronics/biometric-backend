from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.db import get_session
from app.models.models import Employee, EmployeeBase, Branch

router = APIRouter()

@router.post("/", response_model=Employee)
def create_employee(employee: EmployeeBase, branch_id: int, session: Session = Depends(get_session)):
    branch = session.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    db_employee = Employee.from_orm(employee)
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
