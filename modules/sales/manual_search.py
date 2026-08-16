"""
Manual Search Dialog - Fallback for non-barcode products
"""

import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
    QHeaderView, QAbstractItemView, QMessageBox, QCompleter
)
from PySide6.QtCore import Qt, QTimer, QStringListModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import Product, Setting


class ManualSearchDialog(QDialog):
    """Manual product search dialog with auto-suggest"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.selected_product = None
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self.search_products)
        
        self.setWindowTitle("Search Product")
        self.setModal(True)
        self.setMinimumSize(450, 380)
        self.resize(600, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Search Products")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(title)
        
        # Search input with auto-suggest
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or barcode...")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self._on_search)
        
        # ===== AUTO-SUGGEST =====
        self.search_input.textChanged.connect(self.update_suggestions)
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchStartsWith)
        self.search_input.setCompleter(self.completer)
        # =============================
        
        layout.addWidget(self.search_input)
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Price", "Stock"])
        self.table.verticalHeader().hide()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnHidden(0, True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)

        self.table.doubleClicked.connect(self.select_product)
        
        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px 10px;
            }
            QTableWidget::item:selected {
                background-color: #eff6ff;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 8px 10px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        select_btn = QPushButton("Select")
        select_btn.setObjectName("primary")
        select_btn.setMinimumHeight(40)
        select_btn.setMinimumWidth(100)
        select_btn.clicked.connect(self.select_product)
        button_layout.addWidget(select_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load initial results
        self.search_products()
    
    def update_suggestions(self, text):
        """Update product suggestions as user types"""
        if not text or len(text) < 1:
            self.completer.setModel(QStringListModel([]))
            return
        
        session = self.db.get_session()
        try:
            products = session.query(Product).filter(
                Product.name.ilike(f'{text}%')
            ).limit(20).all()
            
            suggestions = []
            for product in products:
                suggestions.append(product.name)
            
            model = QStringListModel(suggestions)
            self.completer.setModel(model)
            
        except Exception as e:
            print(f"Error updating suggestions: {e}")
        finally:
            session.close()
    
    def _on_search(self):
        self._search_timer.start()
    
    def search_products(self):
        """Search for products"""
        search_text = self.search_input.text().strip().lower()
        
        session = self.db.get_session()
        try:
            query = session.query(Product)
            
            if search_text:
                query = query.filter(
                    (Product.name.ilike(f'%{search_text}%')) |
                    (Product.barcode.ilike(f'%{search_text}%'))
                )
            
            # Get currency symbol
            currency = session.query(Setting).filter_by(key='currency_symbol').first()
            currency_symbol = currency.value if currency else 'Rs'
            
            products = query.order_by(Product.name).limit(50).all()
            
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                self.table.setItem(row, 0, QTableWidgetItem(str(product.id)))
                self.table.setItem(row, 1, QTableWidgetItem(product.name))
                self.table.setItem(row, 2, QTableWidgetItem(f"{currency_symbol}{product.selling_price:,.2f}"))
                self.table.setItem(row, 3, QTableWidgetItem(str(product.current_stock)))
                
        except Exception as e:
            print(f"Error searching: {e}")
        finally:
            session.close()
    
    def select_product(self):
        """Select the current product"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a product.")
            return
        
        product_id = int(self.table.item(row, 0).text())
        
        session = self.db.get_session()
        try:
            self.selected_product = session.query(Product).filter_by(id=product_id).first()
        finally:
            session.close()
        
        self.accept()
    
    def get_selected_product(self):
        """Get the selected product"""
        return self.selected_product