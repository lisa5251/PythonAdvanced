
const API_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/admin/stats`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.status === 401 || response.status === 403) {
            localStorage.removeItem("access_token");
            alert("You are not authorized to access this page.");
            window.location.href = "login.html";
            return;
        }

        if (!response.ok) {
            throw new Error("Could not load dashboard statistics");
        }

        const stats = await response.json();

        document.getElementById("totalUsers").textContent =
            stats.total_users;

        document.getElementById("totalResumes").textContent =
            stats.total_resumes;

        document.getElementById("totalAnalyses").textContent =
            stats.total_analyses;

        document.getElementById("averageScore").textContent =
            stats.average_score + "%";

        await loadUsers();

    } catch (error) {
        document.getElementById("status").textContent =
            "Error: " + error.message;
    }
}

async function loadUsers() {
    const response = await fetch(`${API_URL}/admin/users`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        throw new Error("Could not load users");
    }

    const users = await response.json();

    const table = document.getElementById("usersTable");

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

    document.getElementById("status").textContent =
        `${users.length} registered users`;
}

document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
});

loadDashboard();

