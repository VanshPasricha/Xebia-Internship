"""Admin and faculty main window with role-based navigation."""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from client.api_client import BackendApiClient, BackendApiError
from gui.attendance_page import AttendanceWidget
from gui.branding import FacetrackLogo, PortalHeader
from gui.manage_faculty import ManageFacultyWidget
from gui.register_student import RegisterStudentWidget
from gui.timetable_page import TimetableWidget
from services.attendance_service import AttendanceService
from services.faculty_service import FacultyService
from services.student_service import StudentService
from services.timetable_service import TimetableService
from utils.theme import theme_manager

LOGGER = logging.getLogger(__name__)


class DashboardHome(QWidget):
    """Overview cards for the landing page."""

    def __init__(self, faculty_user) -> None:
        super().__init__()
        self.faculty_user = faculty_user
        self.student_service = StudentService()
        self.faculty_service = FacultyService()
        self.timetable_service = TimetableService()
        self.attendance_service = AttendanceService()
        self.api_client = BackendApiClient()
        self.cards: dict[str, QLabel] = {}
        self._build_ui()
        self.refresh()

    def _metric_card(self, label_text: str, footnote: str) -> QFrame:
        card = QFrame()
        card.setObjectName("MetricCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        label = QLabel(label_text)
        label.setObjectName("MetricLabel")
        value = QLabel("0")
        value.setObjectName("MetricValue")
        note = QLabel(footnote)
        note.setObjectName("MetricFootnote")
        note.setWordWrap(True)
        self.cards[label_text] = value
        card_layout.addWidget(label)
        card_layout.addWidget(value)
        card_layout.addWidget(note)
        return card

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)

        role_title = "Admin control center" if self.faculty_user.role == "admin" else "Faculty command center"
        role_subtitle = (
            "Register faculty, register students, assign faculty to timetable entries, and review attendance state across the system."
            if self.faculty_user.role == "admin"
            else "Review your assigned timetable and run attendance only for classes assigned to your faculty account."
        )
        hero = PortalHeader("Role-based operations", f"Welcome back, {self.faculty_user.name}", role_subtitle)
        layout.addWidget(hero)

        metrics = QGridLayout()
        metrics.setHorizontalSpacing(16)
        metrics.setVerticalSpacing(16)
        metric_specs = (
            [
                ("Faculty Accounts", "Admin-managed faculty access"),
                ("Total Students", "All registered student profiles"),
                ("Today's Classes", "All classes scheduled for today"),
                ("Attendance Records", "Recorded attendance history"),
            ]
            if self.faculty_user.role == "admin"
            else [
                ("My Classes Today", "Assigned classes scheduled today"),
                ("Total Students", "Available registered students"),
                ("Attendance Records", "Historical present and absent logs"),
                ("Late Students", "Students with recorded late flags"),
            ]
        )
        for index, (label, footnote) in enumerate(metric_specs):
            metrics.addWidget(self._metric_card(label, footnote), index // 2, index % 2)
        layout.addLayout(metrics)

        overview_card = QFrame()
        overview_card.setObjectName("Card")
        overview_layout = QVBoxLayout(overview_card)
        overview_layout.setContentsMargins(22, 22, 22, 22)
        table_title = QLabel("Late Students Overview" if self.faculty_user.role == "faculty" else "Today's Scheduled Classes")
        table_title.setObjectName("Title")
        table_subtitle = QLabel(
            "Late flags are shown per student." if self.faculty_user.role == "faculty" else "Admin view of all timetable entries scheduled for the current day."
        )
        table_subtitle.setObjectName("Subtitle")
        table_subtitle.setWordWrap(True)
        overview_layout.addWidget(table_title)
        overview_layout.addWidget(table_subtitle)

        if self.faculty_user.role == "admin":
            self.detail_table = QTableWidget(0, 5)
            self.detail_table.setHorizontalHeaderLabels(["Subject", "Faculty", "Day", "Time", "Batch"])
        else:
            self.detail_table = QTableWidget(0, 5)
            self.detail_table.setHorizontalHeaderLabels(["Roll Number", "Name", "Batch", "Current Red Flags", "Total Late Flags"])
        self.detail_table.horizontalHeader().setStretchLastSection(True)
        overview_layout.addWidget(self.detail_table)
        layout.addWidget(overview_card)
        layout.addStretch()

    def refresh(self) -> None:
        try:
            late_rows = self.api_client.get_late_flag_report()
            total_students = len(self.api_client.list_students())
            total_records = len(self.api_client.get_attendance_records())
            if self.faculty_user.role == "admin":
                today_rows = self.api_client.get_today_classes()
                faculty_count = len(self.api_client.list_faculty(include_admin=False))
            else:
                today_rows = self.api_client.get_today_classes(self.faculty_user.username)
                faculty_count = None
        except BackendApiError:
            late_rows = self.attendance_service.get_late_student_report()
            total_students = len(self.student_service.list_students())
            total_records = self.attendance_service.count_total_records()
            if self.faculty_user.role == "admin":
                today_rows = self.timetable_service.get_today_classes(None)
                faculty_count = self.faculty_service.count_faculty(include_admin=False)
            else:
                today_rows = self.timetable_service.get_today_classes(self.faculty_user.username)
                faculty_count = None

        if self.faculty_user.role == "admin":
            self.cards["Faculty Accounts"].setText(str(faculty_count))
            self.cards["Total Students"].setText(str(total_students))
            self.cards["Today's Classes"].setText(str(len(today_rows)))
            self.cards["Attendance Records"].setText(str(total_records))

            self.detail_table.setRowCount(len(today_rows))
            for row_index, entry in enumerate(today_rows):
                if isinstance(entry, dict):
                    values = [entry["subject"], entry["faculty"], entry["day"], f"{entry['start_time']}-{entry['end_time']}", entry["section"]]
                else:
                    values = [entry.subject, entry.faculty, entry.day, f"{entry.start_time}-{entry.end_time}", entry.section]
                for col_index, value in enumerate(values):
                    self.detail_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
        else:
            self.cards["My Classes Today"].setText(str(len(today_rows)))
            self.cards["Total Students"].setText(str(total_students))
            self.cards["Attendance Records"].setText(str(total_records))
            self.cards["Late Students"].setText(str(len(late_rows)))

            self.detail_table.setRowCount(len(late_rows))
            for row_index, row in enumerate(late_rows):
                values = [row["roll_no"], row["name"], row.get("section", "-"), row["red_flags"], row["total_late_flags"]]
                for col_index, value in enumerate(values):
                    self.detail_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))


class ReportsWidget(QWidget):
    """Attendance reporting page with CSV export."""

    def __init__(self) -> None:
        super().__init__()
        self.attendance_service = AttendanceService()
        self.api_client = BackendApiClient()
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)

        header = QFrame()
        header.setObjectName("Card")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(22, 22, 22, 22)
        copy = QVBoxLayout()
        title = QLabel("Attendance Reports")
        title.setObjectName("Title")
        subtitle = QLabel("Review attendance history, late flags, and export clean CSV reports for administration.")
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)
        copy.addWidget(title)
        copy.addWidget(subtitle)
        header_layout.addLayout(copy)
        self.export_button = QPushButton("Export CSV")
        self.export_button.clicked.connect(self.export_csv)
        header_layout.addWidget(self.export_button, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(header)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Roll Number", "Name", "Subject", "Date", "Time", "Status", "Late Flags"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def refresh(self) -> None:
        try:
            records = self.api_client.get_attendance_records()
            values_list = [
                [record["roll_no"], record["name"], record["subject"], record["date"], record["time"], record["status"], record["late_flags"]]
                for record in records
            ]
        except BackendApiError:
            records = self.attendance_service.get_records()
            values_list = [
                [record.roll_no, record.name, record.subject, record.date, record.time, record.status, record.late_flags]
                for record in records
            ]
        self.table.setRowCount(len(records))
        for row_index, values in enumerate(values_list):
            for col_index, value in enumerate(values):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def export_csv(self) -> None:
        records = self.attendance_service.get_records()
        if not records:
            QMessageBox.information(self, "No Records", "There are no attendance records to export.")
            return

        default_name = Path.cwd() / "data" / "attendance_report.csv"
        output, _ = QFileDialog.getSaveFileName(self, "Export Attendance CSV", str(default_name), "CSV Files (*.csv)")
        if not output:
            return

        path = self.attendance_service.export_to_csv(output, records)
        QMessageBox.information(self, "Export Complete", f"Attendance exported to:\n{path}")


class FacultyDashboard(QMainWindow):
    """Main admin/faculty desktop experience."""

    def __init__(self, faculty_user) -> None:
        super().__init__()
        self.faculty_user = faculty_user
        self.setWindowTitle(f"FACETRACK - {faculty_user.role.title()} Dashboard")
        self.resize(1360, 820)
        self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.pages: list[QWidget] = []
        self.page_keys: list[str] = []
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
        sidebar_layout.addWidget(FacetrackLogo(f"{self.faculty_user.role.title()} Workspace"))

        info_card = QFrame()
        info_card.setObjectName("MetricCard")
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(18, 18, 18, 18)
        portal_label = QLabel("Signed in as")
        portal_label.setObjectName("MetricLabel")
        info_name = QLabel(self.faculty_user.name)
        info_name.setObjectName("StrongText")
        info_meta = QLabel(f"@{self.faculty_user.username}\nRole: {self.faculty_user.role.title()}")
        info_meta.setObjectName("SidebarMeta")
        info_meta.setWordWrap(True)
        info_layout.addWidget(portal_label)
        info_layout.addWidget(info_name)
        info_layout.addWidget(info_meta)
        sidebar_layout.addWidget(info_card)

        self.theme_button = QPushButton(theme_manager.toggle_label())
        self.theme_button.setProperty("variant", "theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.theme_button)

        self.nav = QListWidget()
        self.nav.setObjectName("NavList")
        self.nav.currentRowChanged.connect(self._switch_page)
        sidebar_layout.addWidget(self.nav, 1)

        self.logout_button = QPushButton("Logout")
        self.logout_button.setProperty("variant", "ghost")
        self.logout_button.clicked.connect(self.close)
        sidebar_layout.addWidget(self.logout_button)
        layout.addWidget(sidebar)

        self.stack = QStackedWidget()
        self.home_page = DashboardHome(self.faculty_user)
        self.reports_page = ReportsWidget()
        self._add_page("dashboard", "Dashboard", self.home_page)

        if self.faculty_user.role == "admin":
            self.register_page = RegisterStudentWidget()
            self.manage_faculty_page = ManageFacultyWidget()
            self.timetable_page = TimetableWidget(read_only=False)
            self._add_page("students", "Register Student", self.register_page)
            self._add_page("faculty", "Manage Faculty", self.manage_faculty_page)
            self._add_page("timetable", "Timetable", self.timetable_page)
            self._add_page("reports", "Reports", self.reports_page)

            self.register_page.student_registered.connect(self.refresh_all)
            self.manage_faculty_page.faculty_updated.connect(self.refresh_all)
            self.timetable_page.timetable_updated.connect(self.refresh_all)
        else:
            self.attendance_page = AttendanceWidget(self.faculty_user.username)
            self.timetable_page = TimetableWidget(faculty_username=self.faculty_user.username, read_only=True)
            self._add_page("attendance", "Attendance", self.attendance_page)
            self._add_page("timetable", "Timetable", self.timetable_page)
            self._add_page("reports", "Reports", self.reports_page)

        layout.addWidget(self.stack, 1)
        self.nav.setCurrentRow(0)

    def _add_page(self, key: str, label: str, widget: QWidget) -> None:
        self.page_keys.append(key)
        self.pages.append(widget)
        QListWidgetItem(label, self.nav)
        self.stack.addWidget(widget)

    def _switch_page(self, index: int) -> None:
        if index < 0:
            return
        self.stack.setCurrentIndex(index)
        current_key = self.page_keys[index]
        if current_key in {"dashboard", "attendance", "reports", "timetable"}:
            self.refresh_all()

    def refresh_all(self) -> None:
        try:
            self.home_page.refresh()
            self.reports_page.refresh()
            if hasattr(self, "attendance_page"):
                self.attendance_page.load_today_classes()
            if hasattr(self, "timetable_page"):
                self.timetable_page.load_entries()
        except Exception as exc:
            LOGGER.exception("Dashboard refresh failed")
            QMessageBox.warning(self, "Refresh Error", f"The dashboard could not refresh fully.\n\n{exc}")

    def toggle_theme(self) -> None:
        theme_manager.toggle_theme()
        self.theme_button.setText(theme_manager.toggle_label())

