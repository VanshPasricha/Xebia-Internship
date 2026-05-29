"""Application-wide configuration values."""

from __future__ import annotations

import os
from pathlib import Path
import sys


APP_NAME = "FACETRACK"
APP_TAGLINE = "A Role-Based Smart Identity and Management System Using Face Recognition"
PROJECT_DIR = Path(__file__).resolve().parent.parent
RUNTIME_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else PROJECT_DIR
BASE_DIR = RUNTIME_DIR
DATA_DIR = RUNTIME_DIR / "data"
FACES_DIR = DATA_DIR / "faces"
DATABASE_PATH = DATA_DIR / "database.db"
LOGS_DIR = DATA_DIR / "logs"
LOG_FILE = LOGS_DIR / "facetrack.log"
THEME_STATE_PATH = DATA_DIR / "theme.json"

FACE_SAMPLE_TARGET = 15
FACE_SAMPLE_MAX = 20
FACE_DISTANCE_THRESHOLD = 0.52
CAMERA_INDEX = 0
FACULTY_DEFAULT_USERNAME = "admin"
FACULTY_DEFAULT_PASSWORD = "admin123"
FACULTY_DEFAULT_NAME = "Administrator"
BATCH_OPTIONS = [f"B{i}" for i in range(1, 97)]
BACKEND_API_BASE_URL = os.getenv("FACETRACK_BACKEND_API_URL", "http://127.0.0.1:8000/api")
BACKEND_API_TIMEOUT_SECONDS = float(os.getenv("FACETRACK_BACKEND_API_TIMEOUT_SECONDS", "0.6"))
BACKEND_API_ENABLED = os.getenv("FACETRACK_BACKEND_API_ENABLED", "0") == "1"
DEFAULT_THEME = "light"
THEME_OPTIONS = {"light", "dark"}


def _theme_palette(theme: str) -> dict[str, str]:
    if theme == "dark":
        return {
            "app_bg": "#08111f",
            "text": "#d9e5f2",
            "window_bg": "#08111f",
            "sidebar_bg_start": "#0f1b31",
            "sidebar_bg_mid": "#142846",
            "sidebar_bg_end": "#17375d",
            "sidebar_border": "#203552",
            "card_bg": "#101a2d",
            "card_border": "#213551",
            "hero_bg_start": "#15263f",
            "hero_bg_mid": "#214066",
            "hero_bg_end": "#1d5878",
            "hero_border": "#2a4c70",
            "brand_outer_start": "#67d8ff",
            "brand_outer_end": "#3a74ff",
            "brand_inner": "#eef4fb",
            "brand_initials": "#133156",
            "logo_text": "#f5f8fd",
            "logo_subtext": "#a8bed5",
            "sidebar_meta": "#92a9c3",
            "title": "#f0f5fb",
            "subtitle": "#96abc4",
            "hero_title": "#fbfdff",
            "hero_subtitle": "#c9d7e5",
            "eyebrow": "#7edcff",
            "metric_label": "#90a6c0",
            "metric_value": "#eff5fc",
            "metric_footnote": "#7f96b2",
            "tab_pane": "#101a2d",
            "tab_text": "#95a7bf",
            "tab_selected_bg": "#28476f",
            "tab_selected_text": "#f7fbff",
            "button_start": "#4c8fff",
            "button_end": "#27c3ff",
            "button_hover_start": "#3c7de7",
            "button_hover_end": "#1dafef",
            "button_disabled_bg": "#46566d",
            "button_disabled_text": "#bcc8d6",
            "secondary_bg": "#17253b",
            "secondary_text": "#e3ecf6",
            "secondary_border": "#2c4465",
            "secondary_hover": "#1a2e48",
            "danger_start": "#ad445c",
            "danger_end": "#d55b66",
            "ghost_bg": "#18283e",
            "ghost_text": "#edf5fe",
            "ghost_border": "#30435e",
            "input_bg": "#0d1626",
            "input_text": "#e7eef7",
            "input_border": "#2b3e58",
            "input_focus": "#50a8ff",
            "selection": "#378fff",
            "table_bg": "#0d1626",
            "table_alt_bg": "#112034",
            "table_border": "#213551",
            "gridline": "#1d2d43",
            "header_bg": "#132238",
            "header_text": "#9cb1c8",
            "header_border": "#263a55",
            "nav_text": "#e3ecf6",
            "nav_selected_bg": "#25466f",
            "nav_selected_border": "#3b6598",
            "progress_bg": "#0d1626",
            "progress_border": "#2b3e58",
            "progress_start": "#4d90ff",
            "progress_end": "#29c2ff",
            "scroll_handle": "#37506d",
        }

    return {
        "app_bg": "#fff2e6",
        "text": "#27364a",
        "window_bg": "#fff4eb",
        "sidebar_bg_start": "#fffefd",
        "sidebar_bg_mid": "#fffaf4",
        "sidebar_bg_end": "#fff5ec",
        "sidebar_border": "#f2dac1",
        "card_bg": "#fffdfb",
        "card_border": "#efd9c4",
        "hero_bg_start": "#fff1de",
        "hero_bg_mid": "#ffe9d5",
        "hero_bg_end": "#fff4e7",
        "hero_border": "#efd6b9",
        "brand_outer_start": "#ffd58c",
        "brand_outer_end": "#ffb15e",
        "brand_inner": "#fffdfa",
        "brand_initials": "#ae5b1d",
        "logo_text": "#28374d",
        "logo_subtext": "#7c8da3",
        "sidebar_meta": "#7f8ea0",
        "title": "#243349",
        "subtitle": "#7a8b9f",
        "hero_title": "#243349",
        "hero_subtitle": "#7f8ea1",
        "eyebrow": "#ff9d58",
        "metric_label": "#93a1b0",
        "metric_value": "#2e3b4f",
        "metric_footnote": "#8b98aa",
        "tab_pane": "#fffdf9",
        "tab_text": "#7b8b9f",
        "tab_selected_bg": "#ffe1b8",
        "tab_selected_text": "#9e5a1d",
        "button_start": "#ffca88",
        "button_end": "#ffad60",
        "button_hover_start": "#ffbf74",
        "button_hover_end": "#ffa14b",
        "button_disabled_bg": "#d4dbe3",
        "button_disabled_text": "#7e8d9d",
        "secondary_bg": "#ffffff",
        "secondary_text": "#48596f",
        "secondary_border": "#e6d4c3",
        "secondary_hover": "#fff5eb",
        "danger_start": "#ff9e8e",
        "danger_end": "#ff7d76",
        "ghost_bg": "#ffffff",
        "ghost_text": "#4a5a6f",
        "ghost_border": "#e5d3c1",
        "input_bg": "#fffdfa",
        "input_text": "#314056",
        "input_border": "#e7d7c7",
        "input_focus": "#ffb15d",
        "selection": "#ffc98b",
        "table_bg": "#fffdfb",
        "table_alt_bg": "#fff7f0",
        "table_border": "#ecd7c3",
        "gridline": "#f0e0d2",
        "header_bg": "#fff2e2",
        "header_text": "#7f6c58",
        "header_border": "#edd5bb",
        "nav_text": "#536173",
        "nav_selected_bg": "#ffe0b6",
        "nav_selected_border": "#ffbe72",
        "progress_bg": "#fff7f1",
        "progress_border": "#ead3bc",
        "progress_start": "#ffc47a",
        "progress_end": "#ff9c56",
        "scroll_handle": "#d8c1ad",
    }


def get_app_stylesheet(theme: str = DEFAULT_THEME) -> str:
    palette = _theme_palette(theme if theme in THEME_OPTIONS else DEFAULT_THEME)
    return f"""
QWidget {{
    background-color: {palette["app_bg"]};
    color: {palette["text"]};
    font-family: "Segoe UI Variable";
    font-size: 13px;
}}
QMainWindow, QDialog {{
    background: {palette["window_bg"]};
}}
QFrame#Sidebar {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {palette["sidebar_bg_start"]}, stop:0.55 {palette["sidebar_bg_mid"]}, stop:1 {palette["sidebar_bg_end"]});
    border: 1px solid {palette["sidebar_border"]};
    border-radius: 26px;
}}
QFrame#Card, QFrame#SectionCard, QFrame#MetricCard {{
    background: {palette["card_bg"]};
    border: 1px solid {palette["card_border"]};
    border-radius: 22px;
}}
QFrame#HeroCard {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {palette["hero_bg_start"]}, stop:0.55 {palette["hero_bg_mid"]}, stop:1 {palette["hero_bg_end"]});
    border: 1px solid {palette["hero_border"]};
    border-radius: 26px;
}}
QFrame#BrandMarkOuter {{
    min-width: 76px;
    min-height: 76px;
    max-width: 76px;
    max-height: 76px;
    border-radius: 24px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {palette["brand_outer_start"]}, stop:1 {palette["brand_outer_end"]});
}}
QFrame#BrandMarkInner {{
    background: {palette["brand_inner"]};
    border-radius: 18px;
}}
QLabel#BrandInitials {{
    color: {palette["brand_initials"]};
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 2px;
}}
QLabel#LogoText {{
    color: {palette["logo_text"]};
    font-size: 30px;
    font-weight: 800;
    letter-spacing: 1px;
    background: transparent;
}}
QLabel#LogoSubtext {{
    color: {palette["logo_subtext"]};
    font-size: 14px;
    font-weight: 600;
    background: transparent;
}}
QLabel#SidebarMeta {{
    color: {palette["sidebar_meta"]};
    font-size: 13px;
    background: transparent;
}}
QLabel#Title {{
    font-size: 28px;
    font-weight: 760;
    color: {palette["title"]};
    background: transparent;
}}
QLabel#Subtitle {{
    font-size: 13px;
    color: {palette["subtitle"]};
    background: transparent;
}}
QLabel#HeroTitle {{
    font-size: 30px;
    font-weight: 800;
    color: {palette["hero_title"]};
    background: transparent;
}}
QLabel#HeroSubtitle {{
    font-size: 14px;
    color: {palette["hero_subtitle"]};
    background: transparent;
}}
QLabel#Eyebrow {{
    color: {palette["eyebrow"]};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    background: transparent;
}}
QLabel#MetricLabel {{
    font-size: 12px;
    font-weight: 650;
    color: {palette["metric_label"]};
    background: transparent;
}}
QLabel#MetricValue {{
    font-size: 30px;
    font-weight: 800;
    color: {palette["metric_value"]};
    background: transparent;
}}
QLabel#MetricFootnote {{
    font-size: 12px;
    color: {palette["metric_footnote"]};
    background: transparent;
}}
QLabel#StrongText {{
    font-size: 18px;
    font-weight: 700;
    color: {palette["title"]};
    background: transparent;
}}
QTabWidget::pane {{
    border: 1px solid {palette["card_border"]};
    border-radius: 20px;
    top: -1px;
    background: {palette["tab_pane"]};
}}
QTabBar::tab {{
    background: transparent;
    color: {palette["tab_text"]};
    padding: 12px 18px;
    margin-right: 6px;
    border-radius: 14px;
    font-weight: 600;
}}
QTabBar::tab:selected {{
    background: {palette["tab_selected_bg"]};
    color: {palette["tab_selected_text"]};
}}
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {palette["button_start"]}, stop:1 {palette["button_end"]});
    color: white;
    border: none;
    border-radius: 16px;
    padding: 12px 18px;
    font-weight: 700;
}}
QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {palette["button_hover_start"]}, stop:1 {palette["button_hover_end"]});
}}
QPushButton:disabled {{
    background: {palette["button_disabled_bg"]};
    color: {palette["button_disabled_text"]};
}}
QPushButton[variant="secondary"] {{
    background: {palette["secondary_bg"]};
    color: {palette["secondary_text"]};
    border: 1px solid {palette["secondary_border"]};
}}
QPushButton[variant="secondary"]:hover,
QPushButton[variant="ghost"]:hover,
QPushButton[variant="theme"]:hover {{
    background: {palette["secondary_hover"]};
}}
QPushButton[variant="danger"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {palette["danger_start"]}, stop:1 {palette["danger_end"]});
}}
QPushButton[variant="ghost"], QPushButton[variant="theme"] {{
    background: {palette["ghost_bg"]};
    color: {palette["ghost_text"]};
    border: 1px solid {palette["ghost_border"]};
}}
QLineEdit, QComboBox, QSpinBox, QTimeEdit {{
    background: {palette["input_bg"]};
    color: {palette["input_text"]};
    border: 1px solid {palette["input_border"]};
    border-radius: 16px;
    padding: 10px 12px;
    selection-background-color: {palette["selection"]};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {{
    border: 1px solid {palette["input_focus"]};
}}
QTableWidget, QListWidget {{
    background: {palette["table_bg"]};
    alternate-background-color: {palette["table_alt_bg"]};
    border: 1px solid {palette["table_border"]};
    border-radius: 18px;
    gridline-color: {palette["gridline"]};
    outline: 0;
}}
QHeaderView::section {{
    background: {palette["header_bg"]};
    color: {palette["header_text"]};
    padding: 10px;
    border: none;
    border-bottom: 1px solid {palette["header_border"]};
    font-weight: 700;
}}
QListWidget#NavList {{
    background: transparent;
    border: none;
    color: {palette["nav_text"]};
    outline: 0;
}}
QListWidget#NavList::item {{
    padding: 14px 16px;
    border-radius: 16px;
    margin: 4px 0;
    font-size: 14px;
    font-weight: 600;
}}
QListWidget#NavList::item:selected {{
    background: {palette["nav_selected_bg"]};
    border: 1px solid {palette["nav_selected_border"]};
}}
QProgressBar {{
    border: 1px solid {palette["progress_border"]};
    border-radius: 12px;
    background: {palette["progress_bg"]};
    text-align: center;
    min-height: 12px;
    color: {palette["text"]};
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {palette["progress_start"]}, stop:1 {palette["progress_end"]});
    border-radius: 10px;
}}
QMessageBox {{
    background: {palette["card_bg"]};
}}
QScrollBar:vertical {{
    background: transparent;
    width: 12px;
    margin: 4px;
}}
QScrollBar::handle:vertical {{
    background: {palette["scroll_handle"]};
    border-radius: 6px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
    border: none;
}}
"""
