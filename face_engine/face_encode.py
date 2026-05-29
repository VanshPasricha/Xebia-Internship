"""Facial embedding extraction helpers."""

from __future__ import annotations

import logging
from typing import Iterable

import cv2
import numpy as np

try:
    import face_recognition
except ImportError:
    face_recognition = None

LOGGER = logging.getLogger(__name__)


class FaceEncoder:
    """Create consistent encodings from frames or image files."""

    def __init__(self) -> None:
        self._face_recognition_available = face_recognition is not None
        self._cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    @property
    def mode(self) -> str:
        """Describe which encoding strategy is active."""
        return "face_recognition" if self._face_recognition_available else "opencv-fallback"

    def _detect_primary_face(self, frame: np.ndarray) -> np.ndarray | None:
        """Return a cropped face region when exactly one face is present."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(80, 80))
        if len(faces) != 1:
            return None

        x, y, w, h = max(faces, key=lambda item: item[2] * item[3])
        pad = max(24, int(min(w, h) * 0.18))
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(frame.shape[1], x + w + pad)
        y1 = min(frame.shape[0], y + h + pad)
        return frame[y0:y1, x0:x1]

    def fallback_encoding(self, frame: np.ndarray) -> np.ndarray | None:
        """Generate a lightweight deterministic embedding from a detected face crop."""
        face_region = self._detect_primary_face(frame)
        if face_region is None:
            return None
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        normalized = cv2.equalizeHist(gray)
        resized = cv2.resize(normalized, (32, 32)).astype(np.float64) / 255.0
        return resized.flatten()

    def face_recognition_encoding(self, frame: np.ndarray) -> np.ndarray | None:
        """Generate a dlib/face_recognition embedding from a BGR frame."""
        if not self._face_recognition_available:
            return None

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame = np.ascontiguousarray(rgb_frame, dtype=np.uint8)
            locations = face_recognition.face_locations(rgb_frame, model="hog")
            if len(locations) != 1:
                return None
            encodings = face_recognition.face_encodings(rgb_frame, locations, num_jitters=1)
            if len(encodings) == 1:
                return encodings[0]
        except Exception:
            LOGGER.exception("face_recognition failed on live frame")
        return None

    def encoding_from_frame(self, frame: np.ndarray) -> np.ndarray | None:
        """Extract a single face encoding from a BGR frame."""
        encoding = self.face_recognition_encoding(frame)
        if encoding is not None:
            return encoding
        return self.fallback_encoding(frame)

    def encodings_from_files(self, image_paths: Iterable[str]) -> list[np.ndarray]:
        """Load images and collect any encodings that can be generated."""
        encodings: list[np.ndarray] = []
        for image_path in image_paths:
            frame = cv2.imread(str(image_path))
            if frame is None:
                continue

            if self._face_recognition_available:
                try:
                    image = face_recognition.load_image_file(str(image_path))
                    image = np.ascontiguousarray(image, dtype=np.uint8)
                    locations = face_recognition.face_locations(image, model="hog")
                    if len(locations) != 1:
                        continue
                    file_encodings = face_recognition.face_encodings(image, locations)
                    if len(file_encodings) == 1:
                        encodings.append(file_encodings[0])
                        continue
                except Exception:
                    LOGGER.exception("face_recognition failed on sample %s; using fallback encoder", image_path)

            fallback = self.fallback_encoding(frame)
            if fallback is not None:
                encodings.append(fallback)
        return encodings
