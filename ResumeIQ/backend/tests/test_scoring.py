from app.services.scoring import calculate_score, extract_keywords


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
    # currently fails: regex keeps the trailing dot
    assert "python" in extract_keywords("I know Python.")


def test_short_tech_terms_kept():
    # currently fails: len(word) > 2 drops these
    assert "ai" in extract_keywords("AI and ML experience")


def test_stop_words_removed():
    assert "the" not in extract_keywords("the quick fox")
