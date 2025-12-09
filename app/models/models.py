from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column

class BranchBase(SQLModel):
    name: str = Field(index=True)
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: float = 100.0  # meters
    phone: Optional[str] = None
    city: Optional[str] = None

class Branch(BranchBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employees: List["Employee"] = Relationship(back_populates="branch")

class EmployeeBase(SQLModel):
    first_name: str
    last_name: str
    employee_number: str = Field(unique=True, index=True)
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    work_schedule: Optional[str] = None # e.g. "09:00 - 18:00"
    is_active: bool = True
    face_embedding: Optional[List[float]] = Field(default=None, sa_column=Column(JSON)) # Store vector as JSON list

class Employee(EmployeeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    branch_id: Optional[int] = Field(default=None, foreign_key="branch.id")
    branch: Optional[Branch] = Relationship(back_populates="employees")
    attendances: List["Attendance"] = Relationship(back_populates="employee")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AttendanceBase(SQLModel):
    timestamp: datetime
    type: str  # check-in, check-out
    status: str # on-time, late, etc
    confidence_score: Optional[float] = None
    biometric_verified: bool = False

class Attendance(AttendanceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id")
    employee: Employee = Relationship(back_populates="attendances")
    branch_id: int = Field(foreign_key="branch.id")
