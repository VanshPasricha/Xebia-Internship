"""Camera helpers used by student registration and attendance."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from utils.config import CAMERA_INDEX, FACES_DIR


class CameraStream:
    """Thin wrapper around OpenCV video capture."""

    def __init__(self, camera_index: int = CAMERA_INDEX) -> None:
        self.camera_index = camera_index
        self.capture: cv2.VideoCapture | None = None

    def open(self) -> bool:
        """Open the configured camera."""
        self.capture = cv2.VideoCapture(self.camera_index)
        if not self.capture or not self.capture.isOpened():
            return False

        # Prefer a wider, stable preview and explicitly avoid digital zoom where supported.
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if hasattr(cv2, "CAP_PROP_ZOOM"):
            self.capture.set(cv2.CAP_PROP_ZOOM, 0)
        return True

    def read(self) -> np.ndarray | None:
        """Return the latest frame if available."""
        if not self.capture:
            return None
        success, frame = self.capture.read()
        return frame if success else None

    def release(self) -> None:
        """Release the camera resource."""
        if self.capture:
            self.capture.release()
            self.capture = None


def save_face_sample(roll_no: str, frame: np.ndarray, index: int) -> Path:
    """Persist a captured sample under the student's folder."""
    student_dir = FACES_DIR / roll_no
    student_dir.mkdir(parents=True, exist_ok=True)
    output_path = student_dir / f"sample_{index:02d}.jpg"
    cv2.imwrite(str(output_path), frame)
    return output_path
