
document.addEventListener("DOMContentLoaded", () => {

    const protectedPages = [
        "dashboard.html",
        "upload.html",
        "results.html"
    ];

    const currentPage = window.location.pathname
        .split("/")
        .pop();

    // Protect dashboard pages
    if (
        protectedPages.includes(currentPage) &&
        !getUserId()
    ) {
        window.location.href = "login.html";
        return;
    }

    // Logout
    const logoutButton = document.getElementById("logoutButton");

    if (logoutButton) {
        logoutButton.addEventListener("click", (event) => {
            event.preventDefault();

            localStorage.removeItem("user_id");
            localStorage.removeItem("last_analysis_id");
            localStorage.removeItem("last_resume_id");

            window.location.href = "index.html";
        });
    }

});
