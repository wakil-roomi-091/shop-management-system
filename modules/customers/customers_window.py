"""
Customers Window
Main customer management interface
"""

import sys
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
    QMessageBox, QGroupBox, QAbstractItemView, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import DatabaseManager, Customer
from .add_customer_dialog import AddCustomerDialog


class CustomersWindow(QWidget):
    """Main customer management window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.load_customers)
        
        self.setWindowTitle("Customer Management")
        
        # Apply styles
        from ui.styles import get_app_style
        self.setStyleSheet(get_app_style())
        
        self.setup_ui()
        self.load_customers()
    
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Customer Management")
        title_label.setObjectName("header")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Search Bar
        search_group = QGroupBox("Search Customer")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Search by name, phone, or email...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.search_input)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # Button Bar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_btn = QPushButton("Add Customer")
        add_btn.setObjectName("success")
        add_btn.clicked.connect(self.add_customer)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("primary")
        edit_btn.clicked.connect(self.edit_customer)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self.delete_customer)
        button_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("secondary")
        refresh_btn.clicked.connect(self.load_customers)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        # Count label
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("font-size: 13px; color: #64748b;")
        button_layout.addWidget(self.count_label)
        
        main_layout.addLayout(button_layout)
        
        # Customers Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Email", "Purchases", "Total Spent", "Last Purchase"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()
        
        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background-color: white;
                gridline-color: #e2e8f0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px 10px;
                border-right: 1px solid #e2e8f0;
            }
            QTableWidget::item:last {
                border-right: none;
            }
            QTableWidget::item:selected {
                background-color: #eff6ff;
                color: #0f172a;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #0f172a;
                padding: 12px 10px;
                border: none;
                border-right: 1px solid #e2e8f0;
                border-bottom: 2px solid #e2e8f0;
                font-size: 13px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTableWidget::item:alternate {
                background-color: #f8fafc;
            }
        """)
        
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.setColumnWidth(2, 140)   # Phone
        self.table.setColumnWidth(3, 180)   # Email
        self.table.setColumnWidth(4, 100)   # Purchases
        self.table.setColumnWidth(5, 130)   # Total Spent
        self.table.setColumnWidth(6, 160)   # Last Purchase
        self.table.setColumnHidden(0, True) # Hide ID

        # Responsive column stretching: Customer Name stretches to fill available space
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        header.setSectionResizeMode(5, QHeaderView.Interactive)
        header.setSectionResizeMode(6, QHeaderView.Interactive)
        
        self.table.doubleClicked.connect(self.edit_customer)
        
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
    
    def _on_search_text_changed(self):
        """Handle search text change with debounce"""
        self._search_timer.start()
    
    def load_customers(self):
        """Load customers into table"""
        session = self.db.get_session()
        try:
            query = session.query(Customer)
            
            # Apply search filter
            search_text = self.search_input.text().strip().lower()
            if search_text:
                query = query.filter(
                    (Customer.name.ilike(f'%{search_text}%')) |
                    (Customer.phone.ilike(f'%{search_text}%')) |
                    (Customer.email.ilike(f'%{search_text}%'))
                )
            
            customers = query.order_by(Customer.name).all()
            
            self.table.setRowCount(len(customers))
            
            for row, customer in enumerate(customers):
                self.table.setItem(row, 0, QTableWidgetItem(str(customer.id)))
                self.table.setItem(row, 1, QTableWidgetItem(customer.name))
                self.table.setItem(row, 2, QTableWidgetItem(customer.phone))
                self.table.setItem(row, 3, QTableWidgetItem(customer.email or "-"))
                self.table.setItem(row, 4, QTableWidgetItem(str(customer.total_purchases)))
                self.table.setItem(row, 5, QTableWidgetItem(f"Rs {customer.total_spent:,.2f}"))
                
                last_purchase = customer.last_purchase_date
                if last_purchase:
                    self.table.setItem(row, 6, QTableWidgetItem(last_purchase.strftime("%b %d, %Y")))
                else:
                    self.table.setItem(row, 6, QTableWidgetItem("-"))
            
            self.count_label.setText(f"Total: {len(customers)} customers")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load customers: {str(e)}")
        finally:
            session.close()
    
    def add_customer(self):
        """Open dialog to add a new customer"""
        dialog = AddCustomerDialog(self)
        if dialog.exec():
            self.load_customers()
    
    def edit_customer(self):
        """Open dialog to edit selected customer"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a customer to edit.")
            return
        
        customer_id = int(self.table.item(selected, 0).text())
        dialog = AddCustomerDialog(self, customer_id)
        if dialog.exec():
            self.load_customers()
    
    def delete_customer(self):
        """Delete selected customer"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a customer to delete.")
            return
        
        customer_id = int(self.table.item(selected, 0).text())
        customer_name = self.table.item(selected, 1).text()
        customer_phone = self.table.item(selected, 2).text()
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{customer_name}' ({customer_phone})?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = self.db.get_session()
            try:
                customer = session.query(Customer).filter_by(id=customer_id).first()
                if customer:
                    # Check if customer has sales
                    sales_count = len(customer.sales)
                    if sales_count > 0:
                        reply2 = QMessageBox.question(
                            self,
                            "Customer Has Sales",
                            f"This customer has {sales_count} purchase(s). Deleting will remove the customer from those sales.\n\nContinue?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        if reply2 == QMessageBox.No:
                            return
                    
                    session.delete(customer)
                    session.commit()
                    QMessageBox.information(self, "Success", f"Customer '{customer_name}' deleted successfully!")
                    self.load_customers()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Could not delete customer: {str(e)}")
            finally:
                session.close()