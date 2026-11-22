from io import BytesIO

import pymupdf
import pytest
from docx import Document
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db
from app.models.user import User
from app.routes import analysis, dashboard, resumes
from app.services.ai_service import AIConfigurationError, AIServiceError


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = test_session()
    session.add(User(name="Test User", email="test@example.com", password_hash="hash"))
    session.commit()
    user_id = session.query(User).first().id
    session.close()

    monkeypatch.setattr(resumes, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(
        analysis,
        "analyze_resume",
        lambda resume_text, job_description: {
            "summary": "Evidence-based test summary.",
            "strengths": ["Python is listed in the resume."],
            "recommendations": ["Describe a measurable result from your work."],
        },
    )

    test_app = FastAPI()
    test_app.include_router(resumes.router)
    test_app.include_router(analysis.router)
    test_app.include_router(dashboard.router)

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides[get_db] = override_get_db
    with TestClient(test_app) as test_client:
        yield test_client, user_id

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def make_resume_pdf():
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Professional Summary\n"
        "Experienced engineer who developed useful software products.\n"
        "Technical Skills\nPython\n"
        "Work Experience\n2020-2024\n- Developed services for 100 users.\n"
        "Education\nBachelor degree, 2019\n"
        "Projects\n- Built an application",
    )
    content = document.tobytes()
    document.close()
    return content


def make_resume_docx():
    document = Document()
    document.add_heading("Professional Summary", level=1)
    document.add_paragraph("Experienced engineer who developed software products.")
    document.add_heading("Technical Skills", level=1)
    document.add_paragraph("Python, Docker")
    output = BytesIO()
    document.save(output)
    return output.getvalue()


def test_upload_general_and_job_matched_analysis_and_dashboard(client):
    test_client, user_id = client
    upload_response = test_client.post(
        f"/resumes/upload?user_id={user_id}",
        files={"file": ("resume.pdf", make_resume_pdf(), "application/pdf")},
    )
    assert upload_response.status_code == 200
    resume_id = upload_response.json()["resume_id"]

    general_response = test_client.post(
        "/analysis/create",
        json={"resume_id": resume_id},
    )
    assert general_response.status_code == 200
    general = general_response.json()
    assert general["has_job_description"] is False
    assert general["job_match_percentage"] is None
    assert sum(item["max_points"] for item in general["score_breakdown"]) == 100
    assert general["overall_score"] == sum(
        item["points"] for item in general["score_breakdown"]
    )
    assert general["ai_recommendations"] == [
        "Describe a measurable result from your work."
    ]

    matched_response = test_client.post(
        "/analysis/create",
        json={
            "resume_id": resume_id,
            "job_description": "Looking for Python and Docker experience.",
        },
    )
    assert matched_response.status_code == 200
    matched = matched_response.json()
    assert matched["has_job_description"] is True
    assert matched["matching_skills"] == ["Python"]
    assert matched["missing_relevant_skills"] == ["Docker"]
    assert matched["job_match_percentage"] == 50

    result_response = test_client.get(f"/analysis/{matched['analysis_id']}")
    assert result_response.status_code == 200
    assert result_response.json()["overall_score"] == matched["overall_score"]

    dashboard_data = test_client.get(
        f"/dashboard/stats?user_id={user_id}"
    ).json()
    assert dashboard_data["total_resumes"] == 1
    assert dashboard_data["total_analyses"] == 2
    assert dashboard_data["average_score"] == matched["overall_score"]
    assert dashboard_data["recent_resumes"][0]["status"] == "Analyzed"
    assert dashboard_data["recent_resumes"][0]["score"] == matched["overall_score"]


def test_upload_and_analyze_docx_resume(client):
    test_client, user_id = client
    upload_response = test_client.post(
        f"/resumes/upload?user_id={user_id}",
        files={
            "file": (
                "resume.docx",
                make_resume_docx(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert upload_response.status_code == 200

    analysis_response = test_client.post(
        "/analysis/create",
        json={"resume_id": upload_response.json()["resume_id"]},
    )
    assert analysis_response.status_code == 200
    assert analysis_response.json()["skills_found"] == ["Docker", "Python"]


def test_analysis_reports_when_ai_key_is_not_configured(client, monkeypatch):
    test_client, user_id = client
    upload_response = test_client.post(
        f"/resumes/upload?user_id={user_id}",
        files={"file": ("resume.pdf", make_resume_pdf(), "application/pdf")},
    )

    def report_unavailable(resume_text, job_description):
        raise AIConfigurationError(
            "AI recommendations are unavailable because OPENAI_API_KEY is not configured."
        )

    monkeypatch.setattr(
        analysis,
        "analyze_resume",
        report_unavailable,
    )

    response = test_client.post(
        "/analysis/create",
        json={"resume_id": upload_response.json()["resume_id"]},
    )
    assert response.status_code == 200
    assert response.json()["ai_recommendations_available"] is False
    assert "OPENAI_API_KEY" in response.json()["ai_notice"]


def test_invalid_ai_key_does_not_block_resume_score(client, monkeypatch):
    test_client, user_id = client
    upload_response = test_client.post(
        f"/resumes/upload?user_id={user_id}",
        files={"file": ("resume.pdf", make_resume_pdf(), "application/pdf")},
    )

    def reject_key(resume_text, job_description):
        raise AIServiceError(
            "OpenAI rejected the API key (HTTP 401). Check OPENAI_API_KEY in the backend .env file."
        )

    monkeypatch.setattr(analysis, "analyze_resume", reject_key)
    response = test_client.post(
        "/analysis/create",
        json={"resume_id": upload_response.json()["resume_id"]},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["overall_score"] > 0
    assert result["ai_recommendations_available"] is False
    assert "HTTP 401" in result["ai_notice"]
    assert "until OPENAI_API_KEY is configured" not in result["summary"]
    saved = test_client.get(f"/analysis/{result['analysis_id']}").json()
    assert saved["overall_score"] == result["overall_score"]


def test_upload_rejects_invalid_pdf(client):
    test_client, user_id = client
    response = test_client.post(
        f"/resumes/upload?user_id={user_id}",
        files={"file": ("resume.pdf", b"not a PDF", "application/pdf")},
    )
    assert response.status_code == 400
    assert "invalid or unreadable" in response.json()["detail"]
