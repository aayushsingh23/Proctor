import cv2
import numpy as np
from ultralytics import YOLO
import face_alignment

class VisionAnalyzer:
    def __init__(self):
        """
        Load face detection (YOLOv8) and landmark detection (face_alignment) models.
        Use case: Detect faces and estimate head pose in a given frame.
        """
        self.faceDetector = YOLO("models/yolov8n-face.pt")
        self.faceDetector.model.fuse()
        self.fa = face_alignment.FaceAlignment(
            face_alignment.LandmarksType.TWO_D,
            flip_input=False,
            device='cpu'
        )

    def analyzeFrame(self, frame):
        """
        Analyze the frame to detect faces and compute head orientation.
        Returns:
            dict with keys: face_detected, people_count, head_pose (yaw, pitch, roll)
        Use case: Core vision engine for your proctoring system.
        """
        h, w = frame.shape[:2]
        preds = self.faceDetector.predict(source=frame, imgsz=640, verbose=False)[0]

        faceDetected = False
        peopleCount = 0
        headPose = None

        for box in preds.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            faceDetected = True
            peopleCount += 1

            faceCrop = frame[y1:y2, x1:x2]
            landmarks = self.fa.get_landmarks_from_image(faceCrop)

            if landmarks is None:
                continue

            lm = landmarks[0]
            lm += np.array([x1, y1])  # Adjust to full-frame coordinates

            # 6 facial landmarks for pose estimation
            imagePoints = np.array([
                lm[30],  # Nose tip
                lm[8],   # Chin
                lm[36],  # Left eye outer corner
                lm[45],  # Right eye outer corner
                lm[48],  # Left mouth corner
                lm[54],  # Right mouth corner
            ], dtype=np.float64)

            # 3D model reference points
            modelPoints = np.array([
                [0.0, 0.0, 0.0],
                [0.0, -63.6, -12.5],
                [-43.3, 32.7, -26.0],
                [43.3, 32.7, -26.0],
                [-28.9, -28.9, -24.1],
                [28.9, -28.9, -24.1]
            ], dtype=np.float64)

            focalLength = w
            cameraMatrix = np.array([
                [focalLength, 0, w / 2],
                [0, focalLength, h / 2],
                [0, 0, 1]
            ], dtype=np.float64)

            distCoeffs = np.zeros((4, 1))

            success, rot, _ = cv2.solvePnP(modelPoints, imagePoints, cameraMatrix, distCoeffs)
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

                headPose = {
                    "yaw": round(np.degrees(y), 2),
                    "pitch": round(np.degrees(x), 2),
                    "roll": round(np.degrees(z), 2)
                }

            break  # Analyze only the first detected face

        return {
            "face_detected": faceDetected,
            "people_count": peopleCount,
            "head_pose": headPose
        }
