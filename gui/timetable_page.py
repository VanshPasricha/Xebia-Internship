"""Timetable management and viewing page."""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTime, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from client.api_client import BackendApiClient, BackendApiError
from services.faculty_service import FacultyService
from services.timetable_service import TimetableService
from utils.config import BATCH_OPTIONS


class TimetableWidget(QWidget):
    """Timetable page used in admin, faculty, and student dashboards."""

    timetable_updated = pyqtSignal()

    def __init__(self, faculty_username: str | None = None, read_only: bool = False, student_section: str | None = None) -> None:
        super().__init__()
        self.faculty_username = faculty_username
        self.read_only = read_only
        self.student_section = student_section
        self.service = TimetableService()
        self.faculty_service = FacultyService()
        self.api_client = BackendApiClient()
        self.editing_entry_id: int | None = None
        self._build_ui()
        self.load_entries()

    def _build_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(18)

        target_column = 0
        if not self.read_only:
            form_card = QFrame()
            form_card.setObjectName("Card")
            form_layout = QVBoxLayout(form_card)
            title = QLabel("Manage Timetable")
            title.setObjectName("Title")
            subtitle = QLabel("Admin publishes weekly classes, assigns the responsible faculty, and maps each class to a batch.")
            subtitle.setObjectName("Subtitle")
            subtitle.setWordWrap(True)
            form_layout.addWidget(title)
            form_layout.addWidget(subtitle)

            self.subject_input = QComboBox()
            self.subject_input.setEditable(True)
            self.day_input = QComboBox()
            self.day_input.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
            self.start_time = QTimeEdit()
            self.start_time.setDisplayFormat("HH:mm")
            self.end_time = QTimeEdit()
            self.end_time.setDisplayFormat("HH:mm")
            self.section_input = QComboBox()
            self.section_input.setEditable(True)
            self.section_input.addItems(BATCH_OPTIONS)
            self.faculty_input = QComboBox()
            self.faculty_input.setEditable(False)
            self._load_faculty_options()

            form = QFormLayout()
            form.addRow("Subject", self.subject_input)
            form.addRow("Assigned Faculty", self.faculty_input)
            form.addRow("Day", self.day_input)
            form.addRow("Start Time", self.start_time)
            form.addRow("End Time", self.end_time)
            form.addRow("Batch", self.section_input)
            form_layout.addLayout(form)

            button_row = QHBoxLayout()
            self.save_button = QPushButton("Add Timetable Entry")
            self.save_button.clicked.connect(self.save_entry)
            self.edit_button = QPushButton("Load Selected")
            self.edit_button.setProperty("variant", "secondary")
            self.edit_button.clicked.connect(self.load_selected_entry)
            self.delete_button = QPushButton("Delete Selected")
            self.delete_button.setProperty("variant", "danger")
            self.delete_button.clicked.connect(self.delete_selected_entry)
            self.reset_button = QPushButton("Reset")
            self.reset_button.setProperty("variant", "secondary")
            self.reset_button.clicked.connect(self.reset_form)
            for button in [self.save_button, self.edit_button, self.delete_button, self.reset_button]:
                button_row.addWidget(button)
            form_layout.addLayout(button_row)
            form_layout.addStretch()
            layout.addWidget(form_card, 0, 0)
            target_column = 1

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        title = QLabel("Weekly Timetable" if self.read_only else "Published Timetable")
        title.setObjectName("Title")
        if self.student_section:
            subtitle = QLabel("Read-only view filtered to the student's batch.")
        elif self.faculty_username and self.read_only:
            subtitle = QLabel("Read-only view filtered to the logged-in faculty account.")
        else:
            subtitle = QLabel("Students and faculty see timetable in read-only mode. Admin controls publishing.")
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)
        table_layout.addWidget(title)
        table_layout.addWidget(subtitle)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Subject", "Faculty", "Day", "Start", "End", "Batch"])
        self.table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.table)
        layout.addWidget(table_card, 0, target_column)

    def _load_faculty_options(self) -> None:
        self.faculty_input.clear()
        try:
            faculty_rows = self.api_client.list_faculty(include_admin=False)
            for faculty in faculty_rows:
                self.faculty_input.addItem(f"{faculty['name']} (@{faculty['username']})", faculty["username"])
            return
        except BackendApiError:
            pass

        faculty_rows = self.faculty_service.list_faculty(include_admin=False)
        for faculty in faculty_rows:
            self.faculty_input.addItem(f"{faculty.name} (@{faculty.username})", faculty.username)

    def save_entry(self) -> None:
        subject = self.subject_input.currentText().strip()
        section = self.section_input.currentText().strip().upper()
        faculty_username = str(self.faculty_input.currentData() or "").strip()
        if not subject or not section or not faculty_username:
            QMessageBox.warning(self, "Missing Fields", "Subject, assigned faculty, and batch are required.")
            return

        payload = {
            "subject": subject,
            "faculty": faculty_username,
            "day": self.day_input.currentText(),
            "start_time": self.start_time.time().toString("HH:mm"),
            "end_time": self.end_time.time().toString("HH:mm"),
            "section": section,
        }
        try:
            if self.editing_entry_id is None:
                response = self.api_client.create_timetable_entry(payload)
            else:
                response = self.api_client.update_timetable_entry(self.editing_entry_id, {**payload, "id": self.editing_entry_id})
            success = response["success"]
            message = response["message"]
        except BackendApiError:
            if self.editing_entry_id is None:
                success, message = self.service.create_entry(**payload)
            else:
                success, message = self.service.update_entry(entry_id=self.editing_entry_id, **payload)

        if not success:
            QMessageBox.warning(self, "Timetable Error", message)
            return

        QMessageBox.information(self, "Timetable Updated", message)
        self.reset_form()
        self.load_entries()
        self.timetable_updated.emit()

    def load_selected_entry(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Select a timetable row first.")
            return

        self.editing_entry_id = int(self.table.item(row, 0).data(Qt.ItemDataRole.UserRole))
        self.subject_input.setCurrentText(self.table.item(row, 0).text())
        faculty_username = self.table.item(row, 1).data(Qt.ItemDataRole.UserRole) or self.table.item(row, 1).text()
        faculty_index = self.faculty_input.findData(faculty_username)
        if faculty_index >= 0:
            self.faculty_input.setCurrentIndex(faculty_index)
        self.day_input.setCurrentText(self.table.item(row, 2).text())
        self.start_time.setTime(QTime.fromString(self.table.item(row, 3).text(), "HH:mm"))
        self.end_time.setTime(QTime.fromString(self.table.item(row, 4).text(), "HH:mm"))
        self.section_input.setCurrentText(self.table.item(row, 5).text())
        self.save_button.setText("Save Changes")

    def delete_selected_entry(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Select a timetable row first.")
            return

        entry_id = int(self.table.item(row, 0).data(Qt.ItemDataRole.UserRole))
        confirm = QMessageBox.question(self, "Delete Timetable", "Delete the selected timetable entry?")
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            response = self.api_client.delete_timetable_entry(entry_id)
            message = response["message"]
        except BackendApiError:
            success, message = self.service.delete_entry(entry_id)
            if not success:
                QMessageBox.warning(self, "Timetable Error", message)
                return

        QMessageBox.information(self, "Timetable Deleted", message)
        self.reset_form()
        self.load_entries()
        self.timetable_updated.emit()

    def reset_form(self) -> None:
        if self.read_only:
            return
        self.editing_entry_id = None
        self.subject_input.setCurrentText("")
        self.day_input.setCurrentIndex(0)
        self.section_input.setCurrentText("B1")
        if self.faculty_input.count() > 0:
            self.faculty_input.setCurrentIndex(0)
        self.save_button.setText("Add Timetable Entry")

    def load_entries(self) -> None:
        try:
            entries = self.api_client.get_timetable(
                faculty=self.faculty_username if self.faculty_username else None,
                section=self.student_section if self.student_section else None,
            )
            faculty_rows = self.api_client.list_faculty(include_admin=True)
            faculty_map = {faculty["username"]: faculty["name"] for faculty in faculty_rows}
        except BackendApiError:
            entries = self.service.list_entries(
                faculty=self.faculty_username if self.faculty_username else None,
                section=self.student_section if self.student_section else None,
            )
            faculty_map = {faculty.username: faculty.name for faculty in self.faculty_service.list_faculty(include_admin=True)}

        self.table.setRowCount(len(entries))
        for row_index, entry in enumerate(entries):
            entry_id = entry["id"] if isinstance(entry, dict) else entry.id
            subject = entry["subject"] if isinstance(entry, dict) else entry.subject
            faculty_username = entry["faculty"] if isinstance(entry, dict) else entry.faculty
            day = entry["day"] if isinstance(entry, dict) else entry.day
            start_time = entry["start_time"] if isinstance(entry, dict) else entry.start_time
            end_time = entry["end_time"] if isinstance(entry, dict) else entry.end_time
            section = entry["section"] if isinstance(entry, dict) else entry.section
            values = [
                subject,
                f"{faculty_map.get(faculty_username, faculty_username)} (@{faculty_username})",
                day,
                start_time,
                end_time,
                section,
            ]
            for col_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if col_index == 0:
                    item.setData(Qt.ItemDataRole.UserRole, entry_id)
                if col_index == 1:
                    item.setData(Qt.ItemDataRole.UserRole, faculty_username)
                self.table.setItem(row_index, col_index, item)
