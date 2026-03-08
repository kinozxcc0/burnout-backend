from sqlalchemy.orm import Session
from app.models.burnout import UsageLog, BurnoutPrediction, Recommendation, SurveyResponse
from datetime import date, timedelta
from app.ai.lstm_model import predict_burnout_risk

def create_usage_log(db: Session, log_data: dict):
    existing = db.query(UsageLog).filter(
        UsageLog.user_id == log_data["user_id"],
        UsageLog.date == log_data["date"]
    ).first()
    if existing:
        for key, value in log_data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    log = UsageLog(**log_data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_last_30_days_logs(db: Session, user_id: int):
    start_date = date.today() - timedelta(days=30)
    return db.query(UsageLog).filter(
        UsageLog.user_id == user_id,
        UsageLog.date >= start_date
    ).order_by(UsageLog.date.asc()).all()

def get_all_logs(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(UsageLog).filter(
        UsageLog.user_id == user_id
    ).order_by(UsageLog.date.desc()).offset(skip).limit(limit).all()

def generate_prediction(db: Session, user_id: int):
    logs = get_last_30_days_logs(db, user_id)

    logs_dict = [{
        "total_screen_time_minutes": l.total_screen_time_minutes,
        "social_media_minutes":      l.social_media_minutes,
        "study_work_minutes":        l.study_work_minutes,
        "breaks_taken":              l.breaks_taken,
        "notifications_received":    l.notifications_received,
        "self_reported_stress":      l.self_reported_stress or 5
    } for l in logs]

    # ✅ Pass survey answers into AI for better accuracy
    survey_row = db.query(SurveyResponse).filter(
        SurveyResponse.user_id == user_id
    ).first()

    survey_dict = None
    if survey_row:
        survey_dict = {
            "stress_level":      survey_row.stress_level,
            "mental_exhaustion": survey_row.mental_exhaustion,
            "motivation":        survey_row.motivation,
            "expected_workload": survey_row.expected_workload,
            "task_consistency":  survey_row.task_consistency,
            "time_management":   survey_row.time_management,
        }

    result = predict_burnout_risk(logs_dict, survey=survey_dict)

    forecast_date = date.today() + timedelta(days=7)
    existing_pred = db.query(BurnoutPrediction).filter(
        BurnoutPrediction.user_id == user_id,
        BurnoutPrediction.forecast_date == forecast_date
    ).first()

    if existing_pred:
        existing_pred.predicted_risk = result["7_day_forecast_risk"]
        existing_pred.confidence     = 0.85
        existing_pred.model_version  = "combined_v2"
        db.commit()
    else:
        db.add(BurnoutPrediction(
            user_id=user_id,
            forecast_date=forecast_date,
            predicted_risk=result["7_day_forecast_risk"],
            confidence=0.85,
            model_version="combined_v2"
        ))
        db.commit()

    save_recommendation(db, user_id, result["recommendation"], result["current_risk"])
    return result

def get_predictions_history(db: Session, user_id: int, limit: int = 30):
    return db.query(BurnoutPrediction).filter(
        BurnoutPrediction.user_id == user_id
    ).order_by(BurnoutPrediction.created_at.desc()).limit(limit).all()

def save_recommendation(db: Session, user_id: int, message: str, risk: float):
    rec_type = "detox" if risk > 0.75 else "reduce" if risk > 0.50 else "maintain"
    existing = db.query(Recommendation).filter(
        Recommendation.user_id == user_id,
        Recommendation.date == date.today()
    ).first()
    if existing:
        existing.message = message
        existing.type    = rec_type
        db.commit()
    else:
        db.add(Recommendation(
            user_id=user_id,
            date=date.today(),
            message=message,
            type=rec_type
        ))
        db.commit()

def get_recommendations(db: Session, user_id: int, limit: int = 10):
    return db.query(Recommendation).filter(
        Recommendation.user_id == user_id
    ).order_by(Recommendation.date.desc()).limit(limit).all()

def get_recovery_trend(db: Session, user_id: int):
    recent_logs = db.query(UsageLog).filter(
        UsageLog.user_id == user_id,
        UsageLog.date >= date.today() - timedelta(days=7)
    ).all()
    previous_logs = db.query(UsageLog).filter(
        UsageLog.user_id == user_id,
        UsageLog.date >= date.today() - timedelta(days=14),
        UsageLog.date < date.today() - timedelta(days=7)
    ).all()

    def avg(logs, field):
        vals = [getattr(l, field) for l in logs if getattr(l, field) is not None]
        return round(sum(vals) / len(vals), 2) if vals else 0

    return {
        "recent_7_days":   {"avg_screen_time": avg(recent_logs, "total_screen_time_minutes"),
                            "avg_stress": avg(recent_logs, "self_reported_stress"),
                            "avg_breaks": avg(recent_logs, "breaks_taken")},
        "previous_7_days": {"avg_screen_time": avg(previous_logs, "total_screen_time_minutes"),
                            "avg_stress": avg(previous_logs, "self_reported_stress"),
                            "avg_breaks": avg(previous_logs, "breaks_taken")},
        "improving": avg(recent_logs, "self_reported_stress") <= avg(previous_logs, "self_reported_stress")
    }