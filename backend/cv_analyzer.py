import cv2
import numpy as np

class VisionAnalyzer:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def analyze_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        face_detected = len(faces) > 0
        people_count = len(faces)

        head_pose = None

        if face_detected:
            # Use the first detected face for simplicity
            (x, y, w, h) = faces[0]

            # Fake facial landmarks as a proxy (only for demonstration)
            image_points = np.array([
                (x + w // 2, y + h // 3),           # Nose tip
                (x + w // 2, y + h - 10),           # Chin
                (x + w // 5, y + h // 3),           # Left eye
                (x + 4 * w // 5, y + h // 3),       # Right eye
                (x + w // 3, y + 4 * h // 5),       # Left mouth
                (x + 2 * w // 3, y + 4 * h // 5)    # Right mouth
            ], dtype="double")

            model_points = np.array([
                [0.0, 0.0, 0.0],          # Nose tip
                [0.0, -63.6, -12.5],      # Chin
                [-43.3, 32.7, -26.0],     # Left eye
                [43.3, 32.7, -26.0],      # Right eye
                [-28.9, -28.9, -24.1],    # Left mouth
                [28.9, -28.9, -24.1]      # Right mouth
            ])

            size = frame.shape
            focal_length = size[1]
            center = (size[1] / 2, size[0] / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype="double")

            dist_coeffs = np.zeros((4, 1))
            success, rotation_vector, _ = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)

            if success:
                rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
                sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
                singular = sy < 1e-6

                if not singular:
                    x = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
                    y = np.arctan2(-rotation_matrix[2, 0], sy)
                    z = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
                else:
                    x = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
                    y = np.arctan2(-rotation_matrix[2, 0], sy)
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
