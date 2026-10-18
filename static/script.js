const imageInput = document.getElementById("imageInput");
const uploadArea = document.getElementById("uploadArea");
const fileName = document.getElementById("fileName");
const previewContainer = document.getElementById("previewContainer");
const originalPreview = document.getElementById("originalPreview");
const enhanceButton = document.getElementById("enhanceButton");
const statusText = document.getElementById("status");
const results = document.getElementById("results");

let selectedFile = null;
let previewUrl = null;

imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    if (!file) return;

    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];

    if (!allowedTypes.includes(file.type)) {
        statusText.textContent = "Please select a JPG, PNG or WEBP image.";
        imageInput.value = "";
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        statusText.textContent = "Image must be smaller than 10 MB.";
        imageInput.value = "";
        return;
    }

    selectedFile = file;

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = URL.createObjectURL(file);

    originalPreview.src = previewUrl;
    previewContainer.classList.remove("hidden");
    fileName.textContent = file.name;
    statusText.textContent = "";
    results.classList.add("hidden");
});

uploadArea.addEventListener("dragover", (event) => {
    event.preventDefault();
    uploadArea.classList.add("dragging");
});

uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("dragging");
});

uploadArea.addEventListener("drop", (event) => {
    event.preventDefault();
    uploadArea.classList.remove("dragging");

    const file = event.dataTransfer.files[0];
    if (!file) return;

    const transfer = new DataTransfer();
    transfer.items.add(file);
    imageInput.files = transfer.files;
    imageInput.dispatchEvent(new Event("change"));
});

enhanceButton.addEventListener("click", async () => {
    if (!selectedFile) {
        statusText.textContent = "Please upload an image first.";
        return;
    }

    const method = document.querySelector(
        'input[name="method"]:checked'
    ).value;

    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("method", method);

    enhanceButton.disabled = true;
    statusText.textContent = "Enhancing image. Please wait...";
    results.classList.add("hidden");

    try {
        const response = await fetch("/enhance", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Enhancement failed.");
        }

        document.getElementById("originalResult").src =
            data.original + "?t=" + Date.now();

        document.getElementById("enhancedResult").src =
            data.enhanced + "?t=" + Date.now();

        document.getElementById("brightnessBefore").textContent =
            data.brightness_before;

        document.getElementById("brightnessAfter").textContent =
            data.brightness_after;

        document.getElementById("contrastBefore").textContent =
            data.contrast_before;

        document.getElementById("contrastAfter").textContent =
            data.contrast_after;

        document.getElementById("processingTime").textContent =
            data.processing_time + " sec";

        const downloadButton = document.getElementById("downloadButton");
        downloadButton.href = data.enhanced;
        downloadButton.download = "enhanced.png";

        results.classList.remove("hidden");
        statusText.textContent = "Enhancement completed successfully!";
        results.scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        statusText.textContent = error.message;
    } finally {
        enhanceButton.disabled = false;
    }
});