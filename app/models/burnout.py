from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    usage_logs = relationship("UsageLog", back_populates="user")
    predictions = relationship("BurnoutPrediction", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    tasks = relationship("DailyTask", back_populates="user")
    survey_responses = relationship("SurveyResponse", back_populates="user")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    total_screen_time_minutes = Column(Integer, default=0)
    social_media_minutes = Column(Integer, default=0)
    study_work_minutes = Column(Integer, default=0)
    breaks_taken = Column(Integer, default=0)
    notifications_received = Column(Integer, default=0)
    self_reported_stress = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="usage_logs")


class DailyTask(Base):
    __tablename__ = "daily_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    task_name = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    time_spent_minutes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tasks")


class BurnoutPrediction(Base):
    __tablename__ = "burnout_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    forecast_date = Column(Date, nullable=False)
    predicted_risk = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    model_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    study_hours_per_day = Column(Integer, default=0)
    social_media_hours = Column(Integer, default=0)
    task_consistency = Column(Integer, default=3)
    time_management = Column(Integer, default=3)
    stress_level = Column(Integer, default=3)
    mental_exhaustion = Column(Integer, default=3)
    motivation = Column(Integer, default=3)
    expected_workload = Column(Integer, default=3)
    expected_study_hours = Column(Integer, default=0)
    expected_social_media = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="survey_responses")