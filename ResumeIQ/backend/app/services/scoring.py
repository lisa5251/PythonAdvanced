
import re


def extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text."""

    words = re.findall(
        r"[a-zA-Z][a-zA-Z+#.]*",
        text.lower()
    )

    stop_words = {
        "the", "and", "for", "with", "you",
        "your", "are", "was", "this", "that",
        "from", "have", "has", "will", "our",
        "their", "they", "who", "what", "when",
        "where", "how", "can", "all", "any",
        "not", "but", "into", "job", "work"
    }

    return {
        word for word in words
        if len(word) > 2 and word not in stop_words
    }


def calculate_score(
    resume_text: str,
    job_description: str
) -> dict:
    """Compare resume keywords with job requirements."""

    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    if not job_keywords:
        return {
            "score": 0,
            "matched": [],
            "missing": []
        }

    matched = sorted(
        resume_keywords.intersection(job_keywords)
    )

    missing = sorted(
        job_keywords - resume_keywords
    )

    score = round(
        len(matched) / len(job_keywords) * 100,
        2
    )

    return {
        "score": score,
        "matched": matched,
        "missing": missing
    }
