"""Student registration page for faculty users."""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from face_engine.face_capture import CameraStream, save_face_sample
from face_engine.face_encode import FaceEncoder
from client.api_client import BackendApiClient, BackendApiError
from services.student_service import StudentService
from utils.config import BATCH_OPTIONS, FACE_SAMPLE_MAX, FACE_SAMPLE_TARGET
from utils.helpers import frame_to_pixmap, serialize_encodings

LOGGER = logging.getLogger(__name__)


class RegisterStudentWidget(QWidget):
    """Admin-managed student registration form with webcam capture and profile management."""

    student_registered = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.student_service = StudentService()
        self.api_client = BackendApiClient()
        self.camera = CameraStream()
        self.encoder = FaceEncoder()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
        self.current_frame = None
        self.captured_paths: list[Path] = []
        self.editing_roll_no: str | None = None

        self._build_ui()
        self.load_students()

    def _build_ui(self) -> None:
        outer = QGridLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setHorizontalSpacing(18)

        left_column = QVBoxLayout()

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)

        title = QLabel("Register Student")
        title.setObjectName("Title")
        subtitle = QLabel("Admin captures 15-20 facial samples and creates or manages student login profiles for each batch.")
        subtitle.setObjectName("Subtitle")
        form_layout.addWidget(title)
        form_layout.addWidget(subtitle)

        self.roll_input = QLineEdit()
        self.name_input = QLineEdit()
        self.department_input = QLineEdit()
        self.year_input = QSpinBox()
        self.year_input.setRange(1, 6)
        self.section_input = QComboBox()
        self.section_input.setEditable(True)
        self.section_input.addItems(BATCH_OPTIONS)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Leave blank to keep current password while editing")

        form = QFormLayout()
        form.addRow("Roll Number", self.roll_input)
        form.addRow("Name", self.name_input)
        form.addRow("Department", self.department_input)
        form.addRow("Year", self.year_input)
        form.addRow("Batch", self.section_input)
        form.addRow("Student Password", self.password_input)
        form_layout.addLayout(form)

        self.progress = QProgressBar()
        self.progress.setRange(0, FACE_SAMPLE_MAX)
        self.progress.setValue(0)
        form_layout.addWidget(self.progress)

        camera_button_row = QHBoxLayout()
        self.camera_button = QPushButton("Start Camera")
        self.camera_button.clicked.connect(self.toggle_camera)
        self.capture_button = QPushButton("Capture Sample")
        self.capture_button.clicked.connect(self.capture_sample)
        self.capture_button.setEnabled(False)
        camera_button_row.addWidget(self.camera_button)
        camera_button_row.addWidget(self.capture_button)
        form_layout.addLayout(camera_button_row)

        action_button_row = QHBoxLayout()
        self.save_button = QPushButton("Register Student")
        self.save_button.clicked.connect(self.register_student)
        self.update_button = QPushButton("Update Profile")
        self.update_button.setProperty("variant", "secondary")
        self.update_button.clicked.connect(self.update_student)
        self.delete_button = QPushButton("Delete Student")
        self.delete_button.setProperty("variant", "danger")
        self.delete_button.clicked.connect(self.delete_student)
        self.reset_button = QPushButton("Reset")
        self.reset_button.setProperty("variant", "secondary")
        self.reset_button.clicked.connect(self._reset_form)
        for button in [self.save_button, self.update_button, self.delete_button, self.reset_button]:
            action_button_row.addWidget(button)
        form_layout.addLayout(action_button_row)
        form_layout.addStretch()
        left_column.addWidget(form_card)

        list_card = QFrame()
        list_card.setObjectName("Card")
        list_layout = QVBoxLayout(list_card)
        list_title = QLabel("Registered Students")
        list_title.setObjectName("Title")
        list_subtitle = QLabel("Select a student to load, edit, or delete the profile.")
        list_subtitle.setObjectName("Subtitle")
        list_layout.addWidget(list_title)
        list_layout.addWidget(list_subtitle)
        self.students_table = QTableWidget(0, 6)
        self.students_table.setHorizontalHeaderLabels(["Roll Number", "Name", "Department", "Year", "Batch", "Red Flags"])
        self.students_table.horizontalHeader().setStretchLastSection(True)
        list_layout.addWidget(self.students_table)

        list_button_row = QHBoxLayout()
        self.load_button = QPushButton("Load Selected")
        self.load_button.setProperty("variant", "secondary")
        self.load_button.clicked.connect(self.load_selected_student)
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.setProperty("variant", "secondary")
        self.refresh_button.clicked.connect(self.load_students)
        list_button_row.addWidget(self.load_button)
        list_button_row.addWidget(self.refresh_button)
        list_layout.addLayout(list_button_row)
        left_column.addWidget(list_card)

        preview_card = QFrame()
        preview_card.setObjectName("Card")
        preview_layout = QVBoxLayout(preview_card)
        self.camera_label = QLabel("Camera preview will appear here.")
        self.camera_label.setMinimumSize(420, 320)
        self.camera_label.setStyleSheet("border: 1px dashed #cdd9e5; border-radius: 16px; color: #617287;")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sample_info = QLabel(f"Captured samples: 0 / {FACE_SAMPLE_TARGET}")
        self.sample_info.setObjectName("Subtitle")
        preview_layout.addWidget(self.camera_label)
        preview_layout.addWidget(self.sample_info)
        preview_layout.addStretch()

        outer.addLayout(left_column, 0, 0)
        outer.addWidget(preview_card, 0, 1)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._stop_camera_preview()
        super().closeEvent(event)

    def _stop_camera_preview(self) -> None:
        if self.timer.isActive():
            self.timer.stop()
        self.camera.release()
        self.camera_button.setText("Start Camera")
        self.capture_button.setEnabled(False)
        self.camera_label.clear()
        self.camera_label.setText("Camera preview will appear here.")

    def toggle_camera(self) -> None:
        if self.timer.isActive():
            self._stop_camera_preview()
            return

        if not self.camera.open():
            QMessageBox.warning(self, "Camera Error", "Unable to access the webcam.")
            return

        self.camera_button.setText("Stop Camera")
        self.capture_button.setEnabled(True)
        self.timer.start(120)

    def _update_frame(self) -> None:
        frame = self.camera.read()
        if frame is None:
            return
        self.current_frame = frame.copy()
        pixmap = frame_to_pixmap(frame).scaled(
            self.camera_label.width(),
            self.camera_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.camera_label.setPixmap(pixmap)

    def capture_sample(self) -> None:
        if self.current_frame is None:
            QMessageBox.information(self, "No Frame", "Start the camera before capturing samples.")
            return

        if len(self.captured_paths) >= FACE_SAMPLE_MAX:
            QMessageBox.information(self, "Limit Reached", "Maximum face sample count reached.")
            return

        roll_no = self.roll_input.text().strip().upper()
        if not roll_no:
            QMessageBox.warning(self, "Missing Roll Number", "Enter the roll number before capturing samples.")
            return

        output_path = save_face_sample(roll_no, self.current_frame, len(self.captured_paths) + 1)
        self.captured_paths.append(output_path)
        self.progress.setValue(len(self.captured_paths))
        self.sample_info.setText(f"Captured samples: {len(self.captured_paths)} / {FACE_SAMPLE_TARGET}")

    def register_student(self) -> None:
        roll_no = self.roll_input.text().strip().upper()
        name = self.name_input.text().strip()
        department = self.department_input.text().strip()
        section = self.section_input.currentText().strip().upper()
        password = self.password_input.text().strip() or roll_no

        if not all([roll_no, name, department, section]):
            QMessageBox.warning(self, "Missing Fields", "Please complete all student fields.")
            return

        if len(self.captured_paths) < FACE_SAMPLE_TARGET:
            QMessageBox.warning(self, "Insufficient Samples", f"Capture at least {FACE_SAMPLE_TARGET} face samples.")
            return

        self.save_button.setEnabled(False)
        self.capture_button.setEnabled(False)
        try:
            self._stop_camera_preview()
            encodings = self.encoder.encodings_from_files([str(path) for path in self.captured_paths])
            payload = {
                "roll_no": roll_no,
                "name": name,
                "department": department,
                "year": self.year_input.value(),
                "section": section,
                "password": password,
                "face_image_dir": str(self.captured_paths[0].parent),
            }
            try:
                response = self.api_client.create_student(
                    {
                        **payload,
                        "serialized_encoding": serialize_encodings(encodings),
                    }
                )
                success = response["success"]
                message = response["message"]
            except BackendApiError:
                success, message = self.student_service.register_student(payload, encodings)
        except Exception as exc:
            LOGGER.exception("Student registration crashed for %s", roll_no)
            QMessageBox.critical(self, "Registration Error", f"Student registration failed unexpectedly.\n\n{exc}")
            return
        finally:
            self.save_button.setEnabled(True)
            self.capture_button.setEnabled(bool(self.current_frame is not None and self.timer.isActive()))

        if not success:
            QMessageBox.warning(self, "Registration Failed", message)
            return

        QMessageBox.information(
            self,
            "Student Registered",
            f"{message}\nStudent login password: {password}\nEncoder mode: {self.encoder.mode}",
        )
        self._reset_form()
        self.load_students()
        self.student_registered.emit()

    def load_students(self) -> None:
        try:
            students = self.api_client.list_students()
            use_dict = True
        except BackendApiError:
            students = self.student_service.list_students()
            use_dict = False
        self.students_table.setRowCount(len(students))
        for row_index, student in enumerate(students):
            values = (
                [student["roll_no"], student["name"], student["department"], student["year"], student["section"], student["red_flags"]]
                if use_dict
                else [student.roll_no, student.name, student.department, student.year, student.section, student.red_flags]
            )
            for col_index, value in enumerate(values):
                self.students_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def load_selected_student(self) -> None:
        row = self.students_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Select a student first.")
            return

        roll_no = self.students_table.item(row, 0).text()
        try:
            student_data = self.api_client.get_student(roll_no)
            student = type("StudentProxy", (), student_data)()
        except BackendApiError:
            student = self.student_service.get_student_by_roll(roll_no)
        if not student:
            QMessageBox.warning(self, "Student Missing", "The selected student could not be loaded.")
            return

        self.editing_roll_no = student.roll_no
        self.roll_input.setText(student.roll_no)
        self.name_input.setText(student.name)
        self.department_input.setText(student.department)
        self.year_input.setValue(student.year)
        self.section_input.setCurrentText(student.section)
        self.password_input.clear()
        self.captured_paths.clear()
        self.progress.setValue(0)
        self.sample_info.setText("Captured samples: edit mode uses existing face data")

    def update_student(self) -> None:
        if not self.editing_roll_no:
            QMessageBox.information(self, "Edit Mode", "Load a student from the table before updating.")
            return

        payload = {
            "roll_no": self.roll_input.text().strip().upper(),
            "name": self.name_input.text().strip(),
            "department": self.department_input.text().strip(),
            "year": self.year_input.value(),
            "section": self.section_input.currentText().strip().upper(),
            "password": self.password_input.text().strip(),
        }
        try:
            response = self.api_client.update_student(self.editing_roll_no, payload)
            message = response["message"]
        except BackendApiError:
            success, message = self.student_service.update_student_profile(self.editing_roll_no, payload)
            if not success:
                QMessageBox.warning(self, "Update Failed", message)
                return

        QMessageBox.information(self, "Student Updated", message)
        self._reset_form()
        self.load_students()
        self.student_registered.emit()

    def delete_student(self) -> None:
        target_roll_no = self.editing_roll_no
        if not target_roll_no:
            row = self.students_table.currentRow()
            if row >= 0:
                target_roll_no = self.students_table.item(row, 0).text()
        if not target_roll_no:
            QMessageBox.information(self, "No Selection", "Load or select a student before deleting.")
            return

        confirm = QMessageBox.question(self, "Delete Student", f"Delete student {target_roll_no}?")
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            response = self.api_client.delete_student(target_roll_no)
            message = response["message"]
        except BackendApiError:
            success, message = self.student_service.delete_student(target_roll_no)
            if not success:
                QMessageBox.warning(self, "Delete Failed", message)
                return

        QMessageBox.information(self, "Student Deleted", message)
        self._reset_form()
        self.load_students()
        self.student_registered.emit()

    def _reset_form(self) -> None:
        self.editing_roll_no = None
        self.current_frame = None
        self.roll_input.clear()
        self.name_input.clear()
        self.department_input.clear()
        self.year_input.setValue(1)
        self.section_input.setCurrentText("B1")
        self.password_input.clear()
        self.captured_paths.clear()
        self.progress.setValue(0)
        self.sample_info.setText(f"Captured samples: 0 / {FACE_SAMPLE_TARGET}")
