"""
Add Expense Dialog
Form for adding expenses
"""

import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
    QPushButton, QMessageBox, QGroupBox, QDateEdit, QTextEdit
)
from PySide6.QtCore import Qt, QDate

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import DatabaseManager, Expense
from utils.logger import get_logger

logger = get_logger(__name__)


class AddExpenseDialog(QDialog):
    """Dialog for adding expenses"""
    
    def __init__(self, parent=None, expense_id=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.expense_id = expense_id
        self.is_edit = expense_id is not None
        
        self.setWindowTitle("Edit Expense" if self.is_edit else "Add Expense")
        self.setModal(True)
        
        from ui.styles import get_app_style
        self.setStyleSheet(get_app_style())
        
        self.setup_ui()
        
        if self.is_edit:
            self.load_expense_data()
        
        self.center_on_screen()
    
    def center_on_screen(self):
        screen = self.screen().availableGeometry() if self.screen() else None
        if screen:
            x = screen.x() + (screen.width() - self.width()) // 2
            y = screen.y() + (screen.height() - self.height()) // 2
            self.move(x, y)
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(28, 20, 28, 20)
        
        # Title
        title = QLabel("Edit Expense" if self.is_edit else "Add Expense")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #0f172a;")
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Fill in the expense details below")
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
                padding: 18px 22px;
                margin-top: 0px;
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(34)
        self.category_combo.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        categories = [
            'Rent', 'Salaries', 'Utilities', 'Electricity', 'Water',
            'Gas', 'Internet', 'Phone', 'Marketing', 'Maintenance',
            'Supplies', 'Insurance', 'Transport', 'Food', 'Other'
        ]
        for cat in categories:
            self.category_combo.addItem(cat)
        form_layout.addRow("Category:", self.category_combo)
        
        # Description
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Enter expense description")
        self.description_input.setMinimumHeight(34)
        self.description_input.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        form_layout.addRow("Description:", self.description_input)
        
        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999.99)
        self.amount_input.setPrefix("Rs ")
        self.amount_input.setSingleStep(10)
        self.amount_input.setMinimumHeight(34)
        self.amount_input.setStyleSheet("font-size: 14px;")
        form_layout.addRow("Amount:", self.amount_input)
        
        # Date
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setMinimumHeight(34)
        self.date_input.setStyleSheet("font-size: 14px;")
        form_layout.addRow("Date:", self.date_input)
        
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
        
        save_btn = QPushButton("Save Expense")
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
        save_btn.clicked.connect(self.save_expense)
        button_layout.addWidget(save_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        self.setFixedSize(480, 420)
    
    def load_expense_data(self):
        """Load expense data for editing"""
        session = self.db.get_session()
        try:
            expense = session.query(Expense).filter_by(id=self.expense_id).first()
            if expense:
                index = self.category_combo.findText(expense.category)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                self.description_input.setText(expense.description or "")
                self.amount_input.setValue(expense.amount)
                self.date_input.setDate(QDate.fromPython(expense.expense_date))
            else:
                QMessageBox.warning(self, "Error", "Expense not found!")
                self.reject()
        except Exception as e:
            logger.error(f"Error loading expense: {e}")
            QMessageBox.critical(self, "Error", f"Could not load expense: {str(e)}")
        finally:
            session.close()
    
    def save_expense(self):
        """Save expense to database"""
        amount = self.amount_input.value()
        
        # Validate
        if amount <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount must be greater than 0!")
            return
        
        session = self.db.get_session()
        try:
            # Get the date and set to start of day
            expense_date = self.date_input.date().toPython()
            expense_date = datetime(expense_date.year, expense_date.month, expense_date.day, 0, 0, 0)
            
            data = {
                'category': self.category_combo.currentText(),
                'description': self.description_input.text().strip() or None,
                'amount': amount,
                'expense_date': expense_date
            }
            
            if self.is_edit:
                # Update existing expense
                expense = session.query(Expense).filter_by(id=self.expense_id).first()
                if expense:
                    for key, value in data.items():
                        setattr(expense, key, value)
                    session.commit()
                    logger.info(f"Expense updated: {expense.category} - {expense.amount}")
                    QMessageBox.information(self, "Success", "Expense updated successfully!")
            else:
                # Create new expense
                expense = Expense(**data)
                session.add(expense)
                session.commit()
                logger.info(f"Expense added: {expense.category} - {expense.amount}")
                QMessageBox.information(self, "Success", "Expense added successfully!")
            
            self.accept()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving expense: {e}")
            QMessageBox.critical(self, "Error", f"Could not save expense: {str(e)}")
        finally:
            session.close()