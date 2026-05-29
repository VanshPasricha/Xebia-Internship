"""Attendance capture page for faculty sessions."""

from __future__ import annotations

from datetime import datetime, timedelta

import cv2
import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from client.api_client import BackendApiClient, BackendApiError
from database.models import TimetableEntry
from face_engine.face_capture import CameraStream
from face_engine.face_recognizer import FaceRecognizer
from services.attendance_service import AttendanceService
from services.student_service import StudentService
from services.timetable_service import TimetableService
from utils.helpers import frame_to_pixmap


class AttendanceWidget(QWidget):
    """Faculty-only attendance page bound to today's classes."""

    def __init__(self, faculty_username: str) -> None:
        super().__init__()
        self.faculty_username = faculty_username
        self.timetable_service = TimetableService()
        self.student_service = StudentService()
        self.attendance_service = AttendanceService()
        self.api_client = BackendApiClient()
        self.camera = CameraStream()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._process_frame)
        self.recognizer: FaceRecognizer | None = None
        self.current_session = None
        self.last_marked: dict[str, datetime] = {}
        self.pending_match_roll_no: str | None = None
        self.pending_match_count = 0
        self.required_confirmations = 1
        self._face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self._build_ui()
        self.load_today_classes()

    def _build_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(18)

        controls = QFrame()
        controls.setObjectName("Card")
        controls_layout = QVBoxLayout(controls)

        title = QLabel("Attendance Session")
        title.setObjectName("Title")
        subtitle = QLabel("Select one of today's faculty classes to begin face-based identity verification for that batch.")
        subtitle.setObjectName("Subtitle")
        controls_layout.addWidget(title)
        controls_layout.addWidget(subtitle)

        row = QHBoxLayout()
        self.class_selector = QComboBox()
        self.start_button = QPushButton("Start Attendance")
        self.start_button.clicked.connect(self.start_session)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setProperty("variant", "danger")
        self.stop_button.clicked.connect(self.stop_session)
        self.stop_button.setEnabled(False)
        row.addWidget(self.class_selector)
        row.addWidget(self.start_button)
        row.addWidget(self.stop_button)
        controls_layout.addLayout(row)

        self.mode_label = QLabel("Awaiting session start.")
        self.mode_label.setObjectName("Subtitle")
        controls_layout.addWidget(self.mode_label)

        self.preview = QLabel("Camera feed will appear here once a class is selected.")
        self.preview.setMinimumSize(420, 300)
        self.preview.setMaximumHeight(540)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setStyleSheet("border: 1px dashed #3a4c64; border-radius: 16px; color: #93a3ba;")
        controls_layout.addWidget(self.preview)

        records_card = QFrame()
        records_card.setObjectName("Card")
        records_layout = QVBoxLayout(records_card)
        records_title = QLabel("Recognized Students")
        records_title.setObjectName("Title")
        records_layout.addWidget(records_title)
        self.records_table = QTableWidget(0, 4)
        self.records_table.setHorizontalHeaderLabels(["Roll Number", "Name", "Time", "Status"])
        self.records_table.horizontalHeader().setStretchLastSection(True)
        records_layout.addWidget(self.records_table)

        layout.addWidget(controls, 0, 0)
        layout.addWidget(records_card, 0, 1)

    def load_today_classes(self) -> None:
        try:
            classes = self.api_client.get_today_classes(self.faculty_username)
        except BackendApiError:
            classes = self.timetable_service.get_today_classes(self.faculty_username)
        self.class_selector.clear()
        self.class_selector.addItem("Select today's class", None)
        for entry in classes:
            if isinstance(entry, dict):
                normalized = TimetableEntry(**entry)
            else:
                normalized = entry
            label = f"{normalized.subject} | {normalized.section} | {normalized.start_time}-{normalized.end_time}"
            self.class_selector.addItem(label, normalized)

    def start_session(self) -> None:
        entry = self.class_selector.currentData()
        if entry is None:
            QMessageBox.warning(self, "No Class Selected", "Choose one of today's classes first.")
            return

        student_records = [
            student for student in self.student_service.get_all_student_encodings() if student["section"] == entry.section and student["encodings"]
        ]
        try:
            api_students = self.api_client.list_student_encodings(entry.section)
            student_records = [
                {
                    "roll_no": student["roll_no"],
                    "name": student["name"],
                    "section": student["section"],
                    "department": student["department"],
                    "year": student["year"],
                    "red_flags": student["red_flags"],
                    "encodings": [np.asarray(encoding, dtype=np.float64) for encoding in student["encodings"]],
                }
                for student in api_students
                if student["encodings"]
            ]
        except BackendApiError:
            pass
        if not student_records:
            QMessageBox.warning(self, "No Students", "No registered students with face data are available for this batch.")
            return

        if not self.camera.open():
            QMessageBox.warning(self, "Camera Error", "Unable to access the webcam.")
            return

        self.current_session = entry
        self.pending_match_roll_no = None
        self.pending_match_count = 0
        self.last_marked.clear()
        self.records_table.setRowCount(0)
        try:
            self.api_client.seed_attendance_session(entry.id)
        except BackendApiError:
            self.attendance_service.ensure_session_records(entry, student_records)
        self.recognizer = FaceRecognizer(student_records)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.mode_label.setText(f"Recognition mode: {self.recognizer.encoder.mode} | Batch: {entry.section}")
        self.timer.start(180)

    def stop_session(self) -> None:
        self.timer.stop()
        self.camera.release()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pending_match_roll_no = None
        self.pending_match_count = 0
        self.preview.clear()
        self.preview.setText("Camera feed will appear here once a class is selected.")

    def _process_frame(self) -> None:
        frame = self.camera.read()
        if frame is None or self.recognizer is None or self.current_session is None:
            return

        match = self.recognizer.recognize(frame)
        if match and match.get("status") == "MATCH":
            roll_no = match["roll_no"]
            if self.pending_match_roll_no == roll_no:
                self.pending_match_count += 1
            else:
                self.pending_match_roll_no = roll_no
                self.pending_match_count = 1

            cutoff = self.last_marked.get(roll_no)
            if self.pending_match_count >= self.required_confirmations and (not cutoff or datetime.now() - cutoff > timedelta(seconds=5)):
                try:
                    response = self.api_client.mark_attendance(self.current_session.id, match["roll_no"])
                    success = response["success"]
                    message = response["message"]
                except BackendApiError:
                    success, message = self.attendance_service.mark_attendance(match, self.current_session)
                self._append_record(
                    match["roll_no"],
                    match["name"],
                    datetime.now().strftime("%H:%M:%S"),
                    "PRESENT" if success else "DUPLICATE",
                )
                self.last_marked[roll_no] = datetime.now()
                self.pending_match_roll_no = None
                self.pending_match_count = 0
                self.mode_label.setText(message)
            else:
                self.mode_label.setText(
                    f"Verifying {match['name']} ({self.pending_match_count}/{self.required_confirmations}) | Distance={match['distance']}"
                )
        elif match and match.get("status") == "NO_FACE":
            self.pending_match_roll_no = None
            self.pending_match_count = 0
            self.mode_label.setText("No single clear face detected. Keep one student in frame.")
        elif match and match.get("status") == "UNKNOWN":
            self.pending_match_roll_no = None
            self.pending_match_count = 0
            self.mode_label.setText(f"Unknown or ambiguous face. Distance={match.get('distance', '-')}")

        display_frame = self._build_display_frame(frame, match)
        pixmap = frame_to_pixmap(display_frame).scaled(
            self.preview.width(),
            self.preview.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview.setPixmap(pixmap)

    def _build_display_frame(self, frame: np.ndarray, match: dict | None) -> np.ndarray:
        """Highlight detected faces without forcing a fixed framing box."""
        display = frame.copy()
        height, width = display.shape[:2]
        gray = cv2.cvtColor(display, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(80, 80))

        frame_color = (36, 168, 255)
        text = "Scanning for a single clear face"
        if match and match.get("status") == "MATCH":
            frame_color = (46, 204, 113)
            text = f"Matched: {match['name']}"
        elif match and match.get("status") == "UNKNOWN":
            frame_color = (80, 130, 220)
            text = "Face detected, adjusting match"
        elif match and match.get("status") == "NO_FACE":
            text = "Keep one clear face visible"

        for x, y, w, h in faces:
            cv2.rectangle(display, (x, y), (x + w, y + h), frame_color, 2)

        cv2.putText(
            display,
            text,
            (24, 34),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            frame_color,
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            display,
            "Avoid multiple faces in frame for best attendance accuracy",
            (24, min(height - 18, height - 18)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 228, 240),
            1,
            cv2.LINE_AA,
        )
        return display

    def _append_record(self, roll_no: str, name: str, time_value: str, status: str) -> None:
        row = self.records_table.rowCount()
        self.records_table.insertRow(row)
        for index, value in enumerate([roll_no, name, time_value, status]):
            self.records_table.setItem(row, index, QTableWidgetItem(value))
