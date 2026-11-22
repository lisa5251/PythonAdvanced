
document.addEventListener("DOMContentLoaded", () => {

    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const message = document.getElementById("authMessage");

    function showMessage(text, success = false) {
        if (!message) return;

        message.textContent = text;
        message.className = success
            ? "message success"
            : "message";
    }

    // LOGIN
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const email = document.getElementById("loginEmail").value.trim();
            const password = document.getElementById("loginPassword").value;

            try {
                showMessage("Logging in...");

                const data = await apiRequest(API_ENDPOINTS.login, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });

                if (!data.user_id || !data.access_token) {
                    throw new Error("The server did not return a valid login session.");
                }

                localStorage.setItem("user_id", data.user_id);
                localStorage.setItem("access_token", data.access_token);

                showMessage("Login successful!", true);

                window.location.href = "dashboard.html";

            } catch (error) {
                showMessage(error.message);
            }
        });
    }

    // REGISTER
    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const name = document.getElementById("registerName").value.trim();
            const email = document.getElementById("registerEmail").value.trim();
            const password = document.getElementById("registerPassword").value;

            if (password.length < 12) {
                showMessage("Password must contain at least 12 characters.");
                return;
            }

            try {
                showMessage("Creating your account...");

                const data = await apiRequest(API_ENDPOINTS.register, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        name: name,
                        email: email,
                        password: password
                    })
                });

                showMessage(
                    data.message || "Registration successful!",
                    true
                );

                registerForm.reset();

                setTimeout(() => {
                    window.location.href = "login.html";
                }, 1200);

            } catch (error) {
                showMessage(error.message);
            }
        });
    }

});
