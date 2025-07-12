let video = document.getElementById("videoPreview");
let canvas = document.getElementById("captureCanvas");
let ctx = canvas.getContext("2d");
let countdownDisplay = document.getElementById("countdown");
let capturedImageBase64 = null;
let isCaptured = false;
let captureBtn = null;
let continueBtn = null;

window.onload = () => {
    captureBtn = document.getElementById("captureBtn");
    continueBtn = document.getElementById("continueBtn");

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => video.srcObject = stream)
        .catch(err => alert("Unable to access camera: " + err));
};

function startCapture() {
    if (isCaptured) {
        // Retake logic
        capturedImageBase64 = null;
        isCaptured = false;
        document.getElementById("capturedPreview").src = "";
        captureBtn.textContent = "Capture";
        continueBtn.classList.add("btn-disabled");
        continueBtn.disabled = true;
        return;
    }

    // Start countdown
    let countdown = 3;
    countdownDisplay.textContent = `Capturing in ${countdown}...`;

    const timer = setInterval(() => {
        countdown--;
        if (countdown > 0) {
            countdownDisplay.textContent = `Capturing in ${countdown}...`;
        } else {
            clearInterval(timer);
            countdownDisplay.textContent = "";
            capturePhoto();
        }
    }, 1000);
}

function capturePhoto() {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    capturedImageBase64 = canvas.toDataURL("image/jpeg").split(",")[1];

    document.getElementById("capturedPreview").src = "data:image/jpeg;base64," + capturedImageBase64;

    // Enable "Continue"
    continueBtn.classList.remove("btn-disabled");
    continueBtn.disabled = false;

    // Change Capture to Retake
    captureBtn.textContent = "Retake";
    isCaptured = true;
}

function goBack() {
    window.location.href = "/";
}

function continueToNext() {
    if (!capturedImageBase64) return;

    fetch("/attire_check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: capturedImageBase64 })
    })
        .then(res => res.json())
        .then(data => {
            if (data?.is_formal?.dress_code) {
                alert(`Dress Code Detected: ${data.is_formal.dress_code.toUpperCase()}`);
                window.location.href = "/fraud_check";
            } else {
                alert("Failed to detect attire. Try again.");
            }
        })
        .catch(err => {
            console.error(err);
            alert("Error while analyzing attire.");
        });
}
