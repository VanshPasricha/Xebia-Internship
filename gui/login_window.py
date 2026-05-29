"""Role-based login window for admin, faculty, and students."""

from __future__ import annotations

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from client.api_client import BackendApiClient, BackendApiError
from database.db import db_manager
from database.models import FacultyUser
from gui.branding import ClassroomIllustration, FacetrackLogo, PortalHeader
from gui.faculty_dashboard import FacultyDashboard
from gui.student_dashboard import StudentDashboard
from services.student_service import StudentService
from utils.config import APP_NAME, FACULTY_DEFAULT_PASSWORD, FACULTY_DEFAULT_USERNAME
from utils.helpers import hash_password
from utils.theme import theme_manager


class LoginWindow(QDialog):
    """Authentication gateway that routes users to the correct dashboard."""

    def __init__(self) -> None:
        super().__init__()
        self.student_service = StudentService()
        self.api_client = BackendApiClient()
        self.setWindowTitle(f"{APP_NAME} Login")
        self.resize(1180, 700)
        self.active_window = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        banner = QFrame()
        banner.setObjectName("Sidebar")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(24, 24, 24, 24)
        banner_layout.setSpacing(16)

        banner_layout.addWidget(FacetrackLogo("Enterprise Academic Operations"))
        banner_layout.addWidget(
            PortalHeader(
                "Access control",
                "Admin manages faculty and timetable. Faculty manages attendance sessions.",
                "Students use a separate read-only portal. Attendance remains faculty-controlled through timetable-assigned classes.",
            )
        )

        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(10)
        stats_grid.setVerticalSpacing(10)
        for index, (label, value) in enumerate(
            [
                ("Admin Control", "Faculty + Timetable"),
                ("Faculty Role", "Attendance Only"),
                ("Class View", "Assigned Batches"),
                ("Student Role", "Read Only"),
            ]
        ):
            card = QFrame()
            card.setObjectName("MetricCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 12, 14, 12)
            caption = QLabel(label)
            caption.setObjectName("MetricLabel")
            metric = QLabel(value)
            metric.setObjectName("MetricValue")
            metric.setStyleSheet("font-size: 18px;")
            metric.setWordWrap(True)
            card_layout.addWidget(caption)
            card_layout.addWidget(metric)
            stats_grid.addWidget(card, index // 2, index % 2)
        banner_layout.addLayout(stats_grid)
        banner_layout.addStretch()

        tips = QFrame()
        tips.setObjectName("MetricCard")
        tips_layout = QVBoxLayout(tips)
        tips_layout.setContentsMargins(16, 16, 16, 16)
        tips_title = QLabel("Default Admin Access")
        tips_title.setObjectName("MetricLabel")
        tips_body = QLabel(
            f"Username: {FACULTY_DEFAULT_USERNAME}\nPassword: {FACULTY_DEFAULT_PASSWORD}\nRole: Admin"
        )
        tips_body.setObjectName("SidebarMeta")
        tips_layout.addWidget(tips_title)
        tips_layout.addWidget(tips_body)
        banner_layout.addWidget(tips)
        root.addWidget(banner, 11)

        form_shell = QFrame()
        form_shell.setObjectName("Card")
        form_layout = QVBoxLayout(form_shell)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(16)

        top_row = QHBoxLayout()
        top_row.addStretch()
        self.theme_button = QPushButton(theme_manager.toggle_label())
        self.theme_button.setProperty("variant", "theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        top_row.addWidget(self.theme_button)
        form_layout.addLayout(top_row)

        heading = QLabel("Sign In")
        heading.setObjectName("Title")
        helper = QLabel(
            "Use admin credentials for system control, faculty credentials for assigned classes, or student credentials for the read-only portal."
        )
        helper.setObjectName("Subtitle")
        helper.setWordWrap(True)
        form_layout.addWidget(heading)
        form_layout.addWidget(helper)

        tabs = QTabWidget()
        tabs.addTab(self._admin_login_tab(), "Admin Login")
        tabs.addTab(self._faculty_login_tab(), "Faculty Login")
        tabs.addTab(self._student_login_tab(), "Student Login")
        form_layout.addWidget(tabs)
        root.addWidget(form_shell, 9)

    def toggle_theme(self) -> None:
        theme_manager.toggle_theme()
        self.theme_button.setText(theme_manager.toggle_label())

    def closeEvent(self, event: QCloseEvent) -> None:
        app = QApplication.instance()
        super().closeEvent(event)
        if app is not None:
            app.quit()

    def _build_faculty_form(self, title: str, subtitle: str, button_text: str) -> tuple[QWidget, QLineEdit, QLineEdit, QPushButton]:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(PortalHeader("Institution console", title, subtitle))

        form_card = QFrame()
        form_card.setObjectName("SectionCard")
        form_card_layout = QVBoxLayout(form_card)
        form = QFormLayout()
        username_input = QLineEdit()
        username_input.setPlaceholderText("Enter username")
        password_input = QLineEdit()
        password_input.setPlaceholderText("Enter password")
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Username", username_input)
        form.addRow("Password", password_input)
        form_card_layout.addLayout(form)
        button = QPushButton(button_text)
        form_card_layout.addWidget(button)
        layout.addWidget(form_card)
        layout.addStretch()
        return tab, username_input, password_input, button

    def _admin_login_tab(self) -> QWidget:
        tab, self.admin_username, self.admin_password, button = self._build_faculty_form(
            "Admin access only.",
            "Admin registers faculty accounts, registers students, and assigns faculty inside timetable entries.",
            "Login as Admin",
        )
        button.clicked.connect(self.login_admin)
        return tab

    def _faculty_login_tab(self) -> QWidget:
        tab, self.faculty_username, self.faculty_password, button = self._build_faculty_form(
            "Faculty access only.",
            "Faculty accounts can only view their assigned timetable and run attendance for those classes.",
            "Login as Faculty",
        )
        button.clicked.connect(self.login_faculty)
        return tab

    def _student_login_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        layout.addWidget(
            PortalHeader(
                "Student portal",
                "Track attendance, timetable, and profile details.",
                "Students have secure read-only access with subject-wise attendance and red flag visibility.",
            )
        )

        form_card = QFrame()
        form_card.setObjectName("SectionCard")
        form_card_layout = QVBoxLayout(form_card)
        form = QFormLayout()
        self.student_roll_no = QLineEdit()
        self.student_roll_no.setPlaceholderText("Enter roll number")
        self.student_password = QLineEdit()
        self.student_password.setPlaceholderText("Enter password")
        self.student_password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Roll Number", self.student_roll_no)
        form.addRow("Password", self.student_password)
        form_card_layout.addLayout(form)
        button = QPushButton("Login as Student")
        button.clicked.connect(self.login_student)
        form_card_layout.addWidget(button)
        layout.addWidget(form_card)
        layout.addStretch()
        return tab

    def _open_dashboard(self, window: QWidget) -> None:
        self.active_window = window
        self.active_window.destroyed.connect(self._restore_login)
        self.active_window.showMaximized()
        self.hide()

    def _restore_login(self) -> None:
        self.active_window = None
        self.theme_button.setText(theme_manager.toggle_label())
        self.showMaximized()
        self.raise_()
        self.activateWindow()

    def _login_staff(self, username: str, password: str, expected_role: str) -> None:
        try:
            response = self.api_client.login(username, password, expected_role)
            user = response["user"]
            faculty_user = FacultyUser(
                id=user["id"],
                username=user["username"],
                name=user["name"],
                role=user["role"],
            )
            self._open_dashboard_safe(lambda: FacultyDashboard(faculty_user))
            return
        except BackendApiError:
            pass

        with db_manager.connection() as conn:
            row = conn.execute(
                "SELECT id, username, name, role FROM Faculty WHERE username = ? AND password = ?",
                (username, hash_password(password)),
            ).fetchone()
        if not row:
            QMessageBox.warning(self, "Login Failed", f"Invalid {expected_role} credentials.")
            return
        if row["role"] != expected_role:
            QMessageBox.warning(self, "Access Denied", f"This account is not allowed to log in through the {expected_role} portal.")
            return

        faculty_user = FacultyUser(
            id=row["id"],
            username=row["username"],
            name=row["name"],
            role=row["role"],
        )
        self._open_dashboard_safe(lambda: FacultyDashboard(faculty_user))

    def login_admin(self) -> None:
        self._login_staff(self.admin_username.text().strip(), self.admin_password.text().strip(), "admin")

    def login_faculty(self) -> None:
        self._login_staff(self.faculty_username.text().strip(), self.faculty_password.text().strip(), "faculty")

    def login_student(self) -> None:
        roll_no = self.student_roll_no.text().strip().upper()
        password = self.student_password.text().strip()
        try:
            response = self.api_client.login(roll_no, password, "student")
            user = response["user"]
            student = self.student_service.get_student_by_roll(user["roll_no"])
            if student:
                self._open_dashboard_safe(lambda: StudentDashboard(student))
                return
        except BackendApiError:
            pass

        student = self.student_service.authenticate_student(
            roll_no,
            password,
        )
        if not student:
            QMessageBox.warning(self, "Login Failed", "Invalid student credentials.")
            return

        self._open_dashboard_safe(lambda: StudentDashboard(student))

    def _open_dashboard_safe(self, window_factory) -> None:
        try:
            window = window_factory()
            self._open_dashboard(window)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Dashboard Error",
                f"The dashboard could not open after login.\n\n{exc}",
            )
