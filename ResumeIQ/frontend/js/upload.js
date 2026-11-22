
document.addEventListener("DOMContentLoaded", () => {

    const uploadForm = document.getElementById("uploadForm");

    if (!uploadForm) return;

    const fileInput = document.getElementById("resumeFile");
    const dropZone = document.getElementById("dropZone");
    const selectedFile = document.getElementById("selectedFile");
    const message = document.getElementById("uploadMessage");
    const analyzeButton = document.getElementById("analyzeButton");

    function showMessage(text, success = false) {
        message.textContent = text;
        message.className = success
            ? "message success"
            : "message";
    }

    function validateFile(file) {
        if (!file) return false;

        if (
            file.type !== "application/pdf" &&
            file.type !== "application/vnd.openxmlformats-officedocument.wordprocessingml.document" &&
            !file.name.toLowerCase().endsWith(".pdf") &&
            !file.name.toLowerCase().endsWith(".docx")
        ) {
            showMessage("Please select a PDF or DOCX file.");
            return false;
        }

        if (file.size > 5 * 1024 * 1024) {
            showMessage("The file must be no larger than 5 MB.");
            return false;
        }

        selectedFile.textContent = "Selected: " + file.name;
        showMessage("");

        return true;
    }

    fileInput.addEventListener("change", () => {
        validateFile(fileInput.files[0]);
    });

    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, event => {
            event.preventDefault();
            dropZone.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, event => {
            event.preventDefault();
            dropZone.classList.remove("dragover");
        });
    });

    dropZone.addEventListener("drop", event => {
        const file = event.dataTransfer.files[0];

        if (!file) return;

        const transfer = new DataTransfer();
        transfer.items.add(file);
        fileInput.files = transfer.files;

        validateFile(file);
    });

    uploadForm.addEventListener("submit", async event => {
        event.preventDefault();

        const file = fileInput.files[0];

        if (!validateFile(file)) return;

        const formData = new FormData();

        // Change "file" if your backend expects a different field name.
        formData.append("file", file);

        const jobDescription =
            document.getElementById("jobDescription").value.trim();

        let resumeUploaded = false;
        try {
            analyzeButton.disabled = true;
            analyzeButton.textContent = "Analyzing...";
            showMessage("Uploading your resume. Please wait...");

            const userId = getUserId();
            if (!userId) {
                throw new Error("Please log in again before uploading a resume.");
            }

            const uploadData = await apiRequest(
                `${API_ENDPOINTS.upload}?user_id=${encodeURIComponent(userId)}`,
                {
                    method: "POST",
                    body: formData
                }
            );
            resumeUploaded = true;

            showMessage("Resume uploaded. Building your detailed analysis...");
            const analysisData = await apiRequest(API_ENDPOINTS.createAnalysis, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    resume_id: uploadData.resume_id,
                    job_description: jobDescription
                })
            });

            if (analysisData.analysis_id) {
                localStorage.setItem("last_analysis_id", analysisData.analysis_id);

                window.location.href =
                    "results.html?id=" + encodeURIComponent(analysisData.analysis_id);
            } else {
                throw new Error("The server did not return an analysis ID.");
            }

        } catch (error) {
            showMessage(
                resumeUploaded
                    ? "Resume uploaded, but analysis could not be completed: " + error.message
                    : error.message
            );
            analyzeButton.disabled = false;
            analyzeButton.textContent = "Analyze My Resume →";
        }
    });
});
