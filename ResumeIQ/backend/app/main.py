
from fastapi import FastAPI

from app.database import Base, engine
from app import models

from app.routes import auth, resumes, analysis, dashboard


# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="ResumeIQ",
    description="AI Powered Resume Analyzer",
    version="1.0.0"
)


# Register API routes
app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to ResumeIQ",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
