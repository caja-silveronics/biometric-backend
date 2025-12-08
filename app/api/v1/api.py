from fastapi import APIRouter
from app.api.v1.endpoints import employees, branches, attendance

api_router = APIRouter()
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(branches.router, prefix="/branches", tags=["branches"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
