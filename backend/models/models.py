from typing import Optional, List
from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    """
    Request schema for analyzing a user's session.
    """
    image: str  # Base64-encoded image string
    keystroke_count: int
    focus_lost_count: int
    keystroke_map: Optional[List[str]] = []


class HeadPose(BaseModel):
    """
    Submodel for representing head pose data.
    """
    pitch: float
    yaw: float
    roll: float


class AnalysisResponse(BaseModel):
    """
    Response schema for returning analysis results.
    """
    face_detected: bool
    people_count: int
    head_pose: Optional[HeadPose] = None
    dominant_emotion: Optional[str] = None
    flags: List[str]
    timestamp: str