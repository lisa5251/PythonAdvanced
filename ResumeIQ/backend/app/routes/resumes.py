
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resume import Resume
from app.services.pdf_service import extract_resume_text

router = APIRouter(prefix="/resumes", tags=["Resumes"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_resume(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    filename = file.filename or ""

    if not filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )

    content = await file.read()

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Maximum upload size is 5 MB"
        )

    try:
        extracted_text = extract_resume_text(
            filename,
            content
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found"
        )

    stored_name = (
        f"{uuid4().hex}{Path(filename).suffix.lower()}"
    )

    file_path = UPLOAD_DIR / stored_name
    file_path.write_bytes(content)

    resume = Resume(
        user_id=user_id,
        filename=filename,
        file_path=str(file_path),
        extracted_text=extracted_text
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "message": "Resume uploaded successfully",
        "resume_id": resume.id,
        "filename": resume.filename
    }


@router.get("/")
def get_resumes(
    user_id: int,
    db: Session = Depends(get_db)
):

    resumes = db.query(Resume).filter(
        Resume.user_id == user_id
    ).all()

    return [
        {
            "id": resume.id,
            "filename": resume.filename,
            "created_at": resume.created_at
        }
        for resume in resumes
    ]
