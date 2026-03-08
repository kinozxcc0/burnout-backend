from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.logs import generate_prediction, get_predictions_history

router = APIRouter()

@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    from app.models.burnout import User, BurnoutPrediction
    from sqlalchemy import func

    total_users     = db.query(func.count(User.id)).scalar()
    avg_risk        = db.query(func.avg(BurnoutPrediction.predicted_risk)).scalar()
    high_risk_count = db.query(func.count(BurnoutPrediction.id)).filter(
        BurnoutPrediction.predicted_risk > 0.75).scalar()

    return {
        "total_users": total_users,
        "average_burnout_risk": round(avg_risk or 0, 3),
        "high_risk_users": high_risk_count
    }

@router.get("/{user_id}/history")
def get_prediction_history(user_id: int, db: Session = Depends(get_db)):
    history = get_predictions_history(db, user_id)
    if not history:
        raise HTTPException(status_code=404, detail="No prediction history found")
    return history

@router.get("/{user_id}")
def get_burnout_prediction(user_id: int, db: Session = Depends(get_db)):
    prediction = generate_prediction(db, user_id)
    return {
        "user_id":              user_id,
        "current_burnout_risk": prediction["current_risk"],
        "7_day_forecast":       prediction["7_day_forecast_risk"],
        "7_day_forecast_days":  prediction.get("7_day_forecast", []),
        "ai_recommendation":    prediction["recommendation"],
        "risk_level":           prediction.get("risk_level", "LOW"),
        "rule_based_score":     prediction.get("rule_based_score", 0),
        "lstm_score":           prediction.get("lstm_score", 0),
    }