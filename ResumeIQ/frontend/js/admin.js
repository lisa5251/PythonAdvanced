
"use strict";

const API_URL = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

function redirectToLogin() {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
}

async function loadDashboard() {
    if (!token) {
        redirectToLogin();
        return;
    }

    const statusElement = document.getElementById("status");

    try {
        if (statusElement) {
            statusElement.textContent = "Loading dashboard...";
        }

        const response = await fetch(`${API_URL}/admin/stats`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.status === 401 || response.status === 403) {
            alert("Your session is invalid or you do not have admin access.");
            redirectToLogin();
            return;
        }

        if (!response.ok) {
            throw new Error(`Dashboard error: ${response.status}`);
        }

        const stats = await response.json();

        setText("totalUsers", stats.total_users);
        setText("totalResumes", stats.total_resumes);
        setText("totalAnalyses", stats.total_analyses);
        setText("averageScore", `${stats.average_score}%`);

        await loadUsers();

    } catch (error) {
        console.error("Dashboard error:", error);

        if (statusElement) {
            statusElement.textContent =
                "Unable to load dashboard. Check your backend connection.";
        }
    }
}

function setText(elementId, value) {
    const element = document.getElementById(elementId);

    if (element) {
        element.textContent = value ?? "--";
    }
}

async function loadUsers() {
    const response = await fetch(`${API_URL}/admin/users`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (response.status === 401 || response.status === 403) {
        redirectToLogin();
        return;
    }

    if (!response.ok) {
        throw new Error(`Users error: ${response.status}`);
    }

    const users = await response.json();

    const table = document.getElementById("usersTable");

    if (!table) {
        throw new Error("Users table not found in admin.html");
    }

    table.replaceChildren();

    users.forEach(user => {
        const row = document.createElement("tr");

        const values = [
            user.id,
            user.name,
            user.email,
            user.role,
            user.created_at
                ? new Date(user.created_at).toLocaleDateString()
                : "N/A"
        ];

        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        table.appendChild(row);
    });

    setText("status", `${users.length} registered users`);
}

// LOGOUT
const logoutButton = document.getElementById("logoutBtn");

if (logoutButton) {
    logoutButton.addEventListener("click", () => {
        redirectToLogin();
    });
}

// START DASHBOARD
loadDashboard();
