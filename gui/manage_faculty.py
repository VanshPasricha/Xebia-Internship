"""Admin-only faculty management page."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from client.api_client import BackendApiClient, BackendApiError
from services.faculty_service import FacultyService


class ManageFacultyWidget(QWidget):
    """Admin-only faculty creation and listing interface."""

    faculty_updated = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.faculty_service = FacultyService()
        self.api_client = BackendApiClient()
        self._build_ui()
        self.load_faculty()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        title = QLabel("Register Faculty")
        title.setObjectName("Title")
        subtitle = QLabel("Admin creates faculty accounts. Only registered faculty members can log in and mark attendance.")
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)
        form_layout.addWidget(title)
        form_layout.addWidget(subtitle)

        self.name_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form = QFormLayout()
        form.addRow("Name", self.name_input)
        form.addRow("Username", self.username_input)
        form.addRow("Password", self.password_input)
        form_layout.addLayout(form)

        button_row = QHBoxLayout()
        self.save_button = QPushButton("Create Faculty Account")
        self.save_button.clicked.connect(self.create_faculty)
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setProperty("variant", "danger")
        self.delete_button.clicked.connect(self.delete_selected)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.delete_button)
        form_layout.addLayout(button_row)
        layout.addWidget(form_card)

        list_card = QFrame()
        list_card.setObjectName("Card")
        list_layout = QVBoxLayout(list_card)
        list_title = QLabel("Faculty Accounts")
        list_title.setObjectName("Title")
        list_subtitle = QLabel("Admin account is protected. Deleting a faculty account also removes timetable assignments for that account.")
        list_subtitle.setObjectName("Subtitle")
        list_subtitle.setWordWrap(True)
        list_layout.addWidget(list_title)
        list_layout.addWidget(list_subtitle)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Username", "Name", "Role", "Login Access"])
        self.table.horizontalHeader().setStretchLastSection(True)
        list_layout.addWidget(self.table)
        layout.addWidget(list_card)

    def load_faculty(self) -> None:
        try:
            faculty_rows = self.api_client.list_faculty(include_admin=True)
            mapped_rows = faculty_rows
            use_dict = True
        except BackendApiError:
            faculty_rows = self.faculty_service.list_faculty(include_admin=True)
            mapped_rows = faculty_rows
            use_dict = False
        self.table.setRowCount(len(faculty_rows))
        for row_index, faculty in enumerate(mapped_rows):
            role = faculty["role"] if use_dict else faculty.role
            username = faculty["username"] if use_dict else faculty.username
            name = faculty["name"] if use_dict else faculty.name
            access = "Attendance + timetable view" if role == "faculty" else "Admin controls"
            values = [username, name, role.title(), access]
            for col_index, value in enumerate(values):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def create_faculty(self) -> None:
        try:
            response = self.api_client.create_faculty(
                self.name_input.text().strip(),
                self.username_input.text().strip(),
                self.password_input.text().strip(),
                role="faculty",
            )
            message = response["message"]
        except BackendApiError:
            success, message = self.faculty_service.create_faculty(
                self.name_input.text().strip(),
                self.username_input.text().strip(),
                self.password_input.text().strip(),
                role="faculty",
            )
            if not success:
                QMessageBox.warning(self, "Faculty Error", message)
                return

        QMessageBox.information(self, "Faculty Added", message)
        self.name_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.load_faculty()
        self.faculty_updated.emit()

    def delete_selected(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Select a faculty account first.")
            return

        username = self.table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Delete Faculty", f"Delete faculty account {username}?")
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            response = self.api_client.delete_faculty(username)
            message = response["message"]
        except BackendApiError:
            success, message = self.faculty_service.delete_faculty(username)
            if not success:
                QMessageBox.warning(self, "Faculty Error", message)
                return

        QMessageBox.information(self, "Faculty Removed", message)
        self.load_faculty()
        self.faculty_updated.emit()
