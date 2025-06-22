# backend/app.py

import base64
import numpy as np
import cv2
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pydantic import ValidationError

from models import AnalysisRequest, AnalysisResponse, HeadPose
from cv_analyzer import VisionAnalyzer  # Your own head pose estimation module
from deepface import DeepFace

import traceback

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
CORS(app)

# Load AI Models
try:
    # If VisionAnalyzer still uses dlib internally, you'll need to refactor it too.
    shape_predictor_path = "shape_predictor_68_face_landmarks.dat"
    # vision_analyzer = VisionAnalyzer(shape_predictor_path)
    vision_analyzer = VisionAnalyzer()
    print("✅ AI Models loaded successfully.")
except Exception as e:
    print(f"❌ Error loading AI models: {e}")
    raise e

# Flag logic
def generate_flags(report: AnalysisResponse, request_data: AnalysisRequest) -> list[str]:
    flags = []
    if report.head_pose:
        if report.head_pose.yaw > 25 or report.head_pose.yaw < -25:
            flags.append("CANDIDATE_LOOKING_AWAY")
        if report.head_pose.pitch > 20:
            flags.append("CANDIDATE_LOOKING_DOWN")
    if report.people_count > 1:
        flags.append("MULTIPLE_FACES_DETECTED")
    if not report.face_detected:
        flags.append("FACE_NOT_DETECTED")
    if request_data.focus_lost_count > 0:
        flags.append("BROWSER_FOCUS_LOST")
    return flags

# Main analysis route
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        request_data = AnalysisRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": "Invalid request format", "details": e.errors()}), 400

    try:
        image_data = base64.b64decode(request_data.image)
        frame = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Decoded image is None")
    except Exception as e:
        return jsonify({"error": "Invalid base64 image"}), 400

    try:
        # Run your own analysis (head pose, etc.)
        vision_results = vision_analyzer.analyze_frame(frame)
        head_pose_data = HeadPose(**vision_results["head_pose"]) if vision_results["head_pose"] else None

        dominant_emotion_result = None
        try:
            analysis_result = DeepFace.analyze(
                img_path=frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='mediapipe'  # <<< changed from 'dlib'
            )
            if isinstance(analysis_result, list) and len(analysis_result) > 0:
                dominant_emotion_result = analysis_result[0]['dominant_emotion']
                print("📸 DeepFace result:", analysis_result)
        except Exception as e:
            print("❌ DeepFace analysis failed:")
            traceback.print_exc()

        # Debug output before response
        print("🧠 dominant_emotion_result =", dominant_emotion_result)
        print("🧠 head_pose_data =", head_pose_data)
        print("🧠 vision_results =", vision_results)

        try:
            response = AnalysisResponse(
                face_detected=vision_results["face_detected"],
                people_count=vision_results["people_count"],
                head_pose=head_pose_data,
                dominant_emotion=dominant_emotion_result,
                flags=[]
            )
        except Exception as e:
            print("❌ Failed to create AnalysisResponse:")
            traceback.print_exc()
            return jsonify({"error": "Response formatting failed", "details": str(e)}), 500

        response.flags = generate_flags(response, request_data)
        return jsonify(response.dict())


    except Exception as e:
        print("❌ General processing error:")
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
