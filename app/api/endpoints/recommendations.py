from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.logs import get_recommendations
from app.schemas.burnout import RecommendationResponse
from typing import List

router = APIRouter()

@router.get("/{user_id}", response_model=List[RecommendationResponse])
def get_user_recommendations(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    recs = get_recommendations(db, user_id, limit=limit)
    if not recs:
        raise HTTPException(status_code=404, detail="No recommendations found")
    return recs