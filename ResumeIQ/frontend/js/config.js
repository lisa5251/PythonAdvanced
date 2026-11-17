
const API_BASE_URL = "http://127.0.0.1:8000";

const API_ENDPOINTS = {
    register: "/auth/register",
    login: "/auth/login",
    upload: "/resumes/upload",
    resumes: "/resumes/",
    createAnalysis: "/analysis/create",
    analysis: "/analysis"
};

// Store the logged-in user's ID
function getUserId() {
    return localStorage.getItem("user_id");
}

// Common API request function
async function apiRequest(endpoint, options = {}) {
    const response = await fetch(API_BASE_URL + endpoint, {
        ...options,
        headers: {
            ...(options.headers || {})
        }
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            data.detail || data.message || "Something went wrong."
        );
    }

    return data;
}
