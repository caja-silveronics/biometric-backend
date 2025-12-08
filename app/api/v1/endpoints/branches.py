from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.db import get_session
from app.models.models import Branch, BranchBase

router = APIRouter()

@router.post("/", response_model=Branch)
def create_branch(branch: BranchBase, session: Session = Depends(get_session)):
    db_branch = Branch.from_orm(branch)
    session.add(db_branch)
    session.commit()
    session.refresh(db_branch)
    return db_branch

@router.get("/", response_model=List[Branch])
def read_branches(session: Session = Depends(get_session)):
    branches = session.exec(select(Branch)).all()
    return branches
