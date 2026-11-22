import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import Analysis
from app.models.resume import Resume
from app.services.ai_service import (
    AIConfigurationError,
    AIServiceError,
    analyze_resume,
)
from app.services.scoring import calculate_job_match, calculate_resume_score

router = APIRouter(prefix="/analysis", tags=["Analysis"])


class AnalysisRequest(BaseModel):
    resume_id: int
    job_description: str = Field(default="", max_length=10000)


@router.post("/create")
def create_analysis(data: AnalysisRequest, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == data.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job_description = data.job_description.strip()
    score_data = calculate_resume_score(resume.extracted_text or "")
    match_data = calculate_job_match(
        resume.extracted_text or "",
        job_description,
    )

    try:
        ai_result = analyze_resume(resume.extracted_text or "", job_description)
    except AIConfigurationError as error:
        ai_result = None
        ai_notice = str(error)
    except AIServiceError as error:
        ai_result = None
        ai_notice = str(error)

    analysis_data = {
        **score_data,
        **match_data,
        "has_job_description": bool(job_description),
        "summary": (
            ai_result["summary"] if ai_result
            else "Your resume was scored using the ResumeIQ evidence-based rubric. "
                 "Review the category breakdown for the score details and improvement suggestions."
        ),
        "strengths": score_data["strengths"] + (
            ai_result["strengths"] if ai_result else []
        ),
        "ai_recommendations": (
            ai_result["recommendations"] if ai_result else []
        ),
        "ai_recommendations_available": ai_result is not None,
        "ai_notice": ai_notice if ai_result is None else "",
    }

    analysis = Analysis(
        resume_id=resume.id,
        job_description=job_description,
        match_score=score_data["overall_score"],
        matched_skills=json.dumps(match_data["matching_skills"]),
        missing_skills=json.dumps(match_data["missing_relevant_skills"]),
        feedback=json.dumps(analysis_data),
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        **analysis_data,
    }


@router.get("/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    try:
        details = json.loads(analysis.feedback or "{}")
    except json.JSONDecodeError:
        details = {}

    if not isinstance(details, dict):
        details = {}

    return {
        "id": analysis.id,
        "resume_id": analysis.resume_id,
        "overall_score": details.get("overall_score", analysis.match_score),
        "match_score": analysis.match_score,
        "job_match_percentage": details.get("job_match_percentage"),
        "has_job_description": details.get(
            "has_job_description",
            bool(analysis.job_description),
        ),
        "score_breakdown": details.get("score_breakdown", []),
        "summary": details.get("summary", analysis.feedback or ""),
        "strengths": details.get("strengths", []),
        "areas_to_improve": details.get("areas_to_improve", []),
        "improvements": details.get("improvements", []),
        "ai_recommendations": details.get("ai_recommendations", []),
        "ai_recommendations_available": details.get(
            "ai_recommendations_available",
            False,
        ),
        "ai_notice": details.get("ai_notice", ""),
        "skills_found": details.get("skills_found", []),
        "matching_skills": details.get(
            "matching_skills",
            json.loads(analysis.matched_skills or "[]"),
        ),
        "missing_relevant_skills": details.get(
            "missing_relevant_skills",
            json.loads(analysis.missing_skills or "[]"),
        ),
        "recommended_keywords": details.get("recommended_keywords", []),
        "feedback": details.get("summary", analysis.feedback or ""),
    }
