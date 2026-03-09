from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.endpoints import predictions, users, logs, tasks, recommendations, survey
import sys
import time

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

# --------------------------
# ✅ Automatic table creation with retry for slow DB connections
# --------------------------
max_retries = 5
for i in range(max_retries):
    try:
        print(f"Attempt {i+1}: Creating tables if they don't exist...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        break
    except Exception as e:
        print(f"⚠ Warning: Could not create tables on attempt {i+1}: {e}")
        if i < max_retries - 1:
            print("Retrying in 3 seconds...")
            time.sleep(3)
        else:
            print("❌ Failed to create tables after several attempts")
            sys.exit(1)

# --------------------------
# Include API routers
# --------------------------
app.include_router(users.router,            prefix="/api/v1/users",           tags=["Users"])
app.include_router(logs.router,             prefix="/api/v1/logs",            tags=["Usage Logs"])
app.include_router(predictions.router,      prefix="/api/v1/predictions",     tags=["Predictions"])
app.include_router(tasks.router,            prefix="/api/v1/tasks",           tags=["Daily Tasks"])
app.include_router(recommendations.router,  prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(survey.router,           prefix="/api/v1/survey",          tags=["Survey"])

# --------------------------
# Root and health check endpoints
# --------------------------
@app.get("/")
def root():
    return {"message": "Digital Burnout System API is running!", "version": "1.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}