
document.addEventListener("DOMContentLoaded", () => {

    // DASHBOARD

    const resumeTable = document.getElementById("resumeTable");

    async function loadDashboard() {
        if (!resumeTable) return;

        try {
            const data = await apiRequest(API_ENDPOINTS.dashboard);

            const userName = document.getElementById("userName");
            const totalResumes = document.getElementById("totalResumes");
            const totalAnalyses = document.getElementById("totalAnalyses");
            const averageScore = document.getElementById("averageScore");

            const user = data.user || {};

            if (userName) {
                userName.textContent =
                    user.name || user.full_name || "User";
            }

            const stats = data.stats || data;

            if (totalResumes) {
                totalResumes.textContent =
                    stats.total_resumes ?? 0;
            }

            if (totalAnalyses) {
                totalAnalyses.textContent =
                    stats.total_analyses ?? 0;
            }

            if (averageScore) {
                averageScore.textContent =
                    stats.average_score != null
                    ? stats.average_score + "%"
                    : "--";
            }

            const resumes = data.resumes || data.recent_resumes || [];

            resumeTable.innerHTML = "";

            if (resumes.length === 0) {
                resumeTable.innerHTML =
                    '<tr><td colspan="4">No resumes uploaded yet. Start by uploading one!</td></tr>';
                return;
            }

            resumes.forEach(resume => {
                const row = document.createElement("tr");

                const name = document.createElement("td");
                name.textContent =
                    resume.filename || resume.file_name || "Resume";

                const date = document.createElement("td");
                date.textContent = resume.created_at
                    ? new Date(resume.created_at).toLocaleDateString()
                    : "--";

                const status = document.createElement("td");
                const badge = document.createElement("span");
                badge.className = "status-badge";
                badge.textContent = resume.status || "Uploaded";
                status.appendChild(badge);

                const score = document.createElement("td");
                score.textContent =
                    resume.score != null ? resume.score + "/100" : "--";

                row.append(name, date, status, score);

                if (resume.analysis_id || resume.id) {
                    row.style.cursor = "pointer";
                    row.addEventListener("click", () => {
                        const id = resume.analysis_id || resume.id;
                        localStorage.setItem("last_analysis_id", id);
                        window.location.href =
                            "results.html?id=" + encodeURIComponent(id);
                    });
                }

                resumeTable.appendChild(row);
            });

        } catch (error) {
            resumeTable.innerHTML =
                '<tr><td colspan="4">Could not load dashboard: ' +
                escapeHTML(error.message) + '</td></tr>';
        }
    }

    // ANALYSIS RESULTS

    async function loadResults() {
        const scoreElement = document.getElementById("resultScore");

        if (!scoreElement) return;

        const params = new URLSearchParams(window.location.search);

        const analysisId =
            params.get("id") ||
            localStorage.getItem("last_analysis_id");

        if (!analysisId) {
            document.getElementById("resultsMessage").textContent =
                "No analysis selected. Please upload a resume first.";
            return;
        }

        try {
            const data = await apiRequest(
                API_ENDPOINTS.analysis + "/" +
                encodeURIComponent(analysisId)
            );

            const analysis = data.analysis || data;

            const score =
                analysis.score ??
                analysis.total_score ??
                analysis.overall_score ??
                0;

            scoreElement.textContent = score;

            const circle = document.getElementById("resultScoreCircle");

            if (circle) {
                const safeScore = Math.max(0, Math.min(100, Number(score)));
                circle.style.background =
                    `conic-gradient(var(--primary) ${safeScore}%, #eeeafb 0)`;
            }

            document.getElementById("resultTitle").textContent =
                score >= 80 ? "Excellent Resume!" :
                score >= 60 ? "Good Progress!" :
                "Room for Improvement";

            document.getElementById("resultSummary").textContent =
                analysis.summary ||
                analysis.feedback ||
                "Your resume analysis is complete.";

            renderList(
                "strengthsList",
                analysis.strengths || []
            );

            renderList(
                "improvementsList",
                analysis.improvements ||
                analysis.suggestions || []
            );

            renderSkills(analysis.skills || []);

        } catch (error) {
            document.getElementById("resultsMessage").textContent =
                "Could not load results: " + error.message;
        }
    }

    function renderList(elementId, items) {
        const element = document.getElementById(elementId);

        if (!element) return;

        element.replaceChildren();

        if (!Array.isArray(items) || items.length === 0) {
            const li = document.createElement("li");
            li.textContent = "No information available.";
            element.appendChild(li);
            return;
        }

        items.forEach(item => {
            const li = document.createElement("li");
            li.textContent = typeof item === "string"
                ? item
                : item.description || item.name || JSON.stringify(item);

            element.appendChild(li);
        });
    }

    function renderSkills(skills) {
        const element = document.getElementById("skillsList");

        if (!element) return;

        element.replaceChildren();

        if (!Array.isArray(skills) || skills.length === 0) {
            element.textContent = "No skills information available.";
            return;
        }

        skills.forEach(skill => {
            const name = typeof skill === "string"
                ? skill
                : skill.name || skill.skill || "Skill";

            const percentage = typeof skill === "object"
                ? Math.max(0, Math.min(100, Number(skill.score ?? skill.percentage ?? 75)))
                : 75;

            const item = document.createElement("div");
            item.className = "skill-item";

            const heading = document.createElement("div");
            heading.className = "skill-heading";

            const label = document.createElement("span");
            label.textContent = name;

            const value = document.createElement("strong");
            value.textContent = percentage + "%";

            heading.append(label, value);

            const bar = document.createElement("div");
            bar.className = "skill-bar";

            const fill = document.createElement("span");
            fill.style.width = percentage + "%";

            bar.appendChild(fill);
            item.append(heading, bar);

            element.appendChild(item);
        });
    }

    function escapeHTML(value) {
        return String(value).replace(/[&<>"']/g, char => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[char]);
    }

    loadDashboard();
    loadResults();
});
