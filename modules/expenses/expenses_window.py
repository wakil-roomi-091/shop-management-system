"""
Expenses Window
Track and manage expenses
"""

import sys
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel,
    QMessageBox, QGroupBox, QHeaderView, QAbstractItemView,
    QDateEdit, QComboBox, QFrame
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime
from sqlalchemy import func, extract

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import DatabaseManager, Expense, Sale, Setting
from .add_expense_dialog import AddExpenseDialog
from utils.logger import get_logger, log_user_action

logger = get_logger(__name__)


class ExpensesWindow(QWidget):
    """Expense Management Window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        
        self.setWindowTitle("Expense Management")
        
        from ui.styles import get_app_style
        self.setStyleSheet(get_app_style())
        
        self.setup_ui()
        self.load_expenses()
        self.update_summary()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Expense Management")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Summary Cards
        summary_group = QGroupBox("Monthly Summary")
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)
        
        # Total Sales (Monthly)
        sales_card = self._create_summary_card("Monthly Sales", "Rs 0.00", "#eff6ff", "#2563eb")
        summary_layout.addWidget(sales_card)
        self.monthly_sales_label = sales_card.findChild(QLabel, "value")
        
        # Total Expenses (Monthly)
        expense_card = self._create_summary_card("Monthly Expenses", "Rs 0.00", "#fef2f2", "#dc2626")
        summary_layout.addWidget(expense_card)
        self.monthly_expenses_label = expense_card.findChild(QLabel, "value")
        
        # Net Profit (Monthly)
        profit_card = self._create_summary_card("Net Profit (Monthly)", "Rs 0.00", "#f0fdf4", "#16a34a")
        summary_layout.addWidget(profit_card)
        self.net_profit_label = profit_card.findChild(QLabel, "value")
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Filter
        filter_group = QGroupBox("Filter")
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.setCalendarPopup(True)
        self.from_date.setMinimumHeight(35)
        filter_layout.addWidget(self.from_date)
        
        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        self.to_date.setMinimumHeight(35)
        filter_layout.addWidget(self.to_date)
        
        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        categories = ['Rent', 'Salaries', 'Utilities', 'Electricity', 'Water',
                      'Gas', 'Internet', 'Phone', 'Marketing', 'Maintenance',
                      'Supplies', 'Insurance', 'Transport', 'Food', 'Other']
        for cat in categories:
            self.category_filter.addItem(cat)
        self.category_filter.setMinimumHeight(35)
        filter_layout.addWidget(self.category_filter)
        
        filter_btn = QPushButton("Apply Filter")
        filter_btn.setObjectName("primary")
        filter_btn.setMinimumHeight(35)
        filter_btn.clicked.connect(self.load_expenses)
        filter_layout.addWidget(filter_btn)
        
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)
        
        # Action Buttons
        action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        add_btn = QPushButton("➕ Add Expense")
        add_btn.setObjectName("success")
        add_btn.setMinimumHeight(45)
        add_btn.clicked.connect(self.add_expense)
        action_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setObjectName("primary")
        edit_btn.setMinimumHeight(45)
        edit_btn.clicked.connect(self.edit_expense)
        action_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setObjectName("danger")
        delete_btn.setMinimumHeight(45)
        delete_btn.clicked.connect(self.delete_expense)
        action_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("secondary")
        refresh_btn.setMinimumHeight(45)
        refresh_btn.clicked.connect(self.load_expenses)
        action_layout.addWidget(refresh_btn)
        
        action_group.setLayout(action_layout)
        main_layout.addWidget(action_group)
        
        # Expenses Table
        table_group = QGroupBox("Expenses")
        table_layout = QVBoxLayout()
        
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(5)
        self.expense_table.setHorizontalHeaderLabels(["ID", "Category", "Description", "Amount", "Date"])
        self.expense_table.verticalHeader().hide()
        self.expense_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.expense_table.setAlternatingRowColors(True)
        self.expense_table.setColumnHidden(0, True)
        
        self.expense_table.setColumnWidth(1, 150)
        self.expense_table.setColumnWidth(3, 140)
        self.expense_table.setColumnWidth(4, 160)

        header = self.expense_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        
        self.expense_table.setStyleSheet("""
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
        
        self.expense_table.verticalHeader().setDefaultSectionSize(50)
        
        table_layout.addWidget(self.expense_table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        self.setLayout(main_layout)
    
    def _create_summary_card(self, title, value, bg, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #e2e8f0;
            }}
        """)
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #475569;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {color};
        """)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card
    
    def update_summary(self):
        """Update summary with REAL monthly data"""
        session = self.db.get_session()
        try:
            # Get current month
            today = datetime.now().date()
            month_start = datetime(today.year, today.month, 1)
            month_end = datetime(today.year, today.month, today.day, 23, 59, 59)
            
            # Currency symbol
            currency = session.query(Setting).filter_by(key='currency_symbol').first()
            currency_symbol = currency.value if currency else 'Rs'
            
            # Monthly Sales (from Sale table)
            monthly_sales = session.query(func.sum(Sale.net_amount)).filter(
                Sale.sale_date >= month_start,
                Sale.sale_date <= month_end
            ).scalar() or 0
            
            # Monthly Expenses (from Expense table)
            monthly_expenses = session.query(func.sum(Expense.amount)).filter(
                Expense.expense_date >= month_start,
                Expense.expense_date <= month_end
            ).scalar() or 0
            
            # Net Profit = Sales - Expenses
            net_profit = monthly_sales - monthly_expenses
            
            # Update labels
            self.monthly_sales_label.setText(f"{currency_symbol} {monthly_sales:,.2f}")
            self.monthly_expenses_label.setText(f"{currency_symbol} {monthly_expenses:,.2f}")
            self.net_profit_label.setText(f"{currency_symbol} {net_profit:,.2f}")
            
            # Color coding for net profit
            if net_profit < 0:
                self.net_profit_label.setStyleSheet("font-size: 22px; font-weight: 700; color: #dc2626;")
            else:
                self.net_profit_label.setStyleSheet("font-size: 22px; font-weight: 700; color: #16a34a;")
            
            logger.info(f"Monthly Summary: Sales={monthly_sales}, Expenses={monthly_expenses}, Profit={net_profit}")
            
        except Exception as e:
            logger.error(f"Error updating summary: {e}")
        finally:
            session.close()
    
    def load_expenses(self):
        """Load expenses into table with proper date range"""
        session = self.db.get_session()
        try:
            query = session.query(Expense)
            
            # Apply date filter
            from_date = self.from_date.date().toPython()
            to_date = self.to_date.date().toPython()
            # Set time to end of day for to_date
            to_date = datetime(to_date.year, to_date.month, to_date.day, 23, 59, 59)
            query = query.filter(Expense.expense_date.between(from_date, to_date))
            
            # Apply category filter
            category = self.category_filter.currentText()
            if category != "All Categories":
                query = query.filter(Expense.category == category)
            
            expenses = query.order_by(Expense.expense_date.desc()).all()
            
            self.expense_table.setRowCount(len(expenses))
            
            currency = session.query(Setting).filter_by(key='currency_symbol').first()
            currency_symbol = currency.value if currency else 'Rs'
            
            for row, expense in enumerate(expenses):
                self.expense_table.setItem(row, 0, QTableWidgetItem(str(expense.id)))
                self.expense_table.setItem(row, 1, QTableWidgetItem(expense.category))
                self.expense_table.setItem(row, 2, QTableWidgetItem(expense.description or "-"))
                self.expense_table.setItem(row, 3, QTableWidgetItem(f"{currency_symbol} {expense.amount:,.2f}"))
                self.expense_table.setItem(row, 4, QTableWidgetItem(
                    expense.expense_date.strftime("%Y-%m-%d %I:%M %p")
                ))
            
            logger.info(f"Loaded {len(expenses)} expenses")
            
        except Exception as e:
            logger.error(f"Error loading expenses: {e}")
            QMessageBox.warning(self, "Error", f"Could not load expenses: {str(e)}")
        finally:
            session.close()
    
    def add_expense(self):
        dialog = AddExpenseDialog(self)
        if dialog.exec():
            self.load_expenses()
            self.update_summary()
            log_user_action('system', 'EXPENSE_ADD', "Added new expense")
    
    def edit_expense(self):
        selected = self.expense_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select an expense to edit.")
            return
        
        expense_id = int(self.expense_table.item(selected, 0).text())
        dialog = AddExpenseDialog(self, expense_id)
        if dialog.exec():
            self.load_expenses()
            self.update_summary()
            log_user_action('system', 'EXPENSE_EDIT', f"Edited expense ID: {expense_id}")
    
    def delete_expense(self):
        selected = self.expense_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select an expense to delete.")
            return
        
        expense_id = int(self.expense_table.item(selected, 0).text())
        category = self.expense_table.item(selected, 1).text()
        amount = self.expense_table.item(selected, 3).text()
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete this expense?\n\nCategory: {category}\nAmount: {amount}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = self.db.get_session()
            try:
                expense = session.query(Expense).filter_by(id=expense_id).first()
                if expense:
                    session.delete(expense)
                    session.commit()
                    log_user_action('system', 'EXPENSE_DELETE', f"Deleted expense ID: {expense_id}")
                    self.load_expenses()
                    self.update_summary()
            except Exception as e:
                session.rollback()
                logger.error(f"Error deleting expense: {e}")
                QMessageBox.critical(self, "Error", f"Could not delete expense: {str(e)}")
            finally:
                session.close()