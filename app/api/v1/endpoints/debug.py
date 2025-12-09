from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, delete, select
from app.core.db import get_session
from app.models.models import Attendance, AttendanceBase, Employee, Branch

router = APIRouter()

@router.delete("/clear-all-attendance-danger-zone")
def clear_all_attendance(key: str, session: Session = Depends(get_session)):
    if key != "silveronics-secret-key-123":
        raise HTTPException(status_code=403, detail="Forbidden")
    
    statement = delete(Attendance)
    result = session.exec(statement)
    session.commit()
    return {"status": "ok", "deleted_rows": result.rowcount}
