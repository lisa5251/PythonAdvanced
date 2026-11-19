
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models

from app.routes import auth, resumes, analysis, dashboard, admin


# Create database tables
Base.metadata.create_all(bind=engine)


# Initialize FastAPI
app = FastAPI(
    title="ResumeIQ",
    description="AI Powered Resume Analyzer",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:63342",
        "http://127.0.0.1:63342"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


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
