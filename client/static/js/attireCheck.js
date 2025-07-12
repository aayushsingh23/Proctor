const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const captureBtn = document.getElementById('captureBtn');
const continueBtn = document.getElementById('continueBtn');
const resultEl = document.getElementById('attireResult');

// Start webcam stream
navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
    video.srcObject = stream;
}).catch(err => {
    alert("Camera access is required for attire check.");
});

// Capture and analyze attire
captureBtn.addEventListener('click', async () => {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/jpeg').split(',')[1];

    try {
        const response = await fetch('http://127.0.0.1:5000/attire_check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });

        const data = await response.json();
        if (data.is_formal) {
            resultEl.textContent = "✅ Formal attire detected. ";
            continueBtn.style.display = 'inline-block';
        } else {
            resultEl.textContent = "❌ Informal attire detected. ";
            continueBtn.style.display = 'inline-block';
        }
    } catch (error) {
        console.error("Error in attire check:", error);
        resultEl.textContent = "⚠️ Server error during attire check.";
    }
});

// Continue to proctoring
continueBtn.addEventListener('click', () => {
    window.location.href = '/proctoring';
});
