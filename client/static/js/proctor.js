const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
canvas.width = 480;
canvas.height = 360;

const API_ENDPOINT = 'http://127.0.0.1:5000/analyze';

let keystrokeCount = 0;
let focusLostCount = 0;
let suspiciousKeysThisInterval = new Set();

// --- Task 1: Handle tab change (focus loss) ---
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.warn('FLAG: User switched tabs or minimized the window.');
        focusLostCount++;
    }
});

// --- Task 2: Clipboard Paste ---
document.addEventListener('paste', () => {
    suspiciousKeysThisInterval.add('paste-event');
    console.warn("📋 Paste event detected.");
});

// --- Task 3: Keystroke Monitoring ---
document.addEventListener('keydown', (e) => {
    keystrokeCount++;

    const isCtrl = e.ctrlKey || e.metaKey;
    const isAlt = e.altKey;
    const key = e.key.toLowerCase();

    if (isCtrl && key === 'c') suspiciousKeysThisInterval.add('ctrl+c');
    if (isCtrl && key === 'v') suspiciousKeysThisInterval.add('ctrl+v');
    if (isCtrl && key === 'x') suspiciousKeysThisInterval.add('ctrl+x');
    if (isCtrl && key === 'a') suspiciousKeysThisInterval.add('ctrl+a');
    if (isCtrl && key === 'tab') suspiciousKeysThisInterval.add('ctrl+tab');
    if (isAlt && key === 'tab') suspiciousKeysThisInterval.add('alt+tab');
    if (e.metaKey && key === 'tab') suspiciousKeysThisInterval.add('cmd+tab');
});

// --- Start Proctoring ---
async function startProctoring() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        alert("Camera access is required for proctoring.");
        return;
    }

    setInterval(async () => {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageBase64 = canvas.toDataURL('image/jpeg').split(',')[1];

        const requestData = {
            image: imageBase64,
            keystroke_count: keystrokeCount,
            focus_lost_count: focusLostCount,
            keystroke_map: Array.from(suspiciousKeysThisInterval)
        };

        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                console.error("API Error:", response.statusText);
                return;
            }

            const data = await response.json();
            console.log("API Response:", data);

            updateUI(data);
        } catch (error) {
            console.error("Failed to call analysis API:", error);
        }

        keystrokeCount = 0;
        focusLostCount = 0;
        suspiciousKeysThisInterval.clear();
    }, 4000);
}

function updateUI(data) {
    document.getElementById('faceDetected').textContent = data.face_detected ? "Yes" : "No";
    document.getElementById('peopleCount').textContent = data.people_count;
    document.getElementById('emotion').textContent = data.dominant_emotion || '-';

    if (data.head_pose) {
        const { yaw, pitch, roll } = data.head_pose;
        document.getElementById('headPose').textContent = data.head_orientation_readable;
    } else {
        document.getElementById('headPose').textContent = '-';
    }

    document.getElementById('flags').textContent = data.flags && data.flags.length > 0
        ? data.flags.join(', ')
        : 'None';

    document.getElementById('timestamp').textContent = new Date(data.timestamp).toLocaleTimeString();
}

startProctoring();

document.getElementById("endProctoringBtn").addEventListener("click", async () => {
    try {
        const response = await fetch("http://127.0.0.1:5000/end_proctoring", {
            method: "POST"
        });

        if (!response.ok) {
            console.error("Failed to end proctoring");
            return;
        }

        const result = await response.json();
        alert(result.message || "Proctoring session ended and logs saved.");
        window.location.reload();  // Optional: reset everything

    } catch (err) {
        console.error("Error ending proctoring session:", err);
    }
});
