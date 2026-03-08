from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.logs import create_usage_log, get_all_logs, generate_prediction, get_recovery_trend
from app.schemas.burnout import UsageLogCreate, UsageLogResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=UsageLogResponse, status_code=201)
def add_log(log: UsageLogCreate, db: Session = Depends(get_db)):
    saved_log = create_usage_log(db, log.model_dump())
    generate_prediction(db, log.user_id)
    return saved_log

@router.get("/{user_id}/recovery")
def get_recovery(user_id: int, db: Session = Depends(get_db)):
    return get_recovery_trend(db, user_id)

@router.get("/{user_id}", response_model=List[UsageLogResponse])
def get_user_logs(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logs = get_all_logs(db, user_id, skip=skip, limit=limit)
    if not logs:
        raise HTTPException(status_code=404, detail="No logs found for this user")
    return logs