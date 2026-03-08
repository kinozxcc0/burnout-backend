from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.burnout import SurveyResponse

router = APIRouter()

@router.post("/", status_code=201)
def submit_survey(survey: dict, db: Session = Depends(get_db)):
    from app.schemas.burnout import SurveyCreate
    data = SurveyCreate(**survey)
    existing = db.query(SurveyResponse).filter(
        SurveyResponse.user_id == data.user_id
    ).first()
    if existing:
        for key, value in data.model_dump().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    new_survey = SurveyResponse(**data.model_dump())
    db.add(new_survey)
    db.commit()
    db.refresh(new_survey)
    return new_survey

@router.get("/check/{user_id}")
def check_survey_done(user_id: int, db: Session = Depends(get_db)):
    existing = db.query(SurveyResponse).filter(
        SurveyResponse.user_id == user_id
    ).first()
    return {"survey_done": existing is not None}

@router.get("/all")
def get_all_surveys(db: Session = Depends(get_db)):
    return db.query(SurveyResponse).all()  # ← was missing ()

@router.get("/{user_id}")
def get_survey(user_id: int, db: Session = Depends(get_db)):
    survey = db.query(SurveyResponse).filter(
        SurveyResponse.user_id == user_id
    ).first()
    if not survey:
        raise HTTPException(status_code=404, detail="No survey found")
    return survey