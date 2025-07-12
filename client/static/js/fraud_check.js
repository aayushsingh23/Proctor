const selfieVideo = document.getElementById("selfieVideo");
const canvas = document.getElementById("selfieCanvas");
const ctx = canvas.getContext("2d");
const captureBtn = document.getElementById("captureSelfieBtn");
const selfiePreview = document.getElementById("selfiePreview");

let capturedSelfie = null;
let hasCaptured = false;

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => selfieVideo.srcObject = stream)
    .catch(err => alert("Camera access denied"));

captureBtn.addEventListener("click", () => {
    if (!hasCaptured) {
        // Set canvas size to video size
        canvas.width = selfieVideo.videoWidth;
        canvas.height = selfieVideo.videoHeight;

        // Draw current frame
        ctx.drawImage(selfieVideo, 0, 0, canvas.width, canvas.height);
        capturedSelfie = canvas.toDataURL("image/jpeg").split(",")[1];

        // Show preview
        selfiePreview.src = "data:image/jpeg;base64," + capturedSelfie;
        hasCaptured = true;
        captureBtn.textContent = "Retake";
    } else {
        // Reset
        capturedSelfie = null;
        selfiePreview.src = "";
        hasCaptured = false;
        captureBtn.textContent = "Capture Selfie";
    }
});

document.getElementById("verifyBtn").addEventListener("click", async () => {
    const idInput = document.getElementById("idImageInput").files[0];
    if (!idInput || !capturedSelfie) {
        alert("Please upload ID and take a selfie");
        return;
    }

    const reader = new FileReader();
    reader.onloadend = async () => {
        const idBase64 = reader.result.split(",")[1];

        const res = await fetch("/verify_identity", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id_image: idBase64,
                selfie: capturedSelfie
            })
        });

        const data = await res.json();
        const resultText = data.verified
            ? `✅ Identity verified (distance: ${data.distance.toFixed(3)})`
            : `❌ Identity mismatch (distance: ${data.distance?.toFixed(3) || "N/A"})`;

        document.getElementById("result").textContent = resultText;

        if (data.verified) {
            document.getElementById("continueToProctoring").disabled = false;
            document.getElementById("continueToProctoring").classList.remove("btn-disabled");
        }
    };

    reader.readAsDataURL(idInput);
});

document.getElementById("continueToProctoring").addEventListener("click", () => {
    window.location.href = "/proctoring";
});

