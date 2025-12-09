from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from app.core.db import get_session
from app.models.models import Attendance, AttendanceBase, Employee, Branch

router = APIRouter()

class AttendanceCreate(AttendanceBase):
    employee_id: int
    branch_id: int

@router.post("/", response_model=Attendance)
def create_attendance(attendance: AttendanceCreate, session: Session = Depends(get_session)):
    # Verify employee and branch exist
    employee_id = attendance.employee_id
    branch_id = attendance.branch_id
    
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    branch = session.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # Check for duplicates (Idempotency)
    # If the same employee has exact same timestamp and type, it's a sync retry.
    statement = select(Attendance).where(
        Attendance.employee_id == employee_id,
        Attendance.timestamp == attendance.timestamp,
        Attendance.type == attendance.type
    )
    existing = session.exec(statement).first()
    if existing:
        # Already exists, just return it (idempotent success)
        print(f"Duplicate attendance detected/ignored: {employee.first_name} at {attendance.timestamp}")
        return existing

    try:
        # Create DB model from Input model
        db_attendance = Attendance.from_orm(attendance)
        
        # TIMEZONE CORRECTION:
        # The App sends UTC (e.g. 2025-12-09T09:00:00Z).
        # We want to store LOCAL TIME in the DB (e.g. 2025-12-09T03:00:00).
        # So we convert the incoming timestamp to local system time.
        if db_attendance.timestamp.tzinfo is not None:
             # Convert aware to local (naive)
             db_attendance.timestamp = db_attendance.timestamp.astimezone().replace(tzinfo=None)
        else:
             # Naive input. Assume it is UTC (standard for API JSON).
             # Convert: Naive(UTC) -> Aware(UTC) -> Convert to Local -> Naive(Local)
             from datetime import timezone
             utc_dt = db_attendance.timestamp.replace(tzinfo=timezone.utc)
             local_dt = utc_dt.astimezone() # System Local Time
             db_attendance.timestamp = local_dt.replace(tzinfo=None)

        # Explicitly set IDs just in case, though from_orm might handle it if fields match
        db_attendance.employee_id = employee_id
        db_attendance.branch_id = branch_id
        
        session.add(db_attendance)
        session.commit()
        session.refresh(db_attendance)
        return db_attendance
    except Exception as e:
        print(f"Error creating attendance: {e}")
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
