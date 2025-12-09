from fastapi import APIRouter
from app.core.db import run_migrations

router = APIRouter()

@router.get("/migrate", response_model=list[str])
def debug_run_migrations():
    """ 手動でマイグレーションを実行する (Force run migrations manually) """
    logs = run_migrations()
    return logs
