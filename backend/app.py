import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError

from models import AnalysisRequest, AnalysisResponse, HeadPose

# --- AI Model Initialization Placeholder ---
# from mereos.modules.face_detector import FaceDetector
# from fer import FER
# face_detector = FaceDetector()
# emotion_detector = FER(mtcnn=True)
# print("AI Models Loaded.")
# ------------------------------------------

app = Flask(__name__)
CORS(app)


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        request_data = AnalysisRequest(**request.json)
    except ValidationError as e:
        return jsonify({
            "error": "Invalid request format",
            "details": e.errors()
        }), 400

    # --- TODO: Replace this mock analysis with real AI logic ---
    # Decode image and process with actual models when ready.
    # image_data = base64.b64decode(request_data.image)
    # frame = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

    # faces = face_detector.detect_faces(frame)
    # dominant_emotion = emotion_detector.detect_emotion(frame)
    # -----------------------------------------------------------

    # Mocked values (replace with actual analysis later)
    mock_face_detected = True
    mock_people_count = 1
    mock_head_pose = HeadPose(pitch=15.3, yaw=-28.1, roll=2.5)
    mock_emotion = "neutral"

    # Flag logic based on mock data and client metrics
    flags = []

    if mock_head_pose.yaw < -25:
        flags.append("CANDIDATE_LOOKING_AWAY_LEFT")

    if mock_head_pose.pitch > 20:
        flags.append("CANDIDATE_LOOKING_DOWN")

    if request_data.focus_lost_count > 0:
        flags.append("BROWSER_FOCUS_LOST")

    if mock_people_count > 1:
        flags.append("MULTIPLE_FACES_DETECTED")

    # Construct and return response
    response = AnalysisResponse(
        face_detected=mock_face_detected,
        people_count=mock_people_count,
        head_pose=mock_head_pose,
        dominant_emotion=mock_emotion,
        flags=flags
    )

    return jsonify(response.model_dump())


if __name__ == '__main__':
    app.run(debug=True, port=5000)
