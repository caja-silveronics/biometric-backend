from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.core.db import get_session
from app.models.models import Branch, BranchBase

router = APIRouter()

@router.post("/", response_model=Branch)
def create_branch(branch: BranchBase, session: Session = Depends(get_session)):
    # Check if branch with same name already exists
    statement = select(Branch).where(Branch.name == branch.name)
    existing_branch = session.exec(statement).first()
    
    if existing_branch:
        # Update existing branch with new data
        existing_branch.address = branch.address
        existing_branch.phone = branch.phone
        existing_branch.city = branch.city
        existing_branch.code = branch.code
        existing_branch.radius = branch.radius
        existing_branch.latitude = branch.latitude
        existing_branch.longitude = branch.longitude
        
        session.add(existing_branch)
        session.commit()
        session.refresh(existing_branch)
        return existing_branch

    db_branch = Branch.from_orm(branch)
    session.add(db_branch)
    session.commit()
    session.refresh(db_branch)
    return db_branch

@router.get("/", response_model=List[Branch])
def read_branches(session: Session = Depends(get_session)):
    branches = session.exec(select(Branch)).all()
    return branches

@router.delete("/{branch_id}")
def delete_branch(branch_id: int, session: Session = Depends(get_session)):
    branch = session.get(Branch, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    session.delete(branch)
    session.commit()
    return {"ok": True}
