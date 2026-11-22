import json

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import Analysis
from app.models.resume import Resume

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def dashboard_stats(user_id: int, db: Session = Depends(get_db)):
    resume_count = db.query(Resume).filter(Resume.user_id == user_id).count()
    analysis_count = (
        db.query(Analysis)
        .join(Resume, Analysis.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .count()
    )

    latest_analysis_ids = (
        db.query(func.max(Analysis.id).label("analysis_id"))
        .join(Resume, Analysis.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .group_by(Analysis.resume_id)
        .subquery()
    )
    latest_analyses = db.query(Analysis).filter(
        Analysis.id.in_(db.query(latest_analysis_ids.c.analysis_id))
    ).all()
    scores = []
    for analysis in latest_analyses:
        try:
            details = json.loads(analysis.feedback or "{}")
        except json.JSONDecodeError:
            continue
        if isinstance(details, dict) and isinstance(details.get("overall_score"), (int, float)):
            scores.append(details["overall_score"])
    average_score = sum(scores) / len(scores) if scores else None

    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc(), Resume.id.desc())
        .limit(10)
        .all()
    )
    recent_resumes = []
    for resume in resumes:
        analysis = (
            db.query(Analysis)
            .filter(Analysis.resume_id == resume.id)
            .order_by(Analysis.id.desc())
            .first()
        )
        try:
            details = json.loads(analysis.feedback or "{}") if analysis else {}
        except json.JSONDecodeError:
            details = {}
        score = details.get("overall_score") if isinstance(details, dict) else None
        recent_resumes.append({
            "id": resume.id,
            "resume_id": resume.id,
            "analysis_id": analysis.id if analysis else None,
            "filename": resume.filename,
            "created_at": resume.created_at,
            "status": "Analyzed" if analysis else "Uploaded",
            "score": round(score) if isinstance(score, (int, float)) else None,
        })

    return {
        "total_resumes": resume_count,
        "total_analyses": analysis_count,
        "average_score": round(average_score, 2) if average_score is not None else None,
        "recent_resumes": recent_resumes,
    }
