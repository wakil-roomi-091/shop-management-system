"""
Backup & Restore Window
Database backup and restore functionality
"""

import sys
import os
import shutil
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QAbstractItemView,
    QProgressBar,
    QDialog,
    QCheckBox,
)
from PySide6.QtCore import Qt, QTimer

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from database import DatabaseManager
from utils.logger import get_logger, log_user_action

logger = get_logger(__name__)


class BackupWindow(QWidget):
    """Database Backup and Restore Window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()

        # ===== FIX: Get correct backup directory =====
        if getattr(sys, "frozen", False):
            # Running as .exe - look in the same folder as the .exe
            app_root = os.path.dirname(sys.executable)
        else:
            # Running as Python script - look in the project folder
            app_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

        self.backup_dir = os.path.join(app_root, "backups")
        # =============================================

        # Create backups directory if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        self.setWindowTitle("Backup & Restore")

        # Apply styles
        from ui.styles import get_app_style

        self.setStyleSheet(get_app_style())

        self.setup_ui()
        self.load_backups()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header
        title = QLabel("Backup & Restore")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Create backups directory if not exists
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        # Action Buttons
        action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)

        backup_btn = QPushButton("💾 Create Backup")
        backup_btn.setObjectName("success")
        backup_btn.setMinimumHeight(50)
        backup_btn.clicked.connect(self.create_backup)
        action_layout.addWidget(backup_btn)

        restore_btn = QPushButton("🔄 Restore Backup")
        restore_btn.setObjectName("primary")
        restore_btn.setMinimumHeight(50)
        restore_btn.clicked.connect(self.restore_backup)
        action_layout.addWidget(restore_btn)

        auto_backup_btn = QPushButton("⚙️ Auto Backup Settings")
        auto_backup_btn.setObjectName("secondary")
        auto_backup_btn.setMinimumHeight(50)
        auto_backup_btn.clicked.connect(self.auto_backup_settings)
        action_layout.addWidget(auto_backup_btn)

        action_group.setLayout(action_layout)
        main_layout.addWidget(action_group)

        # Backups List - FINAL FIXED UI
        list_group = QGroupBox("Available Backups")
        list_layout = QVBoxLayout()

        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels(
            ["Backup Name", "Date", "Size", "Actions"]
        )
        self.backup_table.verticalHeader().hide()
        self.backup_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backup_table.setAlternatingRowColors(True)

        # Set column widths - ACTIONS COLUMN WIDE ENOUGH FOR BUTTON
        self.backup_table.setColumnWidth(0, 160)
        self.backup_table.setColumnWidth(1, 170)
        self.backup_table.setColumnWidth(2, 90)
        self.backup_table.setColumnWidth(3, 150)  # Wide enough for Delete button

        # Set row height - TALL ENOUGH FOR BUTTON
        self.backup_table.verticalHeader().setDefaultSectionSize(80)

        # Header resize modes - Name stretches, others fixed
        header = self.backup_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(
            0, QHeaderView.Stretch
        )  # Name fills remaining space
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(
            3, QHeaderView.ResizeToContents
        )  # Actions stays 150px

        self.backup_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background-color: white;
                gridline-color: #e2e8f0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px 10px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                padding: 10px 10px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        list_layout.addWidget(self.backup_table)
        list_group.setLayout(list_layout)
        main_layout.addWidget(list_group)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            "font-size: 12px; color: #64748b; padding: 6px;"
        )
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def load_backups(self):
        """Load list of backups"""
        self.backup_table.setRowCount(0)

        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            return

        try:
            backups = []
            for file in os.listdir(self.backup_dir):
                if file.endswith(".db") and file.startswith("backup_"):
                    filepath = os.path.join(self.backup_dir, file)
                    stat = os.stat(filepath)
                    backups.append(
                        {
                            "name": file,
                            "path": filepath,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime),
                        }
                    )

            # Sort by date (newest first)
            backups.sort(key=lambda x: x["modified"], reverse=True)

            self.backup_table.setRowCount(len(backups))

            for row, backup in enumerate(backups):
                # Name
                self.backup_table.setItem(row, 0, QTableWidgetItem(backup["name"]))

                # Date
                self.backup_table.setItem(
                    row,
                    1,
                    QTableWidgetItem(backup["modified"].strftime("%Y-%m-%d %I:%M %p")),
                )

                # Size
                size_kb = backup["size"] / 1024
                if size_kb > 1024:
                    size_str = f"{size_kb/1024:.1f} MB"
                else:
                    size_str = f"{size_kb:.1f} KB"
                self.backup_table.setItem(row, 2, QTableWidgetItem(size_str))

                # Action buttons - PROPERLY SIZED AND CENTERED
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(4, 4, 4, 4)
                btn_layout.setSpacing(0)
                btn_layout.setAlignment(Qt.AlignCenter)

                delete_btn = QPushButton("Delete")
                delete_btn.setObjectName("danger")
                delete_btn.setFixedHeight(25)
                delete_btn.setMinimumWidth(40)
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.clicked.connect(lambda r=row: self.delete_backup(r))

                btn_layout.addWidget(delete_btn)
                btn_widget.setLayout(btn_layout)
                self.backup_table.setCellWidget(row, 3, btn_widget)

            self.status_label.setText(f"Found {len(backups)} backup(s)")

        except Exception as e:
            logger.error(f"Error loading backups: {e}")
            self.status_label.setText(f"Error loading backups: {str(e)}")

    def create_backup(self):
        """Create a new backup"""
        try:
            # Ensure backups directory exists
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_name)

            self.status_label.setText("Creating backup...")

            # Create backup
            import shutil

            db_path = self.db.db_path
            shutil.copy2(db_path, backup_path)

            log_user_action("system", "BACKUP_CREATE", f"Created backup: {backup_name}")
            self.status_label.setText(f"✅ Backup created successfully: {backup_name}")
            self.load_backups()

            QMessageBox.information(
                self,
                "Backup Created",
                f"Backup saved to:\n{backup_path}\n\nSize: {os.path.getsize(backup_path)/1024:.1f} KB",
            )

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            self.status_label.setText(f"❌ Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Could not create backup: {str(e)}")

    def restore_backup(self):
        """Restore from backup"""
        selected = self.backup_table.currentRow()
        if selected < 0:
            QMessageBox.warning(
                self, "No Selection", "Please select a backup to restore."
            )
            return

        backup_name = self.backup_table.item(selected, 0).text()
        backup_path = os.path.join(self.backup_dir, backup_name)

        reply = QMessageBox.question(
            self,
            "Confirm Restore",
            f"Are you sure you want to restore from backup?\n\n"
            f"Backup: {backup_name}\n"
            f"Date: {self.backup_table.item(selected, 1).text()}\n\n"
            f"⚠️ This will REPLACE all current data with the backup data.\n"
            f"This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                self.status_label.setText("Restoring backup...")

                # Close current database connection
                self.db._engine.dispose()

                # Restore backup
                success = self.db.restore_database(backup_path)

                if success:
                    log_user_action(
                        "system", "BACKUP_RESTORE", f"Restored from: {backup_name}"
                    )
                    self.status_label.setText(
                        f"✅ Backup restored successfully: {backup_name}"
                    )
                    QMessageBox.information(
                        self,
                        "Restore Complete",
                        f"Database restored from backup:\n{backup_name}\n\n"
                        "Please restart the application for changes to take effect.",
                    )
                else:
                    self.status_label.setText("❌ Failed to restore backup")
                    QMessageBox.critical(self, "Error", "Failed to restore backup.")

            except Exception as e:
                logger.error(f"Error restoring backup: {e}")
                self.status_label.setText(f"❌ Error: {str(e)}")
                QMessageBox.critical(
                    self, "Error", f"Could not restore backup: {str(e)}"
                )

    def delete_backup(self, row):
        """Delete a backup"""
        backup_name = self.backup_table.item(row, 0).text()
        backup_path = os.path.join(self.backup_dir, backup_name)

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this backup?\n\n{backup_name}",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                os.remove(backup_path)
                log_user_action(
                    "system", "BACKUP_DELETE", f"Deleted backup: {backup_name}"
                )
                self.load_backups()
                self.status_label.setText(f"✅ Backup deleted: {backup_name}")
            except Exception as e:
                logger.error(f"Error deleting backup: {e}")
                QMessageBox.critical(
                    self, "Error", f"Could not delete backup: {str(e)}"
                )

    def auto_backup_settings(self):
        """Auto backup settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Auto Backup Settings")
        dialog.setFixedSize(450, 240)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        title = QLabel("Auto Backup Settings")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        layout.addWidget(title)

        # Check if auto backup is enabled in settings
        session = self.db.get_session()
        try:
            from database.models import Setting

            setting = session.query(Setting).filter_by(key="auto_backup").first()
            if setting and setting.value:
                enabled = setting.value.lower() == "true"
            else:
                enabled = False
        except Exception as e:
            logger.error(f"Error loading auto backup setting: {e}")
            enabled = False
        finally:
            session.close()

        auto_check = QCheckBox("Auto-backup on application exit")
        auto_check.setChecked(enabled)
        auto_check.setStyleSheet("font-size: 13px;")
        layout.addWidget(auto_check)

        info = QLabel(
            "When enabled, a backup will be created automatically when you close the application."
        )
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 12px; color: #64748b;")
        layout.addWidget(info)

        info2 = QLabel("Backups will be saved in the 'backups' folder with timestamp.")
        info2.setWordWrap(True)
        info2.setStyleSheet("font-size: 12px; color: #64748b;")
        layout.addWidget(info2)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primary")
        save_btn.setMinimumHeight(40)
        save_btn.setMinimumWidth(120)
        save_btn.clicked.connect(
            lambda: self.save_auto_backup_setting(auto_check.isChecked(), dialog)
        )
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def save_auto_backup_setting(self, enabled, dialog):
        """Save auto backup setting"""
        session = self.db.get_session()
        try:
            from database.models import Setting

            setting = session.query(Setting).filter_by(key="auto_backup").first()
            if setting:
                setting.value = "True" if enabled else "False"
            else:
                setting = Setting(
                    key="auto_backup", value="True" if enabled else "False"
                )
                session.add(setting)
            session.commit()
            log_user_action("system", "AUTO_BACKUP", f"Set to {enabled}")
            dialog.accept()
            QMessageBox.information(
                self,
                "Settings Saved",
                "Auto backup setting saved successfully.\n\n"
                + (
                    "✅ Auto backup will run when you close the application."
                    if enabled
                    else "❌ Auto backup is now disabled."
                ),
            )
            self.status_label.setText(
                f"✅ Auto backup {'enabled' if enabled else 'disabled'}"
            )
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving auto backup setting: {e}")
            QMessageBox.critical(self, "Error", f"Could not save setting: {str(e)}")
        finally:
            session.close()
