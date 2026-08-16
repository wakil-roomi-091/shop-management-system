"""
Login Window
Full-screen, role-gated login for the Shop Management System.
"""

import sys
import os
import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QFrame, QButtonGroup, QWidget
)
from PySide6.QtCore import Qt, QTimer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager, User
from ui.theme import Palette, make_shadow, rgba, darken

logger = logging.getLogger(__name__)

# (role key stored in the DB, display label)
ROLES = [
    ("admin", "Admin"),
    ("manager", "Manager"),
    ("cashier", "Cashier"),
    ("dataentry", "Data Entry"),
]
ROLE_LABELS = {key: label for key, label in ROLES}

# Seeded once, on first run, if no users exist yet.
DEFAULT_USERS = [
    ("admin", "admin123", "admin"),
    ("manager", "manager123", "manager"),
    ("cashier", "cashier123", "cashier"),
    ("dataentry", "data123", "dataentry"),
]


class LoginWindow(QDialog):
    """Full-screen login: pick your role, then sign in with that role's
    credentials. The two are checked together - a correct username and
    password for the wrong role is still rejected, so a cashier account
    can't be used to sign in as an admin just by picking a different tile.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()

        self.login_successful = False
        self.user_role = None
        self.username = None
        self.user_id = None
        self.selected_role = None

        self.setWindowTitle("Login")
        self.setModal(True)
        self.setWindowState(Qt.WindowFullScreen)
        self.setStyleSheet(f"QDialog {{ background-color: {Palette.TEXT_DARK}; }}")

        self._build_ui()
        self._ensure_default_users()

    # ------------------------------------------------------------ startup

    def _ensure_default_users(self):
        """Seed the four default accounts, but only if the user table is empty."""
        session = self.db.get_session()
        try:
            if session.query(User).count() == 0:
                for username, password, role in DEFAULT_USERS:
                    user = User(username=username, role=role, is_active=1)
                    user.set_password(password)
                    session.add(user)
                session.commit()
        except Exception as e:
            logger.error("Could not seed default users: %s", e)
        finally:
            session.close()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(1)

        center_row = QHBoxLayout()
        center_row.addStretch(1)
        center_row.addWidget(self._build_card())
        center_row.addStretch(1)
        outer.addLayout(center_row)

        outer.addStretch(1)

    def _build_card(self):
        card = QFrame()
        card.setFixedWidth(460)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Palette.WHITE};
                border-radius: 20px;
            }}
        """)
        card.setGraphicsEffect(make_shadow(blur=40, y_offset=12, alpha=60))

        layout = QVBoxLayout(card)
        layout.setSpacing(0)
        layout.setContentsMargins(40, 26, 40, 34)

        layout.addLayout(self._build_exit_row())
        layout.addWidget(self._build_logo_mark())

        title = QLabel("Shop Management System")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {Palette.TEXT_DARK}; margin-top: 14px;"
        )
        layout.addWidget(title)

        subtitle = QLabel("Select your role and sign in to continue")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 13px; color: {Palette.TEXT_MUTED}; margin-bottom: 22px;")
        layout.addWidget(subtitle)

        layout.addWidget(self._build_role_selector())
        layout.addSpacing(18)
        layout.addLayout(self._build_form())

        return card

    def _build_exit_row(self):
        row = QHBoxLayout()
        row.addStretch()

        exit_btn = QPushButton("Close")
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Palette.TEXT_MUTED};
                border: none;
                font-size: 12px;
                font-weight: 600;
                padding: 4px 6px;
            }}
            QPushButton:hover {{
                color: {Palette.DANGER};
            }}
        """)
        exit_btn.clicked.connect(self.reject)
        row.addWidget(exit_btn)
        return row

    @staticmethod
    def _build_logo_mark():
        """A plain letter mark instead of an emoji/image logo."""
        mark = QLabel("S")
        mark.setFixedSize(56, 56)
        mark.setAlignment(Qt.AlignCenter)
        mark.setStyleSheet(f"""
            background-color: {Palette.PRIMARY};
            color: white;
            font-size: 24px;
            font-weight: 700;
            border-radius: 28px;
        """)

        wrapper = QHBoxLayout()
        wrapper.addStretch()
        wrapper.addWidget(mark)
        wrapper.addStretch()

        container = QWidget()
        container.setLayout(wrapper)
        return container

    def _build_role_selector(self):
        container = QWidget()
        row = QHBoxLayout(container)
        row.setSpacing(10)
        row.setContentsMargins(0, 0, 0, 0)

        # QButtonGroup makes the four tiles mutually exclusive, like radio
        # buttons, without manually unchecking the other three by hand.
        self.role_group = QButtonGroup(self)
        self.role_group.setExclusive(True)

        for key, label in ROLES:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(44)
            btn.setStyleSheet(self._role_button_style())
            btn.clicked.connect(lambda checked, k=key: self._on_role_selected(k))
            self.role_group.addButton(btn)
            row.addWidget(btn)

        return container

    @staticmethod
    def _role_button_style():
        return f"""
            QPushButton {{
                background-color: {Palette.WHITE};
                border: 1.5px solid {Palette.BORDER};
                border-radius: 10px;
                padding: 6px;
                font-size: 12px;
                font-weight: 600;
                color: {Palette.TEXT_DARK};
            }}
            QPushButton:hover {{
                border: 1.5px solid {Palette.PRIMARY};
            }}
            QPushButton:checked {{
                background-color: {rgba(Palette.PRIMARY, 0.08)};
                border: 1.5px solid {Palette.PRIMARY};
                color: {Palette.PRIMARY};
            }}
        """

    def _build_form(self):
        form_layout = QVBoxLayout()
        form_layout.setSpacing(14)

        username_label = self._field_label("Username")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(42)
        self.username_input.setStyleSheet(self._input_style())
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)

        password_label = self._field_label("Password")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(42)
        self.password_input.setStyleSheet(self._input_style())
        self.password_input.returnPressed.connect(self.attempt_login)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet(f"font-size: 12px; color: {Palette.DANGER}; min-height: 20px;")
        form_layout.addWidget(self.error_label)

        login_btn = QPushButton("Sign In")
        login_btn.setMinimumHeight(44)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet(self._primary_button_style())
        login_btn.clicked.connect(self.attempt_login)
        form_layout.addWidget(login_btn)

        QTimer.singleShot(100, self.username_input.setFocus)

        return form_layout

    @staticmethod
    def _field_label(text):
        label = QLabel(text)
        label.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {Palette.TEXT_LABEL}; margin-bottom: 2px;"
        )
        return label

    @staticmethod
    def _input_style():
        # NOTE: `color` is set explicitly here on purpose - without it, the
        # typed text inherits whatever the app's default text color is
        # (which can end up matching the field's own background, making
        # anything you type invisible).
        return f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 1px solid {Palette.BORDER};
                border-radius: 8px;
                font-size: 14px;
                color: {Palette.TEXT_DARK};
                background-color: {Palette.BG};
                selection-background-color: {Palette.PRIMARY};
                selection-color: white;
            }}
            QLineEdit:focus {{
                border: 2px solid {Palette.PRIMARY};
                background-color: {Palette.WHITE};
            }}
        """

    @staticmethod
    def _primary_button_style():
        hover_color = darken(Palette.PRIMARY)
        return f"""
            QPushButton {{
                background-color: {Palette.PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """

    # --------------------------------------------------------------- logic

    def _on_role_selected(self, role_key):
        self.selected_role = role_key
        self.error_label.setText("")

    def attempt_login(self):
        if not self.selected_role:
            self.error_label.setText("Please select your role to continue.")
            return

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        self.error_label.setText("")

        if not username or not password:
            self.error_label.setText("Please enter your username and password.")
            return

        session = self.db.get_session()
        try:
            user = session.query(User).filter_by(username=username, is_active=1).first()

            if user is None or not user.check_password(password):
                self.error_label.setText("Invalid username or password.")
                self.password_input.clear()
                self.password_input.setFocus()
                return

            if user.role != self.selected_role:
                self.error_label.setText(
                    f"This account isn't registered as {ROLE_LABELS.get(self.selected_role, self.selected_role)}."
                )
                self.password_input.clear()
                self.password_input.setFocus()
                return

            user.last_login = datetime.now()
            session.commit()

            self.login_successful = True
            self.user_role = user.role
            self.username = user.username
            self.user_id = user.id
            self.accept()

        except Exception as e:
            logger.error("Login error: %s", e)
            self.error_label.setText("Something went wrong. Please try again.")
        finally:
            session.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        super().keyPressEvent(event)