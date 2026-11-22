from app.services.scoring import (
    calculate_job_match,
    calculate_resume_score,
    calculate_score,
    extract_keywords,
)


def test_identical_text_scores_100():
    text = "Python FastAPI PostgreSQL Docker"
    assert calculate_score(text, text)["score"] == 100


def test_no_overlap_scores_0():
    result = calculate_score("Python developer", "Kubernetes terraform")
    assert result["score"] == 0
    assert "kubernetes" in result["missing"]


def test_empty_job_description():
    assert calculate_score("Python", "")["score"] == 0


def test_case_insensitive():
    assert calculate_score("PYTHON", "python")["score"] == 100


def test_trailing_period_ignored():
    assert "python" in extract_keywords("I know Python.")


def test_short_tech_terms_kept():
    assert "ai" in extract_keywords("AI and ML experience")


def test_stop_words_removed():
    assert "the" not in extract_keywords("the quick fox")


def test_job_match_lists_supported_matching_and_missing_skills():
    result = calculate_job_match(
        "Professional Summary\nPython developer",
        "Seeking experience with Python, Docker, and Kubernetes.",
    )
    assert result["job_match_percentage"] == 33
    assert result["matching_skills"] == ["Python"]
    assert result["missing_relevant_skills"] == ["Docker", "Kubernetes"]
    assert result["recommended_keywords"] == ["Docker", "Kubernetes"]


def test_no_job_description_has_no_match_score():
    result = calculate_job_match("Python developer", "")
    assert result["job_match_percentage"] is None
    assert result["missing_relevant_skills"] == []


def test_resume_score_uses_fixed_rubric_and_explains_each_category():
    result = calculate_resume_score(
        "Professional Summary\n"
        "Experienced engineer who developed software products for clients.\n"
        "Technical Skills\nPython\nDocker\n"
        "Work Experience\n2020-2024\n- Developed a service used by 100 customers.\n"
        "Education\nBachelor degree, 2019\n"
        "Projects\nProject portfolio improved speed by 20%.\n"
        "- Delivered a project\n- Built a service\n- Improved results"
    )
    assert result["overall_score"] == sum(
        category["points"] for category in result["score_breakdown"]
    )
    assert [category["max_points"] for category in result["score_breakdown"]] == [
        15, 25, 25, 10, 15, 10
    ]
    assert len(result["score_breakdown"]) == 6
    assert all(
        category["strengths"]
        and category["needs_improvement"] is not None
        and category["suggestions"] is not None
        for category in result["score_breakdown"]
    )
