# backend/cv_analyzer.py

import cv2
import mediapipe as mp
import numpy as np

class VisionAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False,
                                                    max_num_faces=2,
                                                    refine_landmarks=True,
                                                    min_detection_confidence=0.5,
                                                    min_tracking_confidence=0.5)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

    # def analyze_frame(self, frame):
    #     results = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    #     face_results = self.face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    #     face_detected = results.multi_face_landmarks is not None
    #     people_count = len(face_results.detections) if face_results.detections else 0

    #     head_pose = None
    #     if face_detected:
    #         landmarks = results.multi_face_landmarks[0].landmark

    #         # Use 6 key points to estimate head pose
    #         image_points = np.array([
    #             [landmarks[1].x, landmarks[1].y],   # Nose tip
    #             [landmarks[33].x, landmarks[33].y], # Chin
    #             [landmarks[263].x, landmarks[263].y], # Right eye right corner
    #             [landmarks[133].x, landmarks[133].y], # Left eye left corner
    #             [landmarks[362].x, landmarks[362].y], # Right mouth corner
    #             [landmarks[61].x, landmarks[61].y]  # Left mouth corner
    #         ], dtype=np.float32)

    #         h, w, _ = frame.shape
    #         image_points *= [w, h]  # Convert from normalized to pixel coords

    #         model_points = np.array([
    #             [0.0, 0.0, 0.0],        # Nose tip
    #             [0.0, -63.6, -12.5],    # Chin
    #             [43.3, 32.7, -26.0],    # Right eye right corner
    #             [-43.3, 32.7, -26.0],   # Left eye left corner
    #             [28.9, -28.9, -24.1],   # Right mouth corner
    #             [-28.9, -28.9, -24.1]   # Left mouth corner
    #         ])

    #         focal_length = w
    #         center = (w / 2, h / 2)
    #         camera_matrix = np.array([[focal_length, 0, center[0]],
    #                                   [0, focal_length, center[1]],
    #                                   [0, 0, 1]], dtype="double")

    #         dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
    #         success, rotation_vector, _ = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)

    #         if success:
    #             rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    #             proj_matrix = np.hstack((rotation_matrix, np.zeros((3, 1))))
    #             _, _, _, _, _, _, eulerAngles = cv2.decomposeProjectionMatrix(proj_matrix)
    #             yaw = float(eulerAngles[1])
    #             pitch = float(eulerAngles[0])
    #             roll = float(eulerAngles[2])
    #             head_pose = {"yaw": yaw, "pitch": pitch, "roll": roll}

    #     return {
    #         "face_detected": face_detected,
    #         "people_count": people_count,
    #         "head_pose": head_pose
    #     }

    def analyze_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        face_results = self.face_detection.process(rgb)

        face_detected = results.multi_face_landmarks is not None
        people_count = len(face_results.detections) if face_results.detections else 0

        head_pose = None
        if face_detected:
            landmarks = results.multi_face_landmarks[0].landmark
            h, w, _ = frame.shape

            def get_point(idx):
                pt = landmarks[idx]
                return np.array([pt.x * w, pt.y * h], dtype=np.float32)

            image_points = np.array([
                get_point(1),    # Nose tip
                get_point(152),  # Chin
                get_point(33),   # Left eye left corner
                get_point(263),  # Right eye right corner
                get_point(78),   # Left Mouth corner
                get_point(308),  # Right mouth corner
            ], dtype=np.float32)

            model_points = np.array([
                [0.0, 0.0, 0.0],          # Nose tip
                [0.0, -63.6, -12.5],      # Chin
                [-43.3, 32.7, -26.0],     # Left eye
                [43.3, 32.7, -26.0],      # Right eye
                [-28.9, -28.9, -24.1],    # Left mouth
                [28.9, -28.9, -24.1]      # Right mouth
            ])

            focal_length = w
            center = (w / 2, h / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype="double")

            dist_coeffs = np.zeros((4, 1))
            success, rotation_vector, _ = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)

            if success:
                rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
                sy = np.sqrt(rotation_matrix[0,0] ** 2 + rotation_matrix[1,0] ** 2)
                singular = sy < 1e-6

                if not singular:
                    x = np.arctan2(rotation_matrix[2,1], rotation_matrix[2,2])
                    y = np.arctan2(-rotation_matrix[2,0], sy)
                    z = np.arctan2(rotation_matrix[1,0], rotation_matrix[0,0])
                else:
                    x = np.arctan2(-rotation_matrix[1,2], rotation_matrix[1,1])
                    y = np.arctan2(-rotation_matrix[2,0], sy)
                    z = 0

                pitch = np.degrees(x)
                yaw = np.degrees(y)
                roll = np.degrees(z)
                head_pose = {
                    "yaw": round(yaw, 2),
                    "pitch": round(pitch, 2),
                    "roll": round(roll, 2)
                }

        return {
            "face_detected": face_detected,
            "people_count": people_count,
            "head_pose": head_pose
        }
