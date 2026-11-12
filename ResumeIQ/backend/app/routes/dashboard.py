
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.resume import Resume
from app.models.analysis import Analysis

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def dashboard_stats(
    user_id: int,
    db: Session = Depends(get_db)
):

    resume_count = db.query(Resume).filter(
        Resume.user_id == user_id
    ).count()

    analysis_count = db.query(Analysis).join(
        Resume,
        Analysis.resume_id == Resume.id
    ).filter(
        Resume.user_id == user_id
    ).count()

    average_score = db.query(
        func.avg(Analysis.match_score)
    ).join(
        Resume,
        Analysis.resume_id == Resume.id
    ).filter(
        Resume.user_id == user_id
    ).scalar()

    return {
        "total_resumes": resume_count,
        "total_analyses": analysis_count,
        "average_score": round(average_score or 0, 2)
    }
