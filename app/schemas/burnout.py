from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UsageLogBase(BaseModel):
    date: date
    total_screen_time_minutes: int
    social_media_minutes: int = 0
    study_work_minutes: int = 0
    breaks_taken: int = 0
    notifications_received: int = 0
    self_reported_stress: Optional[int] = None

class UsageLogCreate(UsageLogBase):
    user_id: int

class UsageLogResponse(UsageLogBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class DailyTaskBase(BaseModel):
    date: date
    task_name: str
    completed: bool = False
    time_spent_minutes: int = 0

class DailyTaskCreate(DailyTaskBase):
    user_id: int

class DailyTaskResponse(DailyTaskBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class PredictionResponse(BaseModel):
    id: int
    user_id: int
    forecast_date: date
    predicted_risk: float
    confidence: Optional[float]
    model_version: Optional[str]
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()
    )

class RecommendationResponse(BaseModel):
    id: int
    message: str
    type: Optional[str]
    date: date
    model_config = ConfigDict(from_attributes=True)

class SurveyCreate(BaseModel):
    user_id: int
    study_hours_per_day: int = 0
    social_media_hours: int = 0
    task_consistency: int = 3
    time_management: int = 3
    stress_level: int = 3
    mental_exhaustion: int = 3
    motivation: int = 3
    expected_workload: int = 3
    expected_study_hours: int = 0
    expected_social_media: int = 0

class SurveyResponse(BaseModel):
    id: int
    user_id: int
    study_hours_per_day: int
    social_media_hours: int
    task_consistency: int
    time_management: int
    stress_level: int
    mental_exhaustion: int
    motivation: int
    expected_workload: int
    expected_study_hours: int
    expected_social_media: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)