
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
canvas.width = 480;
canvas.height = 360;

const API_ENDPOINT = 'http://127.0.0.1:5000/analyze';

let keystrokeCount = 0;
let focusLostCount = 0;

// --- Task 1: Handling Browser Change (Focus Loss) ---
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.warn('FLAG: User switched tabs or minimized the window.');
        focusLostCount++;
    }
});

// --- Task 2: Keystroke Counting ---
let suspiciousKeysThisInterval = new Set();

document.addEventListener('keydown', (e) => {
    keystrokeCount++;

    const isCtrl = e.ctrlKey || e.metaKey;  // Ctrl for Windows/Linux, Cmd for macOS
    const isAlt = e.altKey;

    const key = e.key.toLowerCase();

    // Handle common cheating patterns
    if (isCtrl && key === 'c') suspiciousKeysThisInterval.add('ctrl+c');
    if (isCtrl && key === 'v') suspiciousKeysThisInterval.add('ctrl+v');
    if (isCtrl && key === 'x') suspiciousKeysThisInterval.add('ctrl+x');
    if (isCtrl && key === 'a') suspiciousKeysThisInterval.add('ctrl+a');
    if (isCtrl && key === 'tab') suspiciousKeysThisInterval.add('ctrl+tab');
    if (isAlt && key === 'tab') suspiciousKeysThisInterval.add('alt+tab');
    if (e.metaKey && key === 'tab') suspiciousKeysThisInterval.add('cmd+tab');  // macOS
});

// --- Main Data Capture and API Call Loop ---
async function startProctoring() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Camera access denied.", err);
        alert("Camera access is required for proctoring.");
        return;
    }

    // Every 3 seconds, capture data and call the API
    setInterval(async () => {
        // 1. Capture video frame
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageBase64 = canvas.toDataURL('image/jpeg').split(',')[1];

        // 2. Prepare the data packet
        const requestData = {
            image: imageBase64,
            keystroke_count: keystrokeCount,
            focus_lost_count: focusLostCount,
            keystroke_map: Array.from(suspiciousKeysThisInterval)
        };

        // 3. Call the API
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

            const analysisResult = await response.json();
            console.log("API Response:", analysisResult);

            // The client is responsible for storing these results

        } catch (error) {
            console.error("Failed to call analysis API:", error);
        }

        // 4. Reset periodic counters
        keystrokeCount = 0;
        focusLostCount = 0;

    }, 3000);
}

startProctoring();