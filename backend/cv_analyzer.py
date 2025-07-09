# cv_analyzer.py

import cv2
import numpy as np
from ultralytics import YOLO
import face_alignment

class VisionAnalyzer:
    def __init__(self):
        self.face_detector = YOLO("models/yolov8n-face.pt")
        self.face_detector.model.fuse()
        self.fa = face_alignment.FaceAlignment(
            face_alignment.LandmarksType.TWO_D,
            flip_input=False,
            device='cpu'
        )

    def analyze_frame(self, frame):
        h, w = frame.shape[:2]
        preds = self.face_detector.predict(source=frame, imgsz=640, verbose=False)[0]

        face_detected = False
        people_count = 0
        head_pose = None

        for box in preds.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            face_detected = True
            people_count += 1

            face_crop = frame[y1:y2, x1:x2]
            landmarks = self.fa.get_landmarks_from_image(face_crop)

            if landmarks is None:
                continue

            lm = landmarks[0]
            # adjust to original coordinates
            lm += np.array([x1, y1])

            image_points = np.array([
                lm[30],  # Nose tip
                lm[8],   # Chin
                lm[36],  # Left eye outer corner
                lm[45],  # Right eye outer corner
                lm[48],  # Left mouth corner
                lm[54],  # Right mouth corner
            ], dtype=np.float64)

            model_points = np.array([
                [0.0, 0.0, 0.0],
                [0.0, -63.6, -12.5],
                [-43.3, 32.7, -26.0],
                [43.3, 32.7, -26.0],
                [-28.9, -28.9, -24.1],
                [28.9, -28.9, -24.1]
            ], dtype=np.float64)

            focal_length = w
            camera_matrix = np.array([
                [focal_length, 0, w / 2],
                [0, focal_length, h / 2],
                [0, 0, 1]
            ], dtype=np.float64)

            dist_coeffs = np.zeros((4, 1))

            success, rot, _ = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)
            if success:
                R, _ = cv2.Rodrigues(rot)
                sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
                if sy < 1e-6:
                    x = np.arctan2(-R[1, 2], R[1, 1])
                    y = np.arctan2(-R[2, 0], sy)
                    z = 0
                else:
                    x = np.arctan2(R[2, 1], R[2, 2])
                    y = np.arctan2(-R[2, 0], sy)
                    z = np.arctan2(R[1, 0], R[0, 0])

                head_pose = {
                    "yaw": round(np.degrees(y), 2),
                    "pitch": round(np.degrees(x), 2),
                    "roll": round(np.degrees(z), 2)
                }

            break

        return {"face_detected": face_detected, "people_count": people_count, "head_pose": head_pose}
