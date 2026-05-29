"""Student main window with read-only academic data."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from client.api_client import BackendApiClient, BackendApiError
from gui.branding import FacetrackLogo, PortalHeader
from gui.timetable_page import TimetableWidget
from services.attendance_service import AttendanceService
from services.student_service import StudentService
from utils.theme import theme_manager


class StudentHomePage(QWidget):
    """Overview dashboard for the student role."""

    def __init__(self, student) -> None:
        super().__init__()
        self.student = student
        self.student_service = StudentService()
        self.api_client = BackendApiClient()
        self._build_ui()
        self.refresh()

    def _metric_card(self, label_text: str, footnote: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setObjectName("MetricCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        label = QLabel(label_text)
        label.setObjectName("MetricLabel")
        value = QLabel("0")
        value.setObjectName("MetricValue")
        note = QLabel(footnote)
        note.setObjectName("MetricFootnote")
        note.setWordWrap(True)
        layout.addWidget(label)
        layout.addWidget(value)
        layout.addWidget(note)
        return card, value

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)

        hero = PortalHeader(
            "Student snapshot",
            f"{self.student.name} | {self.student.roll_no}",
            f"{self.student.department} | Year {self.student.year} | Batch {self.student.section}",
        )
        layout.addWidget(hero)

        stats = QGridLayout()
        stats.setHorizontalSpacing(16)
        attendance_card, self.percent_label = self._metric_card(
            "Attendance Percentage", "Calculated after red-flag deductions are applied."
        )
        red_flag_card, self.red_flag_value = self._metric_card(
            "Total Red Flags", "Every 60 red flags become 1 attendance deduction."
        )
        stats.addWidget(attendance_card, 0, 0)
        stats.addWidget(red_flag_card, 0, 1)
        layout.addLayout(stats)

        tracker = QFrame()
        tracker.setObjectName("Card")
        tracker_layout = QVBoxLayout(tracker)
        tracker_title = QLabel("Attendance Tracker")
        tracker_title.setObjectName("Title")
        tracker_subtitle = QLabel("A quick visual of your current attendance standing across recorded classes.")
        tracker_subtitle.setObjectName("Subtitle")
        tracker_subtitle.setWordWrap(True)
        self.progress = QProgressBar()
        self.progress.setFormat("%p%")
        tracker_layout.addWidget(tracker_title)
        tracker_layout.addWidget(tracker_subtitle)
        tracker_layout.addWidget(self.progress)
        layout.addWidget(tracker)
        layout.addStretch()

    def refresh(self) -> None:
        """Update attendance percentage widgets."""
        try:
            current_student = self.api_client.get_student(self.student.roll_no)
            summary = self.api_client.get_student_attendance_summary(self.student.roll_no)
            self.red_flag_value.setText(str(current_student["red_flags"]))
            overall = summary["overall_percentage"]
        except BackendApiError:
            current_student = self.student_service.get_student_by_roll(self.student.roll_no)
            if current_student:
                self.student = current_student
                self.red_flag_value.setText(str(current_student.red_flags))
            overall, _ = self.student_service.get_attendance_summary(self.student.roll_no)
        self.percent_label.setText(f"{overall}%")
        self.progress.setValue(int(overall))


class StudentAttendancePage(QWidget):
    """Read-only attendance list and subject summary."""

    def __init__(self, student) -> None:
        super().__init__()
        self.student = student
        self.student_service = StudentService()
        self.attendance_service = AttendanceService()
        self.api_client = BackendApiClient()
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)

        summary_card = QFrame()
        summary_card.setObjectName("Card")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(22, 22, 22, 22)
        title = QLabel("Subject-wise Attendance And Flags")
        title.setObjectName("Title")
        subtitle = QLabel("Each subject automatically appears from timetable publishing and attendance history.")
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)
        summary_layout.addWidget(title)
        summary_layout.addWidget(subtitle)
        self.summary_table = QTableWidget(0, 5)
        self.summary_table.setHorizontalHeaderLabels(["Subject", "Present", "Total Classes", "Attendance %", "Red Flags"])
        self.summary_table.horizontalHeader().setStretchLastSection(True)
        summary_layout.addWidget(self.summary_table)
        layout.addWidget(summary_card)

        records_card = QFrame()
        records_card.setObjectName("Card")
        records_layout = QVBoxLayout(records_card)
        records_layout.setContentsMargins(22, 22, 22, 22)
        records_title = QLabel("Attendance Log")
        records_title.setObjectName("Title")
        records_subtitle = QLabel("Detailed session record with per-class late flags.")
        records_subtitle.setObjectName("Subtitle")
        records_subtitle.setWordWrap(True)
        records_layout.addWidget(records_title)
        records_layout.addWidget(records_subtitle)
        self.records_table = QTableWidget(0, 6)
        self.records_table.setHorizontalHeaderLabels(["Subject", "Date", "Time", "Status", "Late Flags", "Roll Number"])
        self.records_table.horizontalHeader().setStretchLastSection(True)
        records_layout.addWidget(self.records_table)
        layout.addWidget(records_card)

    def refresh(self) -> None:
        """Load the student's attendance summary and raw records."""
        try:
            summary = self.api_client.get_student_attendance_summary(self.student.roll_no)
            summary_rows = summary["subject_summaries"]
            records = self.api_client.get_attendance_records(roll_no=self.student.roll_no)
            summary_values = [
                [item["subject"], item["present"], item["total"], item["percentage"], item["late_flags"]]
                for item in summary_rows
            ]
            record_values = [
                [record["subject"], record["date"], record["time"], record["status"], record["late_flags"], record["roll_no"]]
                for record in records
            ]
        except BackendApiError:
            _, summary_rows = self.student_service.get_attendance_summary(self.student.roll_no)
            records = self.attendance_service.get_records(roll_no=self.student.roll_no)
            summary_values = [
                [item.subject, item.present, item.total, item.percentage, item.late_flags]
                for item in summary_rows
            ]
            record_values = [
                [record.subject, record.date, record.time, record.status, record.late_flags, record.roll_no]
                for record in records
            ]

        self.summary_table.setRowCount(len(summary_values))
        for row_index, values in enumerate(summary_values):
            for col_index, value in enumerate(values):
                self.summary_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        self.records_table.setRowCount(len(record_values))
        for row_index, values in enumerate(record_values):
            for col_index, value in enumerate(values):
                self.records_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))


class StudentProfilePage(QWidget):
    """Read-only student profile card."""

    def __init__(self, student) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        hero = PortalHeader(
            "Profile overview",
            "Academic identity card",
            "Read-only details pulled from the student registration record maintained by faculty.",
        )
        layout.addWidget(hero)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        for label_text, value in [
            ("Roll Number", student.roll_no),
            ("Name", student.name),
            ("Department", student.department),
            ("Year", str(student.year)),
            ("Batch", student.section),
        ]:
            row = QFrame()
            row.setObjectName("MetricCard")
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(16, 14, 16, 14)
            label = QLabel(label_text)
            label.setObjectName("MetricLabel")
            content = QLabel(value)
            content.setObjectName("StrongText")
            row_layout.addWidget(label)
            row_layout.addWidget(content)
            card_layout.addWidget(row)
        layout.addWidget(card)
        layout.addStretch()


class StudentDashboard(QMainWindow):
    """Read-only dashboard experience for students."""

    def __init__(self, student) -> None:
        super().__init__()
        self.student = student
        self.setWindowTitle("FACETRACK - Student Dashboard")
        self.resize(1360, 820)
        self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(260)
        sidebar.setMaximumWidth(320)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(22, 22, 22, 22)
        sidebar_layout.setSpacing(16)
        sidebar_layout.addWidget(FacetrackLogo("Student Experience Portal"))

        meta_card = QFrame()
        meta_card.setObjectName("MetricCard")
        meta_layout = QVBoxLayout(meta_card)
        meta_layout.setContentsMargins(18, 18, 18, 18)
        heading = QLabel("Logged in student")
        heading.setObjectName("MetricLabel")
        name = QLabel(self.student.name)
        name.setObjectName("StrongText")
        details = QLabel(f"{self.student.roll_no}\nBatch {self.student.section}\nRead-only academic access")
        details.setObjectName("SidebarMeta")
        details.setWordWrap(True)
        meta_layout.addWidget(heading)
        meta_layout.addWidget(name)
        meta_layout.addWidget(details)
        sidebar_layout.addWidget(meta_card)

        self.theme_button = QPushButton(theme_manager.toggle_label())
        self.theme_button.setProperty("variant", "theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.theme_button)

        self.nav = QListWidget()
        self.nav.setObjectName("NavList")
        for item in ["Dashboard", "Attendance", "Timetable", "Profile"]:
            QListWidgetItem(item, self.nav)
        self.nav.currentRowChanged.connect(self._switch_page)
        sidebar_layout.addWidget(self.nav, 1)

        self.logout_button = QPushButton("Logout")
        self.logout_button.setProperty("variant", "ghost")
        self.logout_button.clicked.connect(self.close)
        sidebar_layout.addWidget(self.logout_button)
        layout.addWidget(sidebar)

        self.stack = QStackedWidget()
        self.home_page = StudentHomePage(self.student)
        self.attendance_page = StudentAttendancePage(self.student)
        self.timetable_page = TimetableWidget(read_only=True, student_section=self.student.section)
        self.profile_page = StudentProfilePage(self.student)
        for widget in [self.home_page, self.attendance_page, self.timetable_page, self.profile_page]:
            self.stack.addWidget(widget)
        layout.addWidget(self.stack, 1)
        self.nav.setCurrentRow(0)

    def _switch_page(self, index: int) -> None:
        """Navigate between student pages and refresh dynamic pages."""
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.home_page.refresh()
        elif index == 1:
            self.attendance_page.refresh()

    def toggle_theme(self) -> None:
        theme_manager.toggle_theme()
        self.theme_button.setText(theme_manager.toggle_label())

