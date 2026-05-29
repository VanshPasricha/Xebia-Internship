"""App-wide theme management for FACETRACK."""

from __future__ import annotations

import json

from PyQt6.QtWidgets import QApplication

from utils.config import DEFAULT_THEME, THEME_OPTIONS, THEME_STATE_PATH, get_app_stylesheet


class ThemeManager:
    """Persist and apply light/dark theme state across the desktop app."""

    def __init__(self) -> None:
        self.current_theme = self.load_theme()

    def load_theme(self) -> str:
        try:
            if THEME_STATE_PATH.exists():
                payload = json.loads(THEME_STATE_PATH.read_text(encoding="utf-8"))
                theme = payload.get("theme", DEFAULT_THEME)
                if theme in THEME_OPTIONS:
                    return theme
        except Exception:
            pass
        return DEFAULT_THEME

    def save_theme(self, theme: str) -> None:
        THEME_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        THEME_STATE_PATH.write_text(json.dumps({"theme": theme}), encoding="utf-8")

    def apply_theme(self, theme: str | None = None) -> str:
        next_theme = theme or self.current_theme
        if next_theme not in THEME_OPTIONS:
            next_theme = DEFAULT_THEME

        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(get_app_stylesheet(next_theme))

        self.current_theme = next_theme
        self.save_theme(next_theme)
        return next_theme

    def toggle_theme(self) -> str:
        next_theme = "light" if self.current_theme == "dark" else "dark"
        return self.apply_theme(next_theme)

    def toggle_label(self) -> str:
        return "Switch To Dark" if self.current_theme == "light" else "Switch To Light"


theme_manager = ThemeManager()
