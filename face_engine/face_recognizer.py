"""Face recognition logic for attendance sessions."""

from __future__ import annotations

from typing import Any

import numpy as np

from face_engine.face_encode import FaceEncoder
from utils.config import FACE_DISTANCE_THRESHOLD


class FaceRecognizer:
    """Compare live encodings against stored student embeddings."""

    def __init__(self, student_records: list[dict[str, Any]], threshold: float | None = None) -> None:
        self.student_records = student_records
        self.encoder = FaceEncoder()
        self.threshold = threshold if threshold is not None else FACE_DISTANCE_THRESHOLD
        self.fallback_threshold = 7.2
        self.ambiguity_margin = 0.02

    def _probe_candidates(self, frame: np.ndarray) -> list[tuple[np.ndarray, float, str]]:
        """Build probe vectors that match the dimensions of stored encodings."""
        dimensions = {
            encoding.shape[0]
            for student in self.student_records
            for encoding in student["encodings"]
            if hasattr(encoding, "shape") and len(encoding.shape) == 1
        }

        probes: list[tuple[np.ndarray, float, str]] = []
        if 128 in dimensions:
            face_probe = self.encoder.face_recognition_encoding(frame)
            if face_probe is not None:
                probes.append((face_probe, self.threshold, "face_recognition"))
        if 1024 in dimensions:
            fallback_probe = self.encoder.fallback_encoding(frame)
            if fallback_probe is not None:
                probes.append((fallback_probe, self.fallback_threshold, "opencv-fallback"))
        return probes

    def recognize(self, frame: np.ndarray) -> dict[str, Any] | None:
        """Return the best student match or an UNKNOWN result."""
        probes = self._probe_candidates(frame)
        if not probes:
            return {"status": "NO_FACE", "distance": None}

        best_match: dict[str, Any] | None = None
        best_distance = float("inf")
        second_best_distance = float("inf")
        best_threshold = self.threshold
        best_mode = "unknown"

        for probe, threshold, mode in probes:
            for student in self.student_records:
                for encoding in student["encodings"]:
                    if encoding.shape != probe.shape:
                        continue
                    distance = float(np.linalg.norm(probe - encoding))
                    if distance < best_distance:
                        second_best_distance = best_distance
                        best_distance = distance
                        best_match = student
                        best_threshold = threshold
                        best_mode = mode
                    elif distance < second_best_distance:
                        second_best_distance = distance

        if best_match and best_distance < best_threshold:
            if best_mode == "face_recognition" and second_best_distance < float("inf") and abs(second_best_distance - best_distance) < self.ambiguity_margin:
                return {"status": "UNKNOWN", "distance": round(best_distance, 4), "reason": "ambiguous"}
            return {
                "roll_no": best_match["roll_no"],
                "name": best_match["name"],
                "section": best_match["section"],
                "distance": round(best_distance, 4),
                "status": "MATCH",
                "mode": best_mode,
            }
        return {"status": "UNKNOWN", "distance": round(best_distance, 4)}
