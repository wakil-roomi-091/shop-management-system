"""
Add/Edit Customer Dialog
Form for adding or editing customers
"""

import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import DatabaseManager, Customer


class AddCustomerDialog(QDialog):
    """Dialog for adding or editing customers"""
    
    def __init__(self, parent=None, customer_id=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.customer_id = customer_id
        self.is_edit = customer_id is not None
        
        self.setWindowTitle("Edit Customer" if self.is_edit else "Add Customer")
        self.setModal(True)
        
        # Apply styles
        from ui.styles import get_app_style
        self.setStyleSheet(get_app_style())
        
        self.setup_ui()
        
        if self.is_edit:
            self.load_customer_data()
        
        # Center on screen
        self.center_on_screen()
    
    def center_on_screen(self):
        """Center the dialog on screen"""
        screen = self.screen().availableGeometry() if self.screen() else None
        if screen:
            x = screen.x() + (screen.width() - self.width()) // 2
            y = screen.y() + (screen.height() - self.height()) // 2
            self.move(x, y)
    
    def setup_ui(self):
        """Setup the dialog interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(28, 20, 28, 20)
        
        # Title
        title = QLabel("Edit Customer" if self.is_edit else "Add New Customer")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #0f172a; padding: 0;")
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Fill in the customer details below")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #64748b;")
        main_layout.addWidget(subtitle)
        
        # Form Group
        form_group = QGroupBox()
        form_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background-color: #ffffff;
                padding: 18px 22px 18px 22px;
                margin-top: 0px;
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Customer Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter customer name")
        self.name_input.setMinimumHeight(34)
        self.name_input.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        form_layout.addRow("Name *:", self.name_input)
        
        # Phone Number
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        self.phone_input.setMinimumHeight(34)
        self.phone_input.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        form_layout.addRow("Phone *:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email (optional)")
        self.email_input.setMinimumHeight(34)
        self.email_input.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        form_layout.addRow("Email:", self.email_input)
        
        # Address
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        self.address_input.setPlaceholderText("Enter address (optional)")
        self.address_input.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                padding: 6px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QTextEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        form_layout.addRow("Address:", self.address_input)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setMinimumHeight(38)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 24px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 8px;
                min-width: 100px;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Customer")
        save_btn.setObjectName("success")
        save_btn.setMinimumHeight(38)
        save_btn.setMinimumWidth(140)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 28px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px;
                min-width: 140px;
            }
        """)
        save_btn.clicked.connect(self.save_customer)
        button_layout.addWidget(save_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Set balanced size
        self.setFixedSize(480, 480)
    
    def load_customer_data(self):
        """Load customer data for editing"""
        session = self.db.get_session()
        try:
            customer = session.query(Customer).filter_by(id=self.customer_id).first()
            if customer:
                self.name_input.setText(customer.name)
                self.phone_input.setText(customer.phone)
                self.email_input.setText(customer.email or "")
                self.address_input.setText(customer.address or "")
            else:
                QMessageBox.warning(self, "Error", "Customer not found!")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load customer: {str(e)}")
        finally:
            session.close()
    
    def save_customer(self):
        """Save customer to database"""
        # Validate inputs
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Customer name is required!")
            return
        
        if not self.phone_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Phone number is required!")
            return
        
        # Validate phone number (basic)
        phone = self.phone_input.text().strip()
        if len(phone) < 7:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid phone number!")
            return
        
        session = self.db.get_session()
        try:
            # Check for duplicate phone number
            existing = session.query(Customer).filter(
                Customer.phone == phone,
                Customer.id != (self.customer_id if self.is_edit else -1)
            ).first()
            
            if existing:
                QMessageBox.warning(self, "Duplicate", "A customer with this phone number already exists!")
                return
            
            # Prepare customer data
            customer_data = {
                'name': self.name_input.text().strip(),
                'phone': phone,
                'email': self.email_input.text().strip() or None,
                'address': self.address_input.toPlainText().strip() or None
            }
            
            if self.is_edit:
                # Update existing customer
                customer = session.query(Customer).filter_by(id=self.customer_id).first()
                if customer:
                    for key, value in customer_data.items():
                        setattr(customer, key, value)
                    session.commit()
                    QMessageBox.information(self, "Success", "Customer updated successfully!")
                    self.accept()
            else:
                # Create new customer
                customer = Customer(**customer_data)
                session.add(customer)
                session.commit()
                QMessageBox.information(self, "Success", f"Customer '{customer.name}' added successfully!")
                self.accept()
                
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Could not save customer: {str(e)}")
        finally:
            session.close()