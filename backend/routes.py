from flask import Blueprint, request, render_template, jsonify
from models.models import AnalysisRequest, AnalysisResponse, HeadPose
from cv_analyzer import VisionAnalyzer
from deepface import DeepFace
from attire_check import check_attire
from datetime import datetime
from pytz import timezone
import traceback, base64, numpy as np, cv2
from pydantic import ValidationError

routes = Blueprint('routes', __name__)
visionAnalyzer = VisionAnalyzer()

# Emotion fusion logic
def fuseEmotions(emotions: dict) -> str:
    nervous = (emotions['fear'] + emotions['angry'] + emotions['disgust']) / 3
    relaxed = (emotions['happy'] + emotions['neutral']) / 2
    composite = {
    "nervous": nervous,
    "relaxed": relaxed,
    "happy": happy,
    "sad": sad,
    "fear": fear
    }

    return max(composite, key=composite.get)


# Head pose to readable string
def describeHeadPose(yaw, pitch, roll):
    orientation = []
    if yaw > 20: orientation.append("looking right")
    elif yaw < -20: orientation.append("looking left")
    if pitch > 160: orientation.append("looking down")
    elif pitch < 30: orientation.append("looking up")
    if roll > 15: orientation.append("head tilted right")
    elif roll < -15: orientation.append("head tilted left")
    return ", ".join(orientation) if orientation else "facing forward"

# Route: Home → Attire Check
@routes.route('/')
def index():
    return render_template('attire_check.html')

# Route: After attire is validated
@routes.route('/proctoring')
def proctoring():
    return render_template('proctor.html')

# Route: Attire API
@routes.route('/attire_check', methods=['POST'])
def handle_attire_check():
    try:
        image_b64 = request.json.get('image')
        result = check_attire(image_b64)
        return jsonify({'is_formal': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Proctor Analysis API
@routes.route('/analyze', methods=['POST'])
def analyze():
    try:
        requestData = AnalysisRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": "Invalid request format", "details": e.errors()}), 400

    try:
        imageData = base64.b64decode(requestData.image)
        frame = cv2.imdecode(np.frombuffer(imageData, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Decoded image is None")
    except Exception:
        return jsonify({"error": "Invalid base64 image"}), 400

    try:
        visionResults = visionAnalyzer.analyzeFrame(frame)
        headPoseData = HeadPose(**visionResults["head_pose"]) if visionResults["head_pose"] else None

        dominantEmotion = None
        try:
            analysis = DeepFace.analyze(
                img_path=frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            if isinstance(analysis, list) and len(analysis) > 0:
                emotions = analysis[0]['emotion']
                dominantEmotion = fuseEmotions(emotions)
        except:
            traceback.print_exc()

        headOrientationReadable = "Not detected"
        if headPoseData:
            headOrientationReadable = describeHeadPose(
                headPoseData.yaw,
                headPoseData.pitch,
                headPoseData.roll
            )

        istTime = datetime.now(timezone('Asia/Kolkata')).isoformat()

        response = AnalysisResponse(
            face_detected=visionResults["face_detected"],
            people_count=visionResults["people_count"],
            head_pose=headPoseData,
            dominant_emotion=dominantEmotion,
            flags=[],
            timestamp=istTime
        )

        # Add flags here if needed
        payload = response.dict()
        payload['head_orientation_readable'] = headOrientationReadable
        return jsonify(payload)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
