from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from app.core.db import get_session
from app.models.models import Attendance, AttendanceBase, Employee, Branch

router = APIRouter()

@router.post("/", response_model=Attendance)
def create_attendance(attendance: AttendanceBase, employee_id: int, branch_id: int, session: Session = Depends(get_session)):
    # Verify employee and branch exist
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    branch = session.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    try:
        db_attendance = Attendance.from_orm(attendance)
        db_attendance.employee_id = employee_id
        db_attendance.branch_id = branch_id
        
        session.add(db_attendance)
        session.commit()
        session.refresh(db_attendance)
        return db_attendance
    except Exception as e:
        print(f"❌ Error creating attendance: {e}")
        # Return 400 instead of 500
        raise HTTPException(status_code=400, detail=f"Error creating attendance record: {str(e)}")

@router.get("/", response_model=List[Attendance])
def read_attendances(
    branch_id: int = None, 
    employee_id: int = None, 
    date: datetime = None,
    session: Session = Depends(get_session)
):
    query = select(Attendance)
    if branch_id:
        query = query.where(Attendance.branch_id == branch_id)
    if employee_id:
        query = query.where(Attendance.employee_id == employee_id)
    # Date filtering logic can be added here
    
    # Order by timestamp desc
    query = query.order_by(Attendance.timestamp.desc())
    
    attendances = session.exec(query).all()
    return attendances
