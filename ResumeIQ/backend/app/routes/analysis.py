
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.services.ai_service import analyze_resume
from app.services.scoring import calculate_score

router = APIRouter(prefix="/analysis", tags=["Analysis"])


class AnalysisRequest(BaseModel):
    resume_id: int
    job_description: str = Field(
        min_length=30,
        max_length=10000
    )


@router.post("/create")
def create_analysis(
    data: AnalysisRequest,
    db: Session = Depends(get_db)
):

    resume = db.query(Resume).filter(
        Resume.id == data.resume_id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    score_data = calculate_score(
        resume.extracted_text,
        data.job_description
    )

    try:
        ai_result = analyze_resume(
            resume.extracted_text,
            data.job_description
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI analysis failed"
        )

    analysis = Analysis(
        resume_id=resume.id,
        job_description=data.job_description,
        match_score=score_data["score"],
        matched_skills=json.dumps(
            ai_result.get("strengths", [])
        ),
        missing_skills=json.dumps(
            ai_result.get("missing_skills", [])
        ),
        feedback=ai_result.get("summary", "")
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        "keyword_score": score_data["score"],
        "ai_analysis": ai_result
    }


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):

    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )

    return {
        "id": analysis.id,
        "resume_id": analysis.resume_id,
        "match_score": analysis.match_score,
        "matched_skills": json.loads(
            analysis.matched_skills or "[]"
        ),
        "missing_skills": json.loads(
            analysis.missing_skills or "[]"
        ),
        "feedback": analysis.feedback
    }
