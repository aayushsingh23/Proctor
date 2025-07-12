import base64
import cv2
import numpy as np
from deepface import DeepFace

def decode_base64_image(b64_string):
    image_data = base64.b64decode(b64_string)
    np_arr = np.frombuffer(image_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

def match_faces(id_image_b64, selfie_b64):
    try:
        id_img = decode_base64_image(id_image_b64)
        selfie_img = decode_base64_image(selfie_b64)

        result = DeepFace.verify(id_img, selfie_img, enforce_detection=False)
        return {
            "verified": result["verified"],
            "distance": result["distance"],
            "threshold": result["threshold"]
        }

    except Exception as e:
        print("❌ Face match failed:", e)
        return {
            "error": str(e),
            "verified": False,
            "distance": None,
            "threshold": None
        }
