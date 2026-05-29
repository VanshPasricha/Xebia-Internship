"""Shared helper utilities for FACETRACK."""

from __future__ import annotations

import base64
import hashlib
import json
import logging
from datetime import datetime
from typing import Iterable

import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap

from utils.config import LOG_FILE, LOGS_DIR


def setup_logging() -> None:
    """Configure file logging once for the application."""
    if logging.getLogger().handlers:
        return

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def hash_password(password: str) -> str:
    """Return a stable SHA-256 password hash."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def serialize_encodings(encodings: Iterable[np.ndarray]) -> str:
    """Serialize numpy encodings into a storable string."""
    payload = [base64.b64encode(np.asarray(item, dtype=np.float64).tobytes()).decode("ascii") for item in encodings]
    return json.dumps(payload)


def deserialize_encodings(raw_value: str | None) -> list[np.ndarray]:
    """Deserialize facial encodings stored in the database."""
    if not raw_value:
        return []

    values = json.loads(raw_value)
    return [np.frombuffer(base64.b64decode(item.encode("ascii")), dtype=np.float64) for item in values]


def current_day_name() -> str:
    """Return the current weekday name."""
    return datetime.now().strftime("%A")


def today_date_str() -> str:
    """Return the current date string."""
    return datetime.now().strftime("%Y-%m-%d")


def now_time_str() -> str:
    """Return the current time string."""
    return datetime.now().strftime("%H:%M:%S")


def frame_to_pixmap(frame: np.ndarray) -> QPixmap:
    """Convert a BGR OpenCV frame to a Qt pixmap."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    height, width, channel = rgb_frame.shape
    bytes_per_line = channel * width
    image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(image)


def safe_percentage(present: int, total: int) -> float:
    """Avoid division by zero while calculating percentages."""
    if total <= 0:
        return 0.0
    return round((present / total) * 100, 2)
