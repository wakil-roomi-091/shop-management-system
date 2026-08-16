"""
Shop Management System
Main Application Entry Point - Fully Responsive
"""

import logging
import sys
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QButtonGroup,
    QDialog,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging FIRST
from utils.logger import setup_logging, get_logger, log_user_action

setup_logging()
logger = get_logger(__name__)

from database import DatabaseManager
from database.init_db import initialize_database
from modules.dashboard import DashboardWindow
from modules.products import ProductsWindow
from modules.sales import SalesWindow
from modules.reports import ReportsWindow
from modules.settings import SettingsWindow
from modules.customers import CustomersWindow
from modules.backup import BackupWindow
from modules.usermanager import UserManagerWindow
from modules.expenses import ExpensesWindow
from modules.auth.login_window import LoginWindow

logger = get_logger(__name__)

# ===== RESPONSIVE FUNCTIONS =====


def get_sidebar_width():
    """Calculate sidebar width based on screen size"""
    screen = QApplication.primaryScreen()
    if screen:
        width = screen.geometry().width()
        if width < 1024:
            return 200
        elif width < 1366:
            return 220
        elif width < 1920:
            return 240
        else:
            return 260
    return 220


def get_font_size():
    """Calculate font size based on screen resolution"""
    screen = QApplication.primaryScreen()
    if screen:
        dpi = screen.logicalDotsPerInch()
        if dpi < 100:
            return 12
        elif dpi < 120:
            return 13
        else:
            return 14
    return 13


# Professional icons
ICONS = {
    "dashboard": "📊",
    "products": "📦",
    "sales": "🛒",
    "customers": "👤",
    "reports": "📈",
    "expenses": "💰",
    "backup": "💾",
    "usermanager": "👥",
    "settings": "⚙️",
}

NAV_ITEMS = [
    ("dashboard", ICONS["dashboard"], "Dashboard", DashboardWindow),
    ("products", ICONS["products"], "Products", ProductsWindow),
    ("sales", ICONS["sales"], "Sales", SalesWindow),
    ("customers", ICONS["customers"], "Customers", CustomersWindow),
    ("reports", ICONS["reports"], "Reports", ReportsWindow),
    ("expenses", ICONS["expenses"], "Expenses", ExpensesWindow),
    ("backup", ICONS["backup"], "Backup", BackupWindow),
    ("usermanager", ICONS["usermanager"], "Users", UserManagerWindow),
    ("settings", ICONS["settings"], "Settings", SettingsWindow),
]

# Role-based access
ROLE_ACCESS = {
    "admin": [
        "dashboard",
        "products",
        "sales",
        "customers",
        "reports",
        "expenses",
        "backup",
        "usermanager",
        "settings",
    ],
    "manager": ["dashboard", "products", "sales", "customers", "reports", "expenses"],
    "cashier": ["sales"],
    "dataentry": ["products"],
}

ROLE_DISPLAY_NAMES = {
    "admin": "Admin",
    "manager": "Manager",
    "cashier": "Cashier",
    "dataentry": "Data Entry",
}

APP_VERSION = "1.0.0"


class MainWindow(QMainWindow):
    """Main application window: sidebar navigation + swappable content area."""

    def __init__(self, user_role=None, username=None):
        super().__init__()
        self.setWindowTitle("Shop Management System")

        # ===== RESPONSIVE WINDOW SIZE =====
        primary_screen = QApplication.primaryScreen()
        avail = primary_screen.availableGeometry() if primary_screen else None
        if avail:
            init_w = min(max(int(avail.width() * 0.90), 800), 1600)
            init_h = min(max(int(avail.height() * 0.90), 550), 1000)
            pos_x = avail.x() + (avail.width() - init_w) // 2
            pos_y = avail.y() + (avail.height() - init_h) // 2
            self.setGeometry(pos_x, pos_y, init_w, init_h)
        else:
            self.setGeometry(50, 50, 1100, 700)
        self.setMinimumSize(780, 520)

        # Set responsive font
        font = QFont("Segoe UI", get_font_size())
        self.setFont(font)

        from ui.styles import get_app_style

        self.setStyleSheet(get_app_style())

        self._ensure_database_ready()

        self.user_role = user_role
        self.username = username
        self.logout_requested = False
        self.allowed_keys = ROLE_ACCESS.get(
            user_role, [key for key, _, _, _ in NAV_ITEMS]
        )

        self.current_widget = None
        self._setup_ui()

        if self.allowed_keys:
            self.navigate_to(self.allowed_keys[0])

        logger.info(f"MainWindow initialized for user: {username} ({user_role})")
        log_user_action(username, "LOGIN", f"Logged in as {user_role}")

    # ------------------------------------------------------------ startup

    def _ensure_database_ready(self):
        """Confirm the database is reachable; initialize it on first run."""
        try:
            db = DatabaseManager()
            session = db.get_session()
            session.close()
        except Exception:
            logger.info("Database not found or unreadable - initializing a new one.")
            initialize_database()

    # ------------------------------------------------------------------ UI

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._build_sidebar())

        self.content_area = QFrame()
        self.content_area.setStyleSheet(
            "QFrame { background-color: #f1f5f9; border: none; }"
        )
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.content_area, 1)

    def _build_sidebar(self):
        sidebar_width = get_sidebar_width()

        sidebar = QFrame()
        sidebar.setFixedWidth(sidebar_width)
        sidebar.setStyleSheet("QFrame { background-color: #0f172a; border: none; }")

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 20, 10, 20)

        # Logo - Responsive font
        logo_size = 18 if sidebar_width > 230 else 16
        logo_label = QLabel("Shop Management")
        logo_label.setStyleSheet(f"""
            color: white;
            font-size: {logo_size}px;
            font-weight: 700;
            padding: 15px 10px;
            letter-spacing: 0.5px;
        """)
        logo_label.setWordWrap(True)
        layout.addWidget(logo_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(
            "background-color: #1e293b; max-height: 1px; margin: 10px 0;"
        )
        layout.addWidget(separator)

        self.nav_buttons = {}
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        # Responsive button font
        btn_font = 14 if sidebar_width > 230 else 12

        for key, icon, label, _ in NAV_ITEMS:
            if key not in self.allowed_keys:
                continue

            btn_text = f"{icon}  {label}"
            btn = QPushButton(btn_text)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #94a3b8;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 15px;
                    text-align: left;
                    font-size: {btn_font}px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #1e293b;
                    color: white;
                }}
                QPushButton:checked {{
                    background-color: #1e293b;
                    color: white;
                }}
            """)
            btn.clicked.connect(lambda checked, k=key: self.navigate_to(k))
            layout.addWidget(btn)
            self.nav_group.addButton(btn)
            self.nav_buttons[key] = btn

        layout.addStretch()

        if self.username:
            role_name = ROLE_DISPLAY_NAMES.get(self.user_role, self.user_role or "")
            user_label = QLabel(f"{self.username} · {role_name}")
            user_label.setStyleSheet(
                "color: #cbd5e1; font-size: 12px; padding: 4px 10px;"
            )
            user_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(user_label)

            logout_btn = QPushButton("🚪 Logout")
            logout_btn.setCursor(Qt.PointingHandCursor)
            logout_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #94a3b8;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 15px;
                    text-align: left;
                    font-size: {btn_font}px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #dc2626;
                    color: white;
                }}
            """)
            logout_btn.clicked.connect(self._logout)
            layout.addWidget(logout_btn)

        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet("color: #475569; font-size: 12px; padding: 10px;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        return sidebar

    def _logout(self):
        self.logout_requested = True
        log_user_action(self.username, "LOGOUT", "User logged out")
        self.close()

    @staticmethod
    def _nav_button_style():
        return """
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                border: none;
                border-radius: 8px;
                padding: 12px 15px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: white;
            }
            QPushButton:checked {
                background-color: #1e293b;
                color: white;
            }
        """

    # ------------------------------------------------------------ routing

    def navigate_to(self, key):
        """Swap the content area to the module registered under `key`."""
        module_map = {
            item_key: window_class for item_key, _, _, window_class in NAV_ITEMS
        }
        window_class = module_map.get(key)
        if window_class is None:
            logger.warning("Unknown navigation target: %s", key)
            return
        if key not in self.allowed_keys:
            logger.warning(
                "Role '%s' does not have access to '%s'", self.user_role, key
            )
            return

        self._clear_content()
        self.current_widget = window_class(self)
        self.content_layout.addWidget(self.current_widget)

        if key in self.nav_buttons:
            self.nav_buttons[key].setChecked(True)

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    # ------------------------------------------------------------ shutdown

    def closeEvent(self, event):
        """Handle window close event - auto backup if enabled"""

        # Check if auto backup is enabled
        try:
            db = DatabaseManager()
            session = db.get_session()
            try:
                from database.models import Setting

                setting = session.query(Setting).filter_by(key="auto_backup").first()
                auto_backup = setting and setting.value == "True"
            except:
                auto_backup = False
            finally:
                session.close()
        except:
            auto_backup = False

        if auto_backup:
            # Create auto backup
            backup_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "backups"
            )
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"auto_backup_{timestamp}.db")

            try:
                db = DatabaseManager()
                db.backup_database(backup_path)
                logger.info(f"Auto backup created: {backup_path}")
                log_user_action(
                    self.username, "AUTO_BACKUP", f"Auto backup created: {backup_path}"
                )
            except Exception as e:
                logger.error(f"Auto backup failed: {e}")

        event.accept()


def main():
    """Main entry point"""

    # ===== ENABLE HIGH DPI SUPPORT =====
    import os

    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"
    # ==================================

    logger.info("=" * 50)
    logger.info("SHOP MANAGEMENT SYSTEM STARTING")
    logger.info(f"Version: {APP_VERSION}")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    # Create application with DPI awareness
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Set application-wide font
    font = QFont("Segoe UI", get_font_size())
    app.setFont(font)

    app.setApplicationName("Shop Management System")
    app.setOrganizationName("ShopManager")
    app.setQuitOnLastWindowClosed(True)

    icon_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico"
    )
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    while True:
        login = LoginWindow()
        if login.exec() != QDialog.Accepted or not login.login_successful:
            logger.info("Login cancelled or failed - exiting application")
            sys.exit(0)

        logger.info(f"User logged in: {login.username} ({login.user_role})")

        window = MainWindow(user_role=login.user_role, username=login.username)
        window.show()
        app.exec()

        if not window.logout_requested:
            logger.info("Application closed - exiting")
            sys.exit(0)


if __name__ == "__main__":
    main()
