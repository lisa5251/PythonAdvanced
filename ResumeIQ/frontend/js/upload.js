
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
            !file.name.toLowerCase().endsWith(".pdf")
        ) {
            showMessage("Please select a PDF file.");
            return false;
        }

        if (file.size > 10 * 1024 * 1024) {
            showMessage("The file must be smaller than 10 MB.");
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

        if (jobDescription) {
            formData.append("job_description", jobDescription);
        }

        try {
            analyzeButton.disabled = true;
            analyzeButton.textContent = "Analyzing...";
            showMessage("Uploading your resume. Please wait...");

            const data = await apiRequest(API_ENDPOINTS.upload, {
                method: "POST",
                body: formData
            });

            const analysisId =
                data.analysis_id ??
                data.analysis?.id ??
                data.id;

            if (analysisId) {
                localStorage.setItem("last_analysis_id", analysisId);

                window.location.href =
                    "results.html?id=" + encodeURIComponent(analysisId);
            } else {
                showMessage(
                    "Upload completed, but no analysis ID was returned. Check your dashboard.",
                    true
                );
                analyzeButton.disabled = false;
                analyzeButton.textContent = "Analyze My Resume →";
            }

        } catch (error) {
            showMessage(error.message);
            analyzeButton.disabled = false;
            analyzeButton.textContent = "Analyze My Resume →";
        }
    });
});
