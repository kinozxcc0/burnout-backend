from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.endpoints import predictions, users, logs, tasks, recommendations, survey

app = FastAPI(
    title="Digital Burnout System API",
    version="1.0",
    description="AI-powered burnout detection and productivity monitoring system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router,            prefix="/api/v1/users",           tags=["Users"])
app.include_router(logs.router,             prefix="/api/v1/logs",            tags=["Usage Logs"])
app.include_router(predictions.router,      prefix="/api/v1/predictions",     tags=["Predictions"])
app.include_router(tasks.router,            prefix="/api/v1/tasks",           tags=["Daily Tasks"])
app.include_router(recommendations.router,  prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(survey.router,           prefix="/api/v1/survey",          tags=["Survey"])

@app.get("/")
def root():
    return {"message": "Digital Burnout System API is running!", "version": "1.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}