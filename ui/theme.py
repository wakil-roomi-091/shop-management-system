"""
Shared design system for the app: color palette, shadow/panel helpers,
and small reusable styled widgets.

Centralizing this here means every module (Dashboard, Products, Sales,
Reports, Settings) renders with the same look without copy-pasting
styling code into each file - and a future palette/spacing change only
has to happen in one place.
"""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


class Palette:
    WHITE = "#FFFFFF"
    BG = "#F8FAFC"
    BORDER = "#E2E8F0"
    PRIMARY = "#2563EB"
    SUCCESS = "#16A34A"
    WARNING = "#F59E0B"
    DANGER = "#DC2626"
    TEXT_DARK = "#0F172A"
    TEXT_MUTED = "#64748B"
    TEXT_LABEL = "#475569"


def rgba(hex_color, alpha):
    """Convert a #RRGGBB hex string to a CSS rgba() string, e.g. for badge backgrounds."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def darken(hex_color, factor=0.85):
    """Return a darker variant of a #RRGGBB color, for hover/pressed button states."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, int(c * factor)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def make_shadow(blur=16, y_offset=3, alpha=25):
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(15, 23, 42, alpha))
    return effect


def panel_frame(title=None):
    """A white, rounded, shadowed container. Returns (frame, content_layout)
    so callers just addWidget/addLayout into content_layout."""
    frame = QFrame()
    frame.setObjectName("panel")
    frame.setStyleSheet(f"""
        QFrame#panel {{
            background-color: {Palette.WHITE};
            border: 1px solid {Palette.BORDER};
            border-radius: 16px;
        }}
    """)
    frame.setGraphicsEffect(make_shadow(blur=14, y_offset=2))

    outer = QVBoxLayout(frame)
    outer.setContentsMargins(20, 18, 20, 18)
    outer.setSpacing(12)

    if title:
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {Palette.TEXT_DARK};")
        outer.addWidget(title_label)

    return frame, outer


def status_badge_style(color):
    """The raw stylesheet string behind a badge, for callers that need to
    apply it to their own QLabel (e.g. wrapped so it doesn't stretch to
    fill a table cell) instead of using make_badge() directly."""
    return f"""
        font-size: 11px;
        font-weight: 700;
        color: {color};
        background-color: {rgba(color, 0.12)};
        border-radius: 10px;
        padding: 4px 10px;
    """


def make_badge(text, color):
    """A small rounded pill badge - e.g. for stock status or low-stock counts."""
    badge = QLabel(text)
    badge.setAlignment(Qt.AlignCenter)
    badge.setStyleSheet(status_badge_style(color))
    return badge


def page_title_label(text):
    """Large page heading, e.g. 'Product Management'."""
    label = QLabel(text)
    label.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {Palette.TEXT_DARK};")
    return label


def page_subtitle_label(text):
    """Muted one-line description shown under a page title."""
    label = QLabel(text)
    label.setStyleSheet(f"font-size: 13px; color: {Palette.TEXT_MUTED};")
    return label