"""Reusable FACETRACK branding widgets for the desktop portal."""

from __future__ import annotations

from pathlib import Path
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget
from utils.config import BASE_DIR

try:
    from PyQt6.QtSvgWidgets import QSvgWidget
except ImportError:  # pragma: no cover
    QSvgWidget = None


def _candidate_asset_dirs() -> list[Path]:
    module_assets = Path(__file__).resolve().parent / "assets"
    runtime_assets = BASE_DIR / "gui" / "assets"
    candidates = [runtime_assets, module_assets]
    if getattr(sys, "frozen", False):
        meipass = Path(getattr(sys, "_MEIPASS", BASE_DIR))
        candidates.insert(0, meipass / "gui" / "assets")

    unique: list[Path] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique


def _resolve_asset(filename: str) -> Path:
    for asset_dir in _candidate_asset_dirs():
        asset_path = asset_dir / filename
        if asset_path.exists():
            return asset_path
    return _candidate_asset_dirs()[0] / filename


LOGO_ASSET = _resolve_asset("facetrack_logo.svg")
CLASSROOM_ASSET = _resolve_asset("classroom_scene.svg")


class _SvgPanel(QWidget):
    def __init__(self, asset_path: Path, fixed_height: int | None = None, fixed_width: int | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        if QSvgWidget is not None and asset_path.exists():
            widget = QSvgWidget(str(asset_path))
            if fixed_height is not None:
                widget.setFixedHeight(fixed_height)
            if fixed_width is not None:
                widget.setFixedWidth(fixed_width)
            layout.addWidget(widget)
        else:
            fallback = QLabel(asset_path.stem.replace("_", " ").title())
            fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(fallback)


class FacetrackLogo(QWidget):
    """Branded logo used in portal sidebars and auth screens."""

    def __init__(self, subtitle: str = "Smart Identity Portal", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(_SvgPanel(LOGO_ASSET, fixed_height=92, fixed_width=92), alignment=Qt.AlignmentFlag.AlignLeft)

        title = QLabel("FACETRACK")
        title.setObjectName("LogoText")
        strap = QLabel("Role-Based Smart Identity And Attendance")
        strap.setObjectName("LogoSubtext")
        strap.setWordWrap(True)
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("SidebarMeta")
        subtitle_label.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(strap)
        layout.addWidget(subtitle_label)


class ClassroomIllustration(QWidget):
    """Asset-backed classroom hero image for the login panel."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(_SvgPanel(CLASSROOM_ASSET, fixed_height=340))


class PortalHeader(QFrame):
    """Top-level brand block for hero sections."""

    def __init__(self, eyebrow: str, title: str, subtitle: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HeroCard")
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        eyebrow_label = QLabel(eyebrow)
        eyebrow_label.setObjectName("Eyebrow")
        title_label = QLabel(title)
        title_label.setObjectName("HeroTitle")
        title_label.setWordWrap(True)
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("HeroSubtitle")
        subtitle_label.setWordWrap(True)

        layout.addWidget(eyebrow_label)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
