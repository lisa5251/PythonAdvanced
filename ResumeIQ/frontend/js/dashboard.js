document.addEventListener("DOMContentLoaded", () => {
    const resumeTable = document.getElementById("resumeTable");

    async function loadDashboard() {
        if (!resumeTable) return;

        try {
            const userId = getUserId();
            const data = await apiRequest(
                `${API_ENDPOINTS.dashboard}?user_id=${encodeURIComponent(userId)}`
            );

            const totalResumes = document.getElementById("totalResumes");
            const totalAnalyses = document.getElementById("totalAnalyses");
            const averageScore = document.getElementById("averageScore");

            if (totalResumes) totalResumes.textContent = data.total_resumes;
            if (totalAnalyses) totalAnalyses.textContent = data.total_analyses;
            if (averageScore) {
                averageScore.textContent = data.average_score == null
                    ? "--"
                    : `${data.average_score}%`;
            }

            renderRecentResumes(data.recent_resumes || []);
        } catch (error) {
            resumeTable.replaceChildren();
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.colSpan = 4;
            cell.textContent = `Could not load dashboard: ${error.message}`;
            row.appendChild(cell);
            resumeTable.appendChild(row);
        }
    }

    function renderRecentResumes(resumes) {
        resumeTable.replaceChildren();

        if (resumes.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");
            cell.colSpan = 4;
            cell.textContent = "No resumes uploaded yet. Start by uploading one!";
            row.appendChild(cell);
            resumeTable.appendChild(row);
            return;
        }

        resumes.forEach(resume => {
            const row = document.createElement("tr");
            const values = [
                resume.filename || "Resume",
                resume.created_at
                    ? new Date(resume.created_at).toLocaleDateString()
                    : "--",
                resume.status || "Uploaded",
                resume.score == null ? "--" : `${resume.score}/100`
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            if (resume.analysis_id) {
                row.tabIndex = 0;
                row.setAttribute("role", "link");
                row.style.cursor = "pointer";
                row.addEventListener("click", () => openAnalysis(resume.analysis_id));
                row.addEventListener("keydown", event => {
                    if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        openAnalysis(resume.analysis_id);
                    }
                });
            }
            resumeTable.appendChild(row);
        });
    }

    function openAnalysis(analysisId) {
        localStorage.setItem("last_analysis_id", analysisId);
        window.location.href = `results.html?id=${encodeURIComponent(analysisId)}`;
    }

    async function loadResults() {
        const scoreElement = document.getElementById("resultScore");
        if (!scoreElement) return;

        const analysisId = new URLSearchParams(window.location.search).get("id")
            || localStorage.getItem("last_analysis_id");
        if (!analysisId) {
            document.getElementById("resultsMessage").textContent =
                "No analysis selected. Please upload a resume first.";
            return;
        }

        try {
            const analysis = await apiRequest(
                `${API_ENDPOINTS.analysis}/${encodeURIComponent(analysisId)}`
            );
            renderResults(analysis);
        } catch (error) {
            document.getElementById("resultsMessage").textContent =
                `Could not load results: ${error.message}`;
        }
    }

    function renderResults(analysis) {
        const score = Number(analysis.overall_score ?? analysis.match_score ?? 0);
        document.getElementById("resultScore").textContent = score;

        const scoreCircle = document.getElementById("resultScoreCircle");
        const safeScore = Math.max(0, Math.min(100, score));
        scoreCircle.style.background =
            `conic-gradient(var(--primary) ${safeScore}%, #eeeafb 0)`;

        document.getElementById("resultTitle").textContent =
            score >= 80 ? "Excellent Resume!" :
            score >= 60 ? "Good Progress!" :
            "Room for Improvement";
        document.getElementById("resultSummary").textContent =
            analysis.summary || "Your resume analysis is complete.";

        renderBreakdown(analysis.score_breakdown || []);
        renderList("strengthsList", analysis.strengths || []);
        renderList(
            "improvementsList",
            analysis.areas_to_improve || analysis.improvements || []
        );
        renderSkillTags("skillsList", analysis.skills_found || []);

        const aiNotice = document.getElementById("aiNotice");
        aiNotice.textContent = analysis.ai_recommendations_available
            ? "Suggestions are generated from the resume text and should be checked for accuracy."
            : (analysis.ai_notice || "AI-generated recommendations are unavailable for this analysis.");
        renderList(
            "aiRecommendations",
            analysis.ai_recommendations || [],
            analysis.ai_recommendations_available
                ? "No additional AI recommendations were returned."
                : "No AI recommendations are available for this analysis. See the message above; your score and rubric-based suggestions are still available."
        );

        if (analysis.has_job_description && analysis.job_match_percentage != null) {
            document.getElementById("jobMatchCard").hidden = false;
            document.getElementById("jobSkillsPanel").hidden = false;
            const matchScore = Math.max(
                0,
                Math.min(100, Number(analysis.job_match_percentage))
            );
            document.getElementById("jobMatchScore").textContent = matchScore;
            document.getElementById("jobMatchProgress").style.width = `${matchScore}%`;
            renderSkillTags("matchingSkills", analysis.matching_skills || []);
            renderSkillTags("missingSkills", analysis.missing_relevant_skills || []);
            renderSkillTags("recommendedKeywords", analysis.recommended_keywords || []);
        }
    }

    function renderBreakdown(categories) {
        const container = document.getElementById("scoreBreakdown");
        container.replaceChildren();

        categories.forEach(category => {
            const card = document.createElement("article");
            card.className = "score-category";

            const heading = document.createElement("div");
            heading.className = "score-category-heading";
            const title = document.createElement("span");
            title.className = "score-category-title";
            title.textContent = category.category;
            const points = document.createElement("strong");
            points.textContent = `${category.points}/${category.max_points}`;
            heading.append(title, points);
            card.appendChild(heading);

            const progress = document.createElement("div");
            progress.className = "progress";
            const fill = document.createElement("span");
            const percent = category.max_points
                ? (category.points / category.max_points) * 100
                : 0;
            fill.style.width = `${percent}%`;
            progress.appendChild(fill);
            card.appendChild(progress);

            appendCategoryDetails(card, "What you did well", category.strengths);
            appendCategoryDetails(card, "Needs improvement", category.needs_improvement);
            appendCategoryDetails(card, "Suggestions", category.suggestions);
            container.appendChild(card);
        });

        if (categories.length === 0) {
            container.textContent = "Detailed scoring information is unavailable.";
        }
    }

    function appendCategoryDetails(container, headingText, items) {
        const heading = document.createElement("h4");
        heading.textContent = headingText;
        const list = document.createElement("ul");
        const details = items && items.length
            ? items
            : [headingText === "Needs improvement"
                ? "No major gaps were identified in this category."
                : "No additional suggestions for this category."];
        details.forEach(item => {
            const entry = document.createElement("li");
            entry.textContent = item;
            list.appendChild(entry);
        });
        container.append(heading, list);
    }

    function renderList(elementId, items, emptyMessage = "No items to show.") {
        const element = document.getElementById(elementId);
        element.replaceChildren();

        if (items.length === 0) {
            const empty = document.createElement("li");
            empty.textContent = emptyMessage;
            element.appendChild(empty);
            return;
        }

        items.forEach(item => {
            const entry = document.createElement("li");
            entry.textContent = item;
            element.appendChild(entry);
        });
    }

    function renderSkillTags(elementId, skills) {
        const element = document.getElementById(elementId);
        element.replaceChildren();

        if (skills.length === 0) {
            element.textContent = "None identified in the extracted text.";
            return;
        }

        skills.forEach(skill => {
            const tag = document.createElement("span");
            tag.className = "skill-tag";
            tag.textContent = skill;
            element.appendChild(tag);
        });
    }

    loadDashboard();
    loadResults();
    window.addEventListener("pageshow", event => {
        if (event.persisted) loadDashboard();
    });
});
