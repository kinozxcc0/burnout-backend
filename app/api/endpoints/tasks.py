from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.burnout import DailyTask
from app.schemas.burnout import DailyTaskCreate, DailyTaskResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=DailyTaskResponse, status_code=201)
def create_task(task: DailyTaskCreate, db: Session = Depends(get_db)):
    new_task = DailyTask(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/{user_id}", response_model=List[DailyTaskResponse])
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    return db.query(DailyTask).filter(
        DailyTask.user_id == user_id
    ).order_by(DailyTask.date.desc()).all()

@router.put("/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(DailyTask).filter(DailyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completed = True
    db.commit()
    return {"message": "Task marked as complete"}