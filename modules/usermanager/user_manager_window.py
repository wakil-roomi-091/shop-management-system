"""
User Manager Window
Admin panel for managing system users
"""

import sys
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel,
    QMessageBox, QGroupBox, QHeaderView, QAbstractItemView,
    QDialog, QFormLayout, QLineEdit, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor  # <-- ADD THIS IMPORT
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import DatabaseManager, User
from utils.logger import get_logger, log_user_action

logger = get_logger(__name__)


class UserManagerWindow(QWidget):
    """User Management Window - Admin only"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        
        self.setWindowTitle("User Management")
        
        # Apply styles
        from ui.styles import get_app_style
        self.setStyleSheet(get_app_style())
        
        self.setup_ui()
        self.load_users()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        title = QLabel("User Management")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel("Manage system users and their roles")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Action Buttons
        action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        add_btn = QPushButton("➕ Add User")
        add_btn.setObjectName("success")
        add_btn.setMinimumHeight(45)
        add_btn.clicked.connect(self.add_user)
        action_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Edit User")
        edit_btn.setObjectName("primary")
        edit_btn.setMinimumHeight(45)
        edit_btn.clicked.connect(self.edit_user)
        action_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Delete User")
        delete_btn.setObjectName("danger")
        delete_btn.setMinimumHeight(45)
        delete_btn.clicked.connect(self.delete_user)
        action_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("secondary")
        refresh_btn.setMinimumHeight(45)
        refresh_btn.clicked.connect(self.load_users)
        action_layout.addWidget(refresh_btn)
        
        action_group.setLayout(action_layout)
        main_layout.addWidget(action_group)
        
        # Users Table
        table_group = QGroupBox("System Users")
        table_layout = QVBoxLayout()
        
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Username", "Full Name", "Role", "Status", "Last Login"
        ])
        self.user_table.verticalHeader().hide()
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.user_table.setAlternatingRowColors(True)
        self.user_table.setColumnHidden(0, True)  # Hide ID column
        
        self.user_table.setColumnWidth(1, 140)
        self.user_table.setColumnWidth(3, 120)
        self.user_table.setColumnWidth(4, 100)
        self.user_table.setColumnWidth(5, 160)

        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        header.setSectionResizeMode(5, QHeaderView.Interactive)
        
        self.user_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background-color: white;
                gridline-color: #e2e8f0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 10px;
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
        
        # Set row height
        self.user_table.verticalHeader().setDefaultSectionSize(50)
        
        table_layout.addWidget(self.user_table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 12px; color: #64748b; padding: 6px;")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
    
    def load_users(self):
        """Load users into table"""
        session = self.db.get_session()
        try:
            users = session.query(User).order_by(User.username).all()
            
            self.user_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
                self.user_table.setItem(row, 1, QTableWidgetItem(user.username))
                self.user_table.setItem(row, 2, QTableWidgetItem(user.full_name or "-"))
                
                # Role with color
                role_item = QTableWidgetItem(user.role.upper())
                if user.role == 'admin':
                    role_item.setBackground(QColor(139, 92, 246, 50))  # Purple
                elif user.role == 'manager':
                    role_item.setBackground(QColor(59, 130, 246, 50))   # Blue
                elif user.role == 'cashier':
                    role_item.setBackground(QColor(34, 197, 94, 50))    # Green
                elif user.role == 'dataentry':
                    role_item.setBackground(QColor(245, 158, 11, 50))   # Amber
                self.user_table.setItem(row, 3, role_item)
                
                # Status
                status_text = "Active" if user.is_active == 1 else "Inactive"
                status_item = QTableWidgetItem(status_text)
                if user.is_active == 1:
                    status_item.setBackground(QColor(34, 197, 94, 50))
                    status_item.setForeground(QColor(22, 163, 74))
                else:
                    status_item.setBackground(QColor(239, 68, 68, 50))
                    status_item.setForeground(QColor(220, 38, 38))
                self.user_table.setItem(row, 4, status_item)
                
                # Last Login
                if user.last_login:
                    last_login = user.last_login.strftime("%Y-%m-%d %I:%M %p")
                else:
                    last_login = "Never"
                self.user_table.setItem(row, 5, QTableWidgetItem(last_login))
            
            self.status_label.setText(f"Total: {len(users)} users")
            
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            QMessageBox.warning(self, "Error", f"Could not load users: {str(e)}")
        finally:
            session.close()
    
    def add_user(self):
        """Open dialog to add a new user"""
        dialog = UserDialog(self)
        if dialog.exec():
            self.load_users()
            log_user_action('admin', 'USER_ADD', f"Added user: {dialog.username}")
    
    def edit_user(self):
        """Open dialog to edit selected user"""
        selected = self.user_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a user to edit.")
            return
        
        user_id = int(self.user_table.item(selected, 0).text())
        dialog = UserDialog(self, user_id)
        if dialog.exec():
            self.load_users()
            log_user_action('admin', 'USER_EDIT', f"Edited user ID: {user_id}")
    
    def delete_user(self):
        """Delete selected user"""
        selected = self.user_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a user to delete.")
            return
        
        user_id = int(self.user_table.item(selected, 0).text())
        username = self.user_table.item(selected, 1).text()
        full_name = self.user_table.item(selected, 2).text()
        
        # Prevent deleting the last admin
        session = self.db.get_session()
        try:
            admin_count = session.query(User).filter_by(role='admin', is_active=1).count()
            user = session.query(User).filter_by(id=user_id).first()
            
            if user and user.role == 'admin' and admin_count <= 1:
                QMessageBox.warning(
                    self,
                    "Cannot Delete",
                    "Cannot delete the last admin user. At least one admin must exist."
                )
                return
        finally:
            session.close()
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete user '{username}' ({full_name})?\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = self.db.get_session()
            try:
                user = session.query(User).filter_by(id=user_id).first()
                if user:
                    # Check if user has sales before deleting
                    if user.sales:
                        reply2 = QMessageBox.question(
                            self,
                            "User Has Sales",
                            f"This user has {len(user.sales)} sales record(s).\n\n"
                            "Deleting this user will remove their association with those sales.\n"
                            "Continue?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        if reply2 == QMessageBox.No:
                            return
                    
                    session.delete(user)
                    session.commit()
                    log_user_action('admin', 'USER_DELETE', f"Deleted user: {username}")
                    QMessageBox.information(self, "Success", f"User '{username}' deleted successfully!")
                    self.load_users()
            except Exception as e:
                session.rollback()
                logger.error(f"Error deleting user: {e}")
                QMessageBox.critical(self, "Error", f"Could not delete user: {str(e)}")
            finally:
                session.close()


class UserDialog(QDialog):
    """Dialog for adding/editing users"""
    
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.user_id = user_id
        self.is_edit = user_id is not None
        self.username = None
        
        self.setWindowTitle("Edit User" if self.is_edit else "Add User")
        self.setModal(True)
        self.setFixedSize(450, 480)
        
        # Apply styles
        from ui.styles import get_app_style
        self.setStyleSheet(get_app_style())
        
        self.setup_ui()
        
        if self.is_edit:
            self.load_user_data()
        
        self.center_on_screen()
    
    def center_on_screen(self):
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2 - 50
        self.move(x, y)
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Title
        title = QLabel("Edit User" if self.is_edit else "Add New User")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0f172a;")
        layout.addWidget(title)
        
        # Form
        form_widget = QGroupBox()
        form_widget.setStyleSheet("""
            QGroupBox {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background-color: white;
                padding: 20px;
                margin-top: 0px;
            }
        """)
        form_layout = QFormLayout()
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(36)
        self.username_input.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        form_layout.addRow("Username:", self.username_input)
        
        # Full Name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Enter full name")
        self.full_name_input.setMinimumHeight(36)
        self.full_name_input.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        form_layout.addRow("Full Name:", self.full_name_input)
        
        # Password (only show for new user or if admin wants to change)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password (min 6 characters)")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(36)
        self.password_input.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        form_layout.addRow("Password:", self.password_input)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm password")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setMinimumHeight(36)
        self.confirm_password.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        form_layout.addRow("Confirm Password:", self.confirm_password)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.setMinimumHeight(36)
        self.role_combo.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        roles = [
            ('admin', 'Admin'),
            ('manager', 'Manager'),
            ('cashier', 'Cashier'),
            ('dataentry', 'Data Entry')
        ]
        for value, label in roles:
            self.role_combo.addItem(label, value)
        form_layout.addRow("Role:", self.role_combo)
        
        # Status
        self.status_check = QCheckBox("Active")
        self.status_check.setChecked(True)
        self.status_check.setStyleSheet("font-size: 14px;")
        form_layout.addRow("Status:", self.status_check)
        
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save User")
        save_btn.setObjectName("success")
        save_btn.setMinimumHeight(40)
        save_btn.setMinimumWidth(140)
        save_btn.clicked.connect(self.save_user)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_user_data(self):
        """Load user data for editing"""
        session = self.db.get_session()
        try:
            user = session.query(User).filter_by(id=self.user_id).first()
            if user:
                self.username_input.setText(user.username)
                self.full_name_input.setText(user.full_name or "")
                
                # Set role
                index = self.role_combo.findData(user.role)
                if index >= 0:
                    self.role_combo.setCurrentIndex(index)
                
                self.status_check.setChecked(user.is_active == 1)
                
                # Disable username editing
                self.username_input.setReadOnly(True)
                self.username_input.setStyleSheet("font-size: 14px; padding: 6px 12px; background-color: #f1f5f9;")
                
                # Make password optional for edit
                self.password_input.setPlaceholderText("Leave blank to keep current password")
                self.confirm_password.setPlaceholderText("Leave blank to keep current password")
            else:
                QMessageBox.warning(self, "Error", "User not found!")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load user: {str(e)}")
        finally:
            session.close()
    
    def save_user(self):
        """Save user to database"""
        username = self.username_input.text().strip()
        full_name = self.full_name_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_password.text()
        role = self.role_combo.currentData()
        is_active = 1 if self.status_check.isChecked() else 0
        
        # Validate
        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required!")
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, "Validation Error", "Username must be at least 3 characters!")
            return
        
        # For new user, password is required
        if not self.is_edit:
            if not password:
                QMessageBox.warning(self, "Validation Error", "Password is required for new users!")
                return
            if len(password) < 6:
                QMessageBox.warning(self, "Validation Error", "Password must be at least 6 characters!")
                return
            if password != confirm:
                QMessageBox.warning(self, "Validation Error", "Passwords do not match!")
                return
        
        # For edit, if password is provided, validate it
        if self.is_edit and password:
            if len(password) < 6:
                QMessageBox.warning(self, "Validation Error", "Password must be at least 6 characters!")
                return
            if password != confirm:
                QMessageBox.warning(self, "Validation Error", "Passwords do not match!")
                return
        
        session = self.db.get_session()
        try:
            # Check if username exists (for new user)
            if not self.is_edit:
                existing = session.query(User).filter_by(username=username).first()
                if existing:
                    QMessageBox.warning(self, "Validation Error", "Username already exists!")
                    return
            
            if self.is_edit:
                user = session.query(User).filter_by(id=self.user_id).first()
                if user:
                    user.full_name = full_name
                    user.role = role
                    user.is_active = is_active
                    if password:
                        user.set_password(password)
                    session.commit()
                    self.username = username
                    QMessageBox.information(self, "Success", f"User '{username}' updated successfully!")
                    self.accept()
            else:
                user = User(
                    username=username,
                    full_name=full_name,
                    role=role,
                    is_active=is_active
                )
                user.set_password(password)
                session.add(user)
                session.commit()
                self.username = username
                QMessageBox.information(self, "Success", f"User '{username}' created successfully!")
                self.accept()
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving user: {e}")
            QMessageBox.critical(self, "Error", f"Could not save user: {str(e)}")
        finally:
            session.close()