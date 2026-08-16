"""
Products Window
Main product management interface
"""

import sys
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
    QMessageBox, QHeaderView, QComboBox, QGroupBox,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QColor

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import DatabaseManager, Product, Category
from database.models import Setting, SaleItem
from .add_product_dialog import AddProductDialog


class Palette:
    BG = "#F8FAFC"
    WHITE = "#FFFFFF"
    BORDER = "#E2E8F0"
    PRIMARY = "#2563EB"
    SUCCESS = "#16A34A"
    WARNING = "#F59E0B"
    DANGER = "#DC2626"
    TEXT_DARK = "#0F172A"
    TEXT_MUTED = "#64748B"


def rgba(hex_color, alpha):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


class ProductsWindow(QWidget):
    """Main product management window"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self._show_only_low_stock = False
        self._low_stock_products = []
        self._stock_label_clickable = False
        
        self.setWindowTitle("Product Management")
        self.setGeometry(100, 100, 1200, 700)
        
        # Apply styles
        from ui.styles import get_app_style
        self.setStyleSheet(get_app_style())
        
        self.setup_ui()
        self.load_products()
    
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Product Management")
        title_label.setObjectName("header")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Search and Filter Bar
        search_group = QGroupBox("Search & Filter")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search")
        self.search_input.setPlaceholderText("Search by name, barcode, or category...")
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(self.search_input)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.load_categories()
        self.category_filter.currentTextChanged.connect(self.search_products)
        search_layout.addWidget(self.category_filter)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # Button Bar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_btn = QPushButton("Add Product")
        add_btn.setObjectName("success")
        add_btn.clicked.connect(self.add_product)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("primary")
        edit_btn.clicked.connect(self.edit_product)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self.delete_product)
        button_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("secondary")
        refresh_btn.clicked.connect(self.load_products)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        # Stock status label - CLICKABLE via event filter
        self.stock_label = QLabel("")
        self.stock_label.setObjectName("info_text")
        self.stock_label.installEventFilter(self)
        button_layout.addWidget(self.stock_label)
        
        main_layout.addLayout(button_layout)
        
        # Products Table - WITH BARCODE COLUMN
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Barcode", "Name", "Category", "Buying Price", 
            "Selling Price", "Stock", "Min Stock", "Status"
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
        self.table.setColumnWidth(1, 140)   # Barcode
        self.table.setColumnWidth(3, 140)   # Category
        self.table.setColumnWidth(4, 120)   # Buying Price
        self.table.setColumnWidth(5, 120)   # Selling Price
        self.table.setColumnWidth(6, 90)    # Stock
        self.table.setColumnWidth(7, 90)    # Min Stock
        self.table.setColumnWidth(8, 110)   # Status
        self.table.setColumnHidden(0, True) # Hide ID

        # Responsive column stretching: Product Name stretches to fill all available width
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        header.setSectionResizeMode(5, QHeaderView.Interactive)
        header.setSectionResizeMode(6, QHeaderView.Interactive)
        header.setSectionResizeMode(7, QHeaderView.Interactive)
        header.setSectionResizeMode(8, QHeaderView.Interactive)
        
        self.table.doubleClicked.connect(self.edit_product)
        
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
    
    def eventFilter(self, obj, event):
        """Handle click events on the stock label"""
        if obj == self.stock_label and event.type() == QEvent.MouseButtonPress:
            if self._stock_label_clickable:
                self._on_stock_label_click()
                return True
        return super().eventFilter(obj, event)
    
    def load_categories(self):
        """Load categories into filter dropdown"""
        session = self.db.get_session()
        try:
            categories = session.query(Category).order_by(Category.name).all()
            for category in categories:
                self.category_filter.addItem(category.name)
        except Exception as e:
            print(f"Error loading categories: {e}")
        finally:
            session.close()
    
    def load_products(self):
        """Load all products into table"""
        self._show_only_low_stock = False
        session = self.db.get_session()
        try:
            query = session.query(Product).join(Category)
            products = query.all()
            
            # Get currency symbol
            currency = session.query(Setting).filter_by(key='currency_symbol').first()
            currency_symbol = currency.value if currency else 'Rs'
            
            self._populate_table(products, currency_symbol)
            self._update_stock_summary(products)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load products: {str(e)}")
        finally:
            session.close()
    
    def search_products(self):
        """Search products by name, barcode, or category"""
        search_text = self.search_input.text().strip().lower()
        category_filter = self.category_filter.currentText()
        
        session = self.db.get_session()
        try:
            query = session.query(Product).join(Category)
            
            # Apply category filter
            if category_filter != "All Categories":
                query = query.filter(Category.name == category_filter)
            
            # Apply search filter
            if search_text:
                query = query.filter(
                    (Product.name.ilike(f'%{search_text}%')) |
                    (Product.barcode.ilike(f'%{search_text}%')) |
                    (Category.name.ilike(f'%{search_text}%'))
                )
            
            products = query.all()
            
            # Get currency symbol
            currency = session.query(Setting).filter_by(key='currency_symbol').first()
            currency_symbol = currency.value if currency else 'Rs'
            
            self._populate_table(products, currency_symbol)
            self._update_stock_summary(products)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not search products: {str(e)}")
        finally:
            session.close()
    
    def _populate_table(self, products, currency_symbol):
        """Populate the table with products - STATUS ALWAYS VISIBLE"""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product.id)))
            
            # Barcode - show "-" if empty
            barcode_text = product.barcode if product.barcode else "-"
            self.table.setItem(row, 1, QTableWidgetItem(barcode_text))
            
            self.table.setItem(row, 2, QTableWidgetItem(product.name))
            self.table.setItem(
                row, 3,
                QTableWidgetItem(product.category.name if product.category else "Uncategorized"),
            )
            self.table.setItem(row, 4, QTableWidgetItem(f"{currency_symbol}{product.buying_price:,.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{currency_symbol}{product.selling_price:,.2f}"))
            
            # Stock with color
            stock_item = QTableWidgetItem(str(product.current_stock))
            if product.current_stock == 0:
                stock_item.setForeground(QColor(Palette.DANGER))
            elif product.current_stock <= product.min_stock_level:
                stock_item.setForeground(QColor(Palette.WARNING))
            self.table.setItem(row, 6, stock_item)
            
            self.table.setItem(row, 7, QTableWidgetItem(str(product.min_stock_level)))
            
            # ALWAYS show status badge
            self._set_status_badge(row, 8, product.stock_status)
        
        self.table.setSortingEnabled(True)
    
    def _set_status_badge(self, row, column, status):
        """Set the status badge - ALWAYS VISIBLE"""
        color_map = {
            "Critical": Palette.DANGER,
            "Warning": Palette.WARNING,
            "Normal": Palette.SUCCESS
        }
        color = color_map.get(status, Palette.SUCCESS)
        
        # Store the status text in the table
        self.table.setItem(row, column, QTableWidgetItem(status))
        
        # Create the badge
        badge = QLabel(status)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                font-weight: 700;
                color: {color};
                background-color: {rgba(color, 0.12)};
                border-radius: 10px;
                padding: 3px 12px;
            }}
        """)
        
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(4, 2, 4, 2)
        wrapper_layout.addWidget(badge)
        wrapper_layout.addStretch()
        self.table.setCellWidget(row, column, wrapper)
    
    def _update_stock_summary(self, products):
        """Update stock summary with clickable warning"""
        low_stock_products = [p for p in products if p.current_stock <= p.min_stock_level]
        low_stock_count = len(low_stock_products)
        self._low_stock_products = low_stock_products
        
        if low_stock_count > 0:
            self.stock_label.setText(f"⚠ {low_stock_count} product(s) low on stock - Click to view")
            self.stock_label.setStyleSheet(
                f"color: #dc2626; font-weight: 600; font-size: 13px; text-decoration: underline;"
            )
            self.stock_label.setCursor(Qt.PointingHandCursor)
            self._stock_label_clickable = True
        else:
            self.stock_label.setText("✅ All products have sufficient stock")
            self.stock_label.setStyleSheet(
                f"color: #22c55e; font-weight: 600; font-size: 13px;"
            )
            self.stock_label.setCursor(Qt.ArrowCursor)
            self._stock_label_clickable = False
    
    def _on_stock_label_click(self):
        """Handle click on stock warning label - filter to show low stock products"""
        if hasattr(self, '_low_stock_products') and self._low_stock_products:
            # Clear search and filter
            self.search_input.clear()
            self.category_filter.setCurrentText("All Categories")
            self._populate_table(self._low_stock_products, self.currency)
            self.stock_label.setText(f"⚠ Showing {len(self._low_stock_products)} low stock product(s) - Click to view all")
            self.stock_label.setStyleSheet(
                f"color: #dc2626; font-weight: 600; font-size: 13px; text-decoration: underline;"
            )
            self._stock_label_clickable = True
    
    def add_product(self):
        """Open dialog to add a new product"""
        dialog = AddProductDialog(self)
        if dialog.exec():
            self.load_products()
    
    def edit_product(self):
        """Open dialog to edit selected product"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a product to edit.")
            return
        
        product_id = int(self.table.item(selected, 0).text())
        dialog = AddProductDialog(self, product_id)
        if dialog.exec():
            self.load_products()
    
    def delete_product(self):
        """Delete selected product"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")
            return
        
        product_id = int(self.table.item(selected, 0).text())
        product_name = self.table.item(selected, 2).text()
        
        # Check if product has sales history
        session = self.db.get_session()
        try:
            sale_count = session.query(SaleItem).filter_by(product_id=product_id).count()
            
            if sale_count > 0:
                QMessageBox.warning(
                    self,
                    "Cannot Delete Product",
                    f"❌ Cannot delete '{product_name}'\n\n"
                    f"This product has been sold {sale_count} time(s).\n"
                    "Products with sales history cannot be deleted.\n\n"
                    "This preserves your sales records and reports accuracy."
                )
                return
                
        except Exception as e:
            print(f"Error checking sales: {e}")
        finally:
            session.close()
        
        # If no sales history, allow normal delete
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{product_name}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            session = self.db.get_session()
            try:
                product = session.query(Product).filter_by(id=product_id).first()
                if product:
                    session.delete(product)
                    session.commit()
                    QMessageBox.information(self, "Success", f"Product '{product_name}' deleted successfully!")
                    self.load_products()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Could not delete product: {str(e)}")
            finally:
                session.close()