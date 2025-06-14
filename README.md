
# Real-Time Behavioral Monitoring System    
## Project Goal

This project is a real-time behavioral monitoring system built using a Flask backend and a client-side HTML/JavaScript interface. It captures webcam video, microphone audio, and keystroke metadata, processes them using AI models, and generates structured JSON reports every 10 seconds.

---
## Core Features

- **Eye Movement Detection**  
  Uses `dlib` and `OpenCV` for gaze direction and blink detection.

- **Facial Expression Recognition**  
  Uses the `FER` library to identify dominant emotions and confidence scores.

- **Head Pose Estimation**  
  Uses `dlib` and `OpenCV` to track pitch, yaw, and roll.

- **Hand Pose & Movement Tracking**  
  Uses `MediaPipe` for real-time hand landmark tracking and gesture recognition.

- **Keystroke Logging**  
  Captures user input metadata using JavaScript key event listeners.

- **Surrounding Analysis**  
  Uses OpenCV’s DNN module with YOLOv8 for people detection and prohibited objects in the background.

- **Voice Cue Monitoring**  
  Captures and analyzes voice input via Web Audio API and `librosa` to determine speech presence and volume.

- **Browser Activity Tracking**  
  - Detects tab or window switching using the Page Visibility API.
  - Detects copy/paste events using JavaScript event listeners.
  - Checks for multiple monitors using `window.screen.isExtended`.

---
## Technologies & Libraries Used

| Feature                      | Technology / Library              |
|-----------------------------|-----------------------------------|
| Eye Movement & Gaze         | dlib, OpenCV                      |
| Facial Expressions          | FER (Facial Emotion Recognition) |
| Head Pose                   | dlib, OpenCV                      |
| Keystrokes                  | JavaScript Event Listeners        |
| Hand Movements              | MediaPipe                         |
| Surrounding Analysis        | OpenCV (DNN Module), YOLO         |
| Voice Cues                  | Web Audio API, Librosa            |
| Tab / Focus Change          | JavaScript Page Visibility API    |
| Copy/Paste Detection        | JavaScript Event Listeners        |
| Secondary Display Detection | JavaScript `window.screen` API    |

---

## JSON Report Format

Reports are generated every 10 seconds and appended to a session log. A sample entry is as follows:

```json
{
  "timestamp": "2023-10-26T18:35:20Z",
  "session_id": "a1b2c3d4e5f67890",
  "eye_movement": {
    "gaze_direction": "right",
    "is_blinking": false
  },
  "facial_expression": {
    "dominant_emotion": "neutral",
    "emotion_scores": {
      "neutral": 0.7,
      "happy": 0.1,
      "surprise": 0.15,
      "sad": 0.02,
      "angry": 0.01,
      "fear": 0.02
    }
  },
  "head_pose": {
    "pitch": -5.2,
    "yaw": 35.8,
    "roll": -2.1
  },
  "surrounding": {
    "people_count": 2,
    "prohibited_objects": []
  },
  "voice_cues": {
    "average_volume": 65.5,
    "is_speaking": true
  },
  "activity": {
    "keystroke_count": 0
  },
  "flags": [
    "CANDIDATE_LOOKING_AWAY",
    "MULTIPLE_FACES_DETECTED",
    "POTENTIAL_SPEAKING_DETECTED",
    "MULTIPLE_DISPLAYS_DETECTED",
    "PASTE_EVENT_DETECTED",
    "BROWSER_TAB_SWITCHED"
  ]
}
```
---
## venv setup

 1. Go to your directory
 ``` 
 cd path/to/your/project

 ```

 2. Setup python venv 
 ```
 python -m venv venv
```
3. Activate it
```
venv\Scripts\activate
```

**Note**:if it shows some authentication error of some type here. Run the following commands. This is a temporary fix.

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\venv\Scripts\Activate.ps1
```
---
## Backend

To run backend run the following command inside the venv

```
python app.py
```