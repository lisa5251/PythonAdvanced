import re


SKILL_ALIASES = {
    "AWS": ("aws", "amazon web services"),
    "Azure": ("azure", "microsoft azure"),
    "C": ("c language",),
    "C#": ("c#", "c sharp"),
    "C++": ("c++", "cpp"),
    "CI/CD": ("ci/cd", "continuous integration", "continuous delivery"),
    "CSS": ("css",),
    "Cypress": ("cypress",),
    "Cybersecurity": ("cybersecurity", "information security"),
    "Data Science": ("data science",),
    "Deep Learning": ("deep learning",),
    "Django": ("django",),
    "Docker": ("docker",),
    "Express": ("express.js", "expressjs"),
    "Excel": ("excel", "microsoft excel"),
    "FastAPI": ("fastapi",),
    "Figma": ("figma",),
    "Flask": ("flask",),
    "Git": ("git", "github", "gitlab"),
    "Go": ("golang",),
    "Google Cloud": ("google cloud", "gcp"),
    "GraphQL": ("graphql",),
    "HTML": ("html",),
    "Java": ("java",),
    "JavaScript": ("javascript", "js"),
    "Jenkins": ("jenkins",),
    "Jest": ("jest",),
    "Jira": ("jira",),
    "Kafka": ("kafka",),
    "Kotlin": ("kotlin",),
    "Kubernetes": ("kubernetes", "k8s"),
    "Linux": ("linux",),
    "LLM": ("llm", "large language model"),
    "Machine Learning": ("machine learning",),
    "MongoDB": ("mongodb",),
    "Microsoft Office": ("microsoft office", "ms office"),
    "MySQL": ("mysql",),
    "Node.js": ("node.js", "nodejs"),
    "NumPy": ("numpy",),
    "NoSQL": ("nosql",),
    "Pandas": ("pandas",),
    "PHP": ("php",),
    "PostgreSQL": ("postgresql", "postgres"),
    "Power BI": ("power bi",),
    "PowerPoint": ("powerpoint",),
    "Problem Solving": ("problem solving", "problem-solving"),
    "Python": ("python",),
    "PyTorch": ("pytorch",),
    "R": ("r",),
    "React": ("react", "react.js", "reactjs"),
    "REST API": ("rest api", "restful api", "restful services"),
    "Redis": ("redis",),
    "Ruby": ("ruby",),
    "Ruby on Rails": ("ruby on rails", "rails"),
    "Rust": ("rust",),
    "Salesforce": ("salesforce",),
    "Selenium": ("selenium",),
    "SQL": ("sql",),
    "Scikit-learn": ("scikit-learn", "scikit learn"),
    "Stakeholder Management": ("stakeholder management",),
    "Spring": ("spring framework", "spring boot"),
    "Swift": ("swift",),
    "Tableau": ("tableau",),
    "Terraform": ("terraform",),
    "TensorFlow": ("tensorflow",),
    "Time Management": ("time management",),
    "TypeScript": ("typescript",),
    "Vue": ("vue", "vue.js", "vuejs"),
    "Word": ("microsoft word",),
    "Communication": ("communication", "communicate"),
    "Leadership": ("leadership", "team leadership"),
    "Project Management": ("project management",),
    "Agile": ("agile", "scrum"),
    "Data Analysis": ("data analysis", "data analytics"),
    "Customer Service": ("customer service", "client service"),
    "Angular": ("angular",),
    "Attention to Detail": ("attention to detail",),
    "Generative AI": ("generative ai",),
    "NLP": ("nlp", "natural language processing"),
    "Testing": ("testing", "test automation"),
}

STOP_WORDS = {
    "the", "and", "for", "with", "you", "your", "are", "was",
    "this", "that", "from", "have", "has", "will", "our", "their",
    "they", "who", "what", "when", "where", "how", "can", "all",
    "any", "not", "but", "into", "job", "work", "role", "team",
    "years", "year", "experience", "required", "preferred", "ability",
    "skills", "skill", "using", "use", "across", "including",
}

SECTION_HEADINGS = {
    "summary": ("summary", "professional summary", "profile", "career objective"),
    "skills": ("skills", "technical skills", "core skills", "technical expertise"),
    "experience": ("experience", "work experience", "employment", "professional experience"),
    "education": ("education", "academic background", "qualifications"),
    "projects": ("projects", "selected projects", "key projects", "achievements"),
}


def extract_keywords(text: str) -> set[str]:
    """Extract normalized words while retaining short technical terms."""
    words = re.findall(
        r"(?<![A-Za-z0-9])(?:[A-Za-z][A-Za-z0-9]*(?:[.+#-][A-Za-z0-9+#]+)*|[.+#]+)(?![A-Za-z0-9])",
        text.lower(),
    )
    normalized = {word.strip(".-") for word in words}
    return {
        word for word in normalized
        if word and word not in STOP_WORDS and (len(word) > 2 or word in {"ai", "ml", "r", "c"})
    }


def _contains_term(text: str, term: str) -> bool:
    pattern = r"(?<![A-Za-z0-9])" + re.escape(term).replace(r"\ ", r"\s+") + r"(?![A-Za-z0-9])"
    return re.search(pattern, text, re.IGNORECASE) is not None


def extract_skills(text: str) -> list[str]:
    """Find only skills from the supported vocabulary that occur in the text."""
    return sorted(
        (
            skill for skill, aliases in SKILL_ALIASES.items()
            if any(_contains_term(text, alias) for alias in aliases)
        ),
        key=str.casefold,
    )


def calculate_job_match(resume_text: str, job_description: str) -> dict:
    """Compare explicit job terms with terms actually found in the resume."""
    if not job_description.strip():
        return {
            "job_match_percentage": None,
            "matching_skills": [],
            "missing_relevant_skills": [],
            "recommended_keywords": [],
        }

    job_skills = extract_skills(job_description)
    if not job_skills:
        job_skills = sorted(extract_keywords(job_description))

    resume_text_lower = resume_text.lower()
    matching = [
        skill for skill in job_skills
        if any(_contains_term(resume_text_lower, alias) for alias in SKILL_ALIASES.get(skill, (skill,)))
    ]
    missing = [skill for skill in job_skills if skill not in matching]
    percentage = round(len(matching) / len(job_skills) * 100) if job_skills else 0

    return {
        "job_match_percentage": percentage,
        "matching_skills": matching,
        "missing_relevant_skills": missing,
        "recommended_keywords": missing.copy(),
    }


def _section_exists(text: str, section: str) -> bool:
    headings = SECTION_HEADINGS[section]
    for line in text.splitlines():
        candidate = re.sub(r"[\s:|•—-]+$", "", line.strip()).casefold()
        if candidate in headings:
            return True
    return False


def _section_text(text: str, section: str) -> str:
    lines = text.splitlines()
    headings = {
        heading
        for values in SECTION_HEADINGS.values()
        for heading in values
    }
    active = False
    content = []
    for line in lines:
        candidate = re.sub(r"[\s:|•—-]+$", "", line.strip()).casefold()
        if candidate in headings:
            if active:
                break
            active = candidate in SECTION_HEADINGS[section]
            continue
        if active:
            content.append(line)
    return "\n".join(content)


def _score_category(name: str, points: int, maximum: int, strengths: list[str], gaps: list[str], suggestions: list[str]) -> dict:
    return {
        "category": name,
        "points": min(points, maximum),
        "max_points": maximum,
        "strengths": strengths or ["No clear evidence for this category was found in the extracted resume text."],
        "needs_improvement": gaps,
        "suggestions": suggestions,
    }


def calculate_resume_score(resume_text: str) -> dict:
    """Score resume evidence against a fixed, explainable 100-point rubric."""
    text = resume_text or ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    skills = extract_skills(text)
    has_bullets = sum(line.startswith(("-", "•", "*", "·")) for line in lines)
    action_words = (
        "developed", "built", "managed", "led", "created", "improved",
        "designed", "delivered", "implemented", "increased", "reduced",
        "analyzed", "supported", "achieved",
    )

    summary_section = _section_exists(text, "summary")
    summary_text = _section_text(text, "summary")
    summary_lower = summary_text.lower()
    summary_points = (5 if summary_section else 0)
    summary_points += 5 if len(summary_text) >= 120 else 3 if len(summary_text) >= 50 else 0
    summary_points += 5 if any(word in summary_lower for word in action_words) else 0
    categories = [
        _score_category(
            "Professional Summary",
            summary_points,
            15,
            ["A clearly labeled professional summary is present."] if summary_section else [],
            [] if summary_points == 15 else ["The summary is missing or does not yet show enough role-specific detail."],
            [] if summary_points == 15 else ["Add a concise 2–4 line profile with your target role, strongest relevant capabilities, and a supported accomplishment."],
        )
    ]

    skills_section = _section_exists(text, "skills")
    skills_points = (8 if skills_section else 0)
    skills_points += 12 if len(skills) >= 8 else 9 if len(skills) >= 5 else 6 if len(skills) >= 2 else 3 if skills else 0
    skills_points += 5 if skills_section and len(_section_text(text, "skills").splitlines()) >= 2 else 0
    categories.append(_score_category(
        "Technical and Relevant Skills",
        skills_points,
        25,
        [f"Skills identified in the resume include {', '.join(skills[:8])}."] if skills else [],
        [] if skills_points == 25 else ["The resume has limited clearly identified skills or could organize them more clearly."],
        [] if skills_points == 25 else ["Add a concise skills section with tools and competencies you can substantiate; tailor it to each role."],
    ))

    experience_section = _section_exists(text, "experience")
    experience_text = _section_text(text, "experience")
    experience_lower = experience_text.lower()
    experience_points = (8 if experience_section else 0)
    experience_points += 5 if re.search(r"\b(?:19|20)\d{2}\b", experience_text) else 0
    experience_points += 6 if any(word in experience_lower for word in action_words) else 0
    experience_points += 6 if re.search(r"\b\d+(?:[.,]\d+)?%?\b", experience_text) else 0
    categories.append(_score_category(
        "Work Experience",
        experience_points,
        25,
        ["A work-experience section is present."] if experience_section else [],
        [] if experience_points == 25 else ["Role dates, action-led descriptions, or measurable outcomes are missing or unclear."],
        [] if experience_points == 25 else ["For each role, add dates and 2–4 action-led bullets describing your own work and measurable results where available."],
    ))

    education_section = _section_exists(text, "education")
    education_text = _section_text(text, "education").lower()
    education_points = (6 if education_section else 0)
    education_points += 2 if re.search(
        r"\b(bachelor|master|associate|ph\.?d|degree|diploma|certificate|bsc|msc|ba|bs)\b",
        education_text,
    ) else 0
    education_points += 2 if re.search(r"\b(?:19|20)\d{2}\b", education_text) else 0
    categories.append(_score_category(
        "Education",
        education_points,
        10,
        ["An education section is present."] if education_section else [],
        [] if education_points == 10 else ["Education details or qualification dates could be clearer."],
        [] if education_points == 10 else ["List relevant qualifications, institutions, and completion dates; include only credentials you have earned."],
    ))

    projects_section = _section_exists(text, "projects")
    projects_text = _section_text(text, "projects").lower()
    projects_points = (6 if projects_section else 0)
    projects_points += 4 if re.search(r"\b(project|portfolio|prototype)\b", projects_text) else 0
    projects_points += 5 if re.search(r"\b\d+(?:[.,]\d+)?%?\b", projects_text) else 0
    categories.append(_score_category(
        "Projects and Achievements",
        projects_points,
        15,
        ["A projects or achievements section is present."] if projects_section else [],
        [] if projects_points == 15 else ["Projects or concrete achievements are missing or lack evidence of impact."],
        [] if projects_points == 15 else ["Add relevant projects or verified achievements and explain your contribution, tools, and outcome."],
    ))

    headings_count = sum(_section_exists(text, section) for section in SECTION_HEADINGS)
    formatting_points = 0
    formatting_points += 4 if headings_count >= 4 else 3 if headings_count >= 2 else 0
    formatting_points += 3 if len(lines) >= 8 and len(text) >= 300 else 1 if len(lines) >= 4 else 0
    formatting_points += 3 if has_bullets >= 3 else 1 if has_bullets else 0
    categories.append(_score_category(
        "Formatting and Readability",
        formatting_points,
        10,
        [f"The resume contains {headings_count} recognizable section headings and {len(lines)} non-empty lines."] if lines else [],
        [] if formatting_points == 10 else ["The extracted text suggests the structure or use of concise bullets could be improved."],
        [] if formatting_points == 10 else ["Use consistent section headings, readable spacing, and concise bullet points; verify the PDF text is in a logical reading order."],
    ))

    total_score = sum(category["points"] for category in categories)
    strengths = [
        detail
        for category in categories
        for detail in category["strengths"]
        if not detail.startswith("No clear evidence")
    ]
    improvements = [
        suggestion
        for category in categories
        for suggestion in category["suggestions"]
    ]

    return {
        "overall_score": total_score,
        "score_breakdown": categories,
        "strengths": strengths,
        "areas_to_improve": [
            category["needs_improvement"][0]
            for category in categories
            if category["needs_improvement"]
        ],
        "improvements": improvements,
        "skills_found": skills,
    }


def calculate_score(resume_text: str, job_description: str) -> dict:
    """Backward-compatible keyword comparison used by older callers."""
    result = calculate_job_match(resume_text, job_description)
    return {
        "score": result["job_match_percentage"] or 0,
        "matched": [skill.lower() for skill in result["matching_skills"]],
        "missing": [skill.lower() for skill in result["missing_relevant_skills"]],
    }
