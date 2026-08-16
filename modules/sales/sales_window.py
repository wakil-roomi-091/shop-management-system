"""
Sales Window - Point of Sale
Barcode-first POS with auto-suggest for fast checkout
"""

import sys
import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QLabel,
    QMessageBox,
    QHeaderView,
    QGroupBox,
    QSpinBox,
    QDoubleSpinBox,
    QScrollArea,
    QFrame,
    QDialog,
    QVBoxLayout as QVBoxLayoutDialog,
    QFormLayout,
    QTextEdit,
    QCompleter,
)
from PySide6.QtCore import Qt, QTimer, QStringListModel
from PySide6.QtGui import QColor, QFont

# Add parent directory to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from database import DatabaseManager, Product, Sale, SaleItem, Setting, Customer
from datetime import datetime


class SalesWindow(QWidget):
    """Main Point of Sale window - Barcode-first design"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.cart = []
        self.discount_percentage = 0.0
        self.discount_amount = 0.0
        self.selected_customer_id = None
        self.suggestion_list = []
        self._customer_search_timer = QTimer()
        self._customer_search_timer.setSingleShot(True)
        self._customer_search_timer.setInterval(300)
        self._customer_search_timer.timeout.connect(self._do_customer_search)

        self.setWindowTitle("Point of Sale")
        self.setGeometry(100, 100, 1200, 750)

        # Apply styles
        from ui.styles import get_app_style

        self.setStyleSheet(get_app_style())

        self.setup_ui()
        self.load_settings()
        self.scanner_input.setFocus()

    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Point of Sale")
        header_label.setObjectName("header")
        header_layout.addWidget(header_label)

        # Date/Time
        self.time_label = QLabel()
        self.time_label.setObjectName("subtitle")
        self.update_time()
        header_layout.addStretch()
        header_layout.addWidget(self.time_label)

        main_layout.addLayout(header_layout)

        # ===== BARCODE SCANNER SECTION =====
        scanner_group = QGroupBox("Search Product")
        scanner_layout = QHBoxLayout()
        scanner_layout.setSpacing(10)

        self.scanner_input = QLineEdit()
        self.scanner_input.setObjectName("search")
        self.scanner_input.setPlaceholderText("Scan barcode or type product name...")
        self.scanner_input.setMinimumHeight(40)

        # ===== AUTO-SUGGEST FUNCTIONALITY =====
        self.scanner_input.textChanged.connect(self.update_suggestions)
        self.suggestion_list = []
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchStartsWith)
        self.completer.activated.connect(self.on_completer_activated)
        self.scanner_input.setCompleter(self.completer)
        # =====================================

        self.scanner_input.returnPressed.connect(self.handle_scanner_input)
        scanner_layout.addWidget(self.scanner_input, 2)

        add_btn = QPushButton("Add to Cart")
        add_btn.setObjectName("primary")
        add_btn.setMinimumHeight(40)
        add_btn.clicked.connect(self.handle_scanner_input)
        scanner_layout.addWidget(add_btn)

        scanner_group.setLayout(scanner_layout)
        main_layout.addWidget(scanner_group)

        # Main Content - Split into two columns
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # LEFT COLUMN - Cart
        left_column = QVBoxLayout()
        left_column.setSpacing(15)

        # Cart Table
        cart_group = QGroupBox("Shopping Cart")
        cart_layout = QVBoxLayout()

        cart_header = QHBoxLayout()
        self.cart_count_label = QLabel("Items: 0")
        self.cart_count_label.setStyleSheet(
            "font-size: 13px; font-weight: 600; color: #64748b;"
        )
        cart_header.addWidget(self.cart_count_label)
        cart_header.addStretch()
        self.cart_total_label = QLabel("Total: Rs 0.00")
        self.cart_total_label.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #2563eb;"
        )
        cart_header.addWidget(self.cart_total_label)
        cart_layout.addLayout(cart_header)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(
            ["Product", "Price", "Qty", "Total", ""]
        )
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setColumnWidth(0, 280)
        self.cart_table.setColumnWidth(1, 100)
        self.cart_table.setColumnWidth(2, 140)
        self.cart_table.setColumnWidth(3, 120)
        self.cart_table.setColumnWidth(4, 100)
        self.cart_table.verticalHeader().setDefaultSectionSize(52)
        self.cart_table.verticalHeader().hide()
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.cart_table.setStyleSheet("""
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

        cart_layout.addWidget(self.cart_table)
        cart_group.setLayout(cart_layout)
        left_column.addWidget(cart_group)

        # RIGHT COLUMN - Summary & Payment wrapped in ScrollArea for responsive screens
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.NoFrame)
        right_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        right_widget = QWidget()
        right_widget.setStyleSheet("background: transparent;")
        right_column = QVBoxLayout(right_widget)
        right_column.setContentsMargins(0, 0, 4, 0)
        right_column.setSpacing(12)

        # Summary Section
        summary_group = QGroupBox("Sale Summary")
        summary_layout = QVBoxLayout()
        summary_layout.setSpacing(10)

        subtotal_layout = QHBoxLayout()
        subtotal_layout.addWidget(QLabel("Subtotal:"))
        subtotal_layout.addStretch()
        self.subtotal_label = QLabel("Rs 0.00")
        self.subtotal_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        subtotal_layout.addWidget(self.subtotal_label)
        summary_layout.addLayout(subtotal_layout)

        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("Discount:"))
        discount_layout.addStretch()

        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setSuffix("%")
        self.discount_input.setValue(0)
        self.discount_input.setMinimumWidth(80)
        self.discount_input.valueChanged.connect(self.update_totals)
        discount_layout.addWidget(self.discount_input)

        self.discount_amount_label = QLabel("Rs 0.00")
        self.discount_amount_label.setStyleSheet("font-size: 14px; color: #ef4444;")
        discount_layout.addWidget(self.discount_amount_label)
        summary_layout.addLayout(discount_layout)

        net_total_layout = QHBoxLayout()
        net_total_layout.addWidget(QLabel("Net Total:"))
        net_total_layout.addStretch()
        self.net_total_label = QLabel("Rs 0.00")
        self.net_total_label.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #3b82f6;"
        )
        net_total_layout.addWidget(self.net_total_label)
        summary_layout.addLayout(net_total_layout)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #e2e8f0;")
        summary_layout.addWidget(sep)

        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("Cash Received:"))
        payment_layout.addStretch()
        self.cash_input = QDoubleSpinBox()
        self.cash_input.setRange(0, 999999.99)
        self.cash_input.setPrefix("Rs ")
        self.cash_input.setMinimumWidth(120)
        self.cash_input.valueChanged.connect(self.calculate_change)
        payment_layout.addWidget(self.cash_input)
        summary_layout.addLayout(payment_layout)

        change_layout = QHBoxLayout()
        change_layout.addWidget(QLabel("Change:"))
        change_layout.addStretch()
        self.change_label = QLabel("Rs 0.00")
        self.change_label.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: #22c55e;"
        )
        change_layout.addWidget(self.change_label)
        summary_layout.addLayout(change_layout)

        summary_group.setLayout(summary_layout)
        right_column.addWidget(summary_group)

        # Customer Section
        customer_group = QGroupBox("Customer")
        customer_layout = QHBoxLayout()

        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("Search customer by name or phone...")
        self.customer_input.setMinimumHeight(35)
        self.customer_input.textChanged.connect(self._on_customer_search)
        customer_layout.addWidget(self.customer_input)

        self.customer_add_btn = QPushButton("+")
        self.customer_add_btn.setFixedSize(35, 35)
        self.customer_add_btn.setObjectName("success")
        self.customer_add_btn.setToolTip("Add new customer")
        self.customer_add_btn.clicked.connect(self.add_customer_from_sale)
        customer_layout.addWidget(self.customer_add_btn)

        customer_group.setLayout(customer_layout)
        right_column.addWidget(customer_group)

        self.customer_info_label = QLabel("No customer selected")
        self.customer_info_label.setStyleSheet(
            "font-size: 12px; color: #64748b; padding: 4px 8px;"
        )
        right_column.addWidget(self.customer_info_label)

        # Action Buttons
        action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout()
        action_layout.setSpacing(10)

        clear_btn = QPushButton("Clear Cart")
        clear_btn.setObjectName("secondary")
        clear_btn.setMinimumHeight(40)
        clear_btn.clicked.connect(self.clear_cart)
        action_layout.addWidget(clear_btn)

        clear_customer_btn = QPushButton("Clear Customer")
        clear_customer_btn.setObjectName("secondary")
        clear_customer_btn.setMinimumHeight(40)
        clear_customer_btn.clicked.connect(self.clear_customer)
        action_layout.addWidget(clear_customer_btn)

        complete_btn = QPushButton("Complete Sale")
        complete_btn.setObjectName("success")
        complete_btn.setMinimumHeight(50)
        complete_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 700;
                background-color: #22c55e;
                color: #ffffff;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
            QPushButton:pressed {
                background-color: #15803d;
            }
        """)
        complete_btn.clicked.connect(self.complete_sale)
        action_layout.addWidget(complete_btn)

        action_group.setLayout(action_layout)
        right_column.addWidget(action_group)
        right_column.addStretch()

        right_scroll.setWidget(right_widget)

        content_layout.addLayout(left_column, 3)
        content_layout.addWidget(right_scroll, 2)

        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    def update_time(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%A, %B %d, %Y  %I:%M %p"))
        QTimer.singleShot(1000, self.update_time)

    def load_settings(self):
        session = self.db.get_session()
        try:
            currency = session.query(Setting).filter_by(key="currency_symbol").first()
            self.currency = currency.value if currency else "Rs"
        except:
            self.currency = "Rs"
        finally:
            session.close()

    # ===== AUTO-SUGGEST METHODS =====
    def update_suggestions(self, text):
        """Update product suggestions as user types"""
        if not text or len(text) < 1:
            self.completer.setModel(QStringListModel([]))
            return

        session = self.db.get_session()
        try:
            # Search products by name starting with the typed text
            products = (
                session.query(Product)
                .filter(Product.name.ilike(f"{text}%"))
                .limit(20)
                .all()
            )

            # Create suggestion list - ONLY PRODUCT NAME (exactly as in products table)
            suggestions = []
            for product in products:
                suggestions.append(product.name)

            # Update completer
            model = QStringListModel(suggestions)
            self.completer.setModel(model)
            self.suggestion_list = products

        except Exception as e:
            print(f"Error updating suggestions: {e}")
        finally:
            session.close()

    def on_completer_activated(self, text):
        """When user selects a suggestion"""
        # Extract product name from suggestion text
        product_name = text
        self.scanner_input.setText(product_name)
        self.handle_scanner_input()

    def handle_scanner_input(self):
        """Handle barcode scan or manual search with suggestions"""
        text = self.scanner_input.text().strip()
        if not text:
            return

        # Try to find product by barcode first (exact match)
        session = self.db.get_session()
        try:
            product = session.query(Product).filter(Product.barcode == text).first()

            if product:
                self.add_product_to_cart(product)
                self.scanner_input.clear()
                self.scanner_input.setFocus()
                return
        finally:
            session.close()

        # Try to find by name (starts with)
        session = self.db.get_session()
        try:
            product = (
                session.query(Product).filter(Product.name.ilike(f"{text}%")).first()
            )

            if product:
                self.add_product_to_cart(product)
                self.scanner_input.clear()
                self.scanner_input.setFocus()
                return
        finally:
            session.close()

        # If nothing found
        QMessageBox.warning(self, "Not Found", f"No product found matching '{text}'.")
        self.scanner_input.selectAll()

    def open_manual_search(self):
        """Open manual search dialog"""
        from .manual_search import ManualSearchDialog

        dialog = ManualSearchDialog(self.db, self)
        if dialog.exec():
            product = dialog.get_selected_product()
            if product:
                self.add_product_to_cart(product)

    def add_product_to_cart(self, product):
        """Add a product to cart"""
        if product.current_stock <= 0:
            QMessageBox.warning(
                self, "Error", f"Product '{product.name}' is out of stock!"
            )
            return

        for item in self.cart:
            if item["product_id"] == product.id:
                if item["quantity"] >= product.current_stock:
                    QMessageBox.warning(
                        self,
                        "Insufficient Stock",
                        f"Cannot add more '{product.name}'. Only {product.current_stock} available.",
                    )
                    return
                item["quantity"] += 1
                item["total"] = item["quantity"] * item["price"]
                self.update_cart_table()
                self.update_totals()
                self.scanner_input.setFocus()
                return

        self.cart.append(
            {
                "product_id": product.id,
                "name": product.name,
                "price": product.selling_price,
                "quantity": 1,
                "total": product.selling_price,
            }
        )

        self.update_cart_table()
        self.update_totals()
        self.scanner_input.setFocus()

    def _on_customer_search(self):
        self._customer_search_timer.start()

    def _do_customer_search(self):
        search_text = self.customer_input.text().strip()
        if not search_text:
            self.customer_info_label.setText("No customer selected")
            self.selected_customer_id = None
            return

        session = self.db.get_session()
        try:
            customer = (
                session.query(Customer)
                .filter(
                    (Customer.name.ilike(f"%{search_text}%"))
                    | (Customer.phone.ilike(f"%{search_text}%"))
                )
                .first()
            )

            if customer:
                self.selected_customer_id = customer.id
                self.customer_info_label.setText(
                    f"✅ {customer.name} - {customer.phone}\n"
                    f"Purchases: {customer.total_purchases} | Spent: {self.currency}{customer.total_spent:,.2f}"
                )
                self.customer_info_label.setStyleSheet(
                    "font-size: 12px; color: #16a34a; padding: 4px 8px;"
                )
            else:
                self.customer_info_label.setText(
                    "❌ Customer not found. Click + to add."
                )
                self.customer_info_label.setStyleSheet(
                    "font-size: 12px; color: #ef4444; padding: 4px 8px;"
                )
                self.selected_customer_id = None
        except Exception as e:
            print(f"Error searching customer: {e}")
        finally:
            session.close()

    def add_customer_from_sale(self):
        """Quick add customer"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Customer")
        dialog.setModal(True)
        dialog.setFixedSize(400, 350)

        layout = QVBoxLayoutDialog()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Add New Customer")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        form_layout = QFormLayout()

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter customer name")
        name_input.setMinimumHeight(32)
        form_layout.addRow("Name:", name_input)

        phone_input = QLineEdit()
        phone_input.setPlaceholderText("Enter phone number")
        phone_input.setMinimumHeight(32)
        form_layout.addRow("Phone:", phone_input)

        email_input = QLineEdit()
        email_input.setPlaceholderText("Enter email (optional)")
        email_input.setMinimumHeight(32)
        form_layout.addRow("Email:", email_input)

        address_input = QTextEdit()
        address_input.setMaximumHeight(60)
        address_input.setPlaceholderText("Enter address (optional)")
        form_layout.addRow("Address:", address_input)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Customer")
        save_btn.setObjectName("success")
        save_btn.clicked.connect(
            lambda: self._save_customer_from_dialog(
                name_input, phone_input, email_input, address_input, dialog
            )
        )
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()

    def _save_customer_from_dialog(
        self, name_input, phone_input, email_input, address_input, dialog
    ):
        name = name_input.text().strip()
        phone = phone_input.text().strip()

        if not name:
            QMessageBox.warning(dialog, "Error", "Name is required!")
            return
        if not phone:
            QMessageBox.warning(dialog, "Error", "Phone number is required!")
            return
        if len(phone) < 7:
            QMessageBox.warning(dialog, "Error", "Please enter a valid phone number!")
            return

        session = self.db.get_session()
        try:
            existing = session.query(Customer).filter_by(phone=phone).first()
            if existing:
                QMessageBox.warning(
                    dialog, "Error", "Customer with this phone already exists!"
                )
                return

            customer = Customer(
                name=name,
                phone=phone,
                email=email_input.text().strip() or None,
                address=address_input.toPlainText().strip() or None,
            )
            session.add(customer)
            session.commit()

            self.selected_customer_id = customer.id
            self.customer_input.setText(name)
            self.customer_info_label.setText(
                f"✅ {customer.name} - {customer.phone}\n" f"New customer added!"
            )
            self.customer_info_label.setStyleSheet(
                "font-size: 12px; color: #16a34a; padding: 4px 8px;"
            )

            QMessageBox.information(
                dialog, "Success", f"Customer '{name}' added successfully!"
            )
            dialog.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(dialog, "Error", f"Could not save customer: {str(e)}")
        finally:
            session.close()

    def clear_customer(self):
        self.selected_customer_id = None
        self.customer_input.clear()
        self.customer_info_label.setText("No customer selected")
        self.customer_info_label.setStyleSheet(
            "font-size: 12px; color: #64748b; padding: 4px 8px;"
        )

    def update_cart_table(self):
        """Update the cart table display"""
        self.cart_table.setRowCount(len(self.cart))

        for row, item in enumerate(self.cart):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.cart_table.setItem(
                row, 1, QTableWidgetItem(f"{self.currency}{item['price']:,.2f}")
            )

            qty_widget = QWidget()
            qty_layout = QHBoxLayout()
            qty_layout.setContentsMargins(2, 2, 2, 2)
            qty_layout.setSpacing(0)

            qty_spin = QSpinBox()
            qty_spin.setRange(1, 999)
            qty_spin.setValue(item["quantity"])
            qty_spin.setMinimumHeight(28)
            qty_spin.setMinimumWidth(100)
            qty_spin.setMaximumWidth(120)
            qty_spin.setStyleSheet("""
                QSpinBox {
                    font-size: 13px;
                    padding: 2px 4px;
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    background-color: white;
                }
                QSpinBox::up-button {
                    width: 18px;
                    border-top-right-radius: 4px;
                    background-color: #f3f4f6;
                }
                QSpinBox::up-button:hover {
                    background-color: #e5e7eb;
                }
                QSpinBox::down-button {
                    width: 18px;
                    border-bottom-right-radius: 4px;
                    background-color: #f3f4f6;
                }
                QSpinBox::down-button:hover {
                    background-color: #e5e7eb;
                }
                QSpinBox::up-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-bottom: 4px solid #6b7280;
                    margin-bottom: 2px;
                }
                QSpinBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid #6b7280;
                    margin-top: 2px;
                }
            """)
            qty_spin.valueChanged.connect(
                lambda val, r=row: self.update_quantity(r, val)
            )
            qty_layout.addWidget(qty_spin)
            qty_widget.setLayout(qty_layout)
            self.cart_table.setCellWidget(row, 2, qty_widget)

            self.cart_table.setItem(
                row, 3, QTableWidgetItem(f"{self.currency}{item['total']:,.2f}")
            )

            remove_btn = QPushButton("×")
            remove_btn.setObjectName("danger")
            remove_btn.setFixedSize(40, 36)
            remove_btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    font-weight: 700;
                    padding: 0px;
                    border-radius: 4px;
                    background-color: #ef4444;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
                QPushButton:pressed {
                    background-color: #b91c1c;
                }
            """)
            remove_btn.clicked.connect(lambda r=row: self.remove_from_cart(r))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(remove_btn)
            btn_widget.setLayout(btn_layout)
            self.cart_table.setCellWidget(row, 4, btn_widget)

        total_items = sum(item["quantity"] for item in self.cart)
        total_amount = sum(item["total"] for item in self.cart)
        self.cart_count_label.setText(f"Items: {total_items}")
        self.cart_total_label.setText(f"Total: {self.currency}{total_amount:,.2f}")

    def update_quantity(self, row, value):
        if row < len(self.cart):
            session = self.db.get_session()
            try:
                product = (
                    session.query(Product)
                    .filter_by(id=self.cart[row]["product_id"])
                    .first()
                )
                if product:
                    if value > product.current_stock:
                        QMessageBox.warning(
                            self,
                            "Insufficient Stock",
                            f"Cannot set quantity to {value}. Only {product.current_stock} available for '{product.name}'.",
                        )
                        self.update_cart_table()
                        self.update_totals()
                        return
            except Exception as e:
                print(f"Error checking stock: {e}")
            finally:
                session.close()

            self.cart[row]["quantity"] = value
            self.cart[row]["total"] = value * self.cart[row]["price"]
            self.update_cart_table()
            self.update_totals()

    def remove_from_cart(self, row):
        if row < len(self.cart):
            self.cart.pop(row)
            self.update_cart_table()
            self.update_totals()

    def update_totals(self):
        subtotal = sum(item["total"] for item in self.cart)

        self.discount_percentage = self.discount_input.value()
        discount_amount = subtotal * (self.discount_percentage / 100)
        self.discount_amount = discount_amount

        net_total = subtotal - discount_amount

        self.subtotal_label.setText(f"{self.currency}{subtotal:,.2f}")
        self.discount_amount_label.setText(f"{self.currency}{discount_amount:,.2f}")
        self.net_total_label.setText(f"{self.currency}{net_total:,.2f}")

        self.calculate_change()

    def calculate_change(self):
        cash = self.cash_input.value()
        net_total = float(
            self.net_total_label.text().replace(f"{self.currency}", "").replace(",", "")
        )
        change = cash - net_total
        if change < 0:
            self.change_label.setText(f"{self.currency}0.00")
            self.change_label.setStyleSheet(
                "font-size: 16px; font-weight: 600; color: #ef4444;"
            )
        else:
            self.change_label.setText(f"{self.currency}{change:,.2f}")
            self.change_label.setStyleSheet(
                "font-size: 16px; font-weight: 600; color: #22c55e;"
            )

    def clear_cart(self):
        if self.cart:
            reply = QMessageBox.question(
                self,
                "Clear Cart",
                "Are you sure you want to clear the cart?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.cart = []
                self.discount_input.setValue(0)
                self.cash_input.setValue(0)
                self.update_cart_table()
                self.update_totals()
                self.scanner_input.setFocus()

    def complete_sale(self):
        if not self.cart:
            QMessageBox.warning(
                self, "Error", "Cart is empty. Please add items before completing sale."
            )
            return

        net_total = float(
            self.net_total_label.text().replace(f"{self.currency}", "").replace(",", "")
        )
        cash = self.cash_input.value()

        if cash < net_total:
            QMessageBox.warning(
                self,
                "Error",
                f"Insufficient cash. Please enter at least {self.currency}{net_total:,.2f}",
            )
            return

        session = self.db.get_session()
        try:
            for item in self.cart:
                product = (
                    session.query(Product).filter_by(id=item["product_id"]).first()
                )
                if product:
                    if item["quantity"] > product.current_stock:
                        QMessageBox.warning(
                            self,
                            "Insufficient Stock",
                            f"Not enough stock for '{product.name}'. Available: {product.current_stock}, Requested: {item['quantity']}",
                        )
                        return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Stock validation failed: {str(e)}")
            return
        finally:
            session.close()

        reply = QMessageBox.question(
            self,
            "Confirm Sale",
            f"Total: {self.currency}{net_total:,.2f}\nCash: {self.currency}{cash:,.2f}\nChange: {self.currency}{cash - net_total:,.2f}\n\nProceed with sale?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            session = self.db.get_session()
            try:
                last_sale = session.query(Sale).order_by(Sale.id.desc()).first()
                if last_sale:
                    invoice_num = int(last_sale.invoice_number.split("-")[1]) + 1
                else:
                    invoice_num = 1
                invoice_number = f"INV-{invoice_num:06d}"

                subtotal = sum(item["total"] for item in self.cart)
                discount_amount = subtotal * (self.discount_percentage / 100)
                net_total = subtotal - discount_amount

                sale = Sale(
                    invoice_number=invoice_number,
                    customer_id=self.selected_customer_id,
                    total_amount=subtotal,
                    discount_amount=discount_amount,
                    discount_percentage=self.discount_percentage,
                    net_amount=net_total,
                    cash_received=cash,
                    change_returned=cash - net_total,
                    profit=0,
                )
                session.add(sale)
                session.flush()

                total_profit = 0
                sale_items = []

                for item in self.cart:
                    product = (
                        session.query(Product).filter_by(id=item["product_id"]).first()
                    )
                    if product:
                        profit_per_item = product.selling_price - product.buying_price
                        item_profit = profit_per_item * item["quantity"]
                        total_profit += item_profit

                        sale_item = SaleItem(
                            sale_id=sale.id,
                            product_id=item["product_id"],
                            quantity=item["quantity"],
                            unit_price=item["price"],
                            total_price=item["total"],
                            discount_per_product=0,
                        )
                        session.add(sale_item)

                        product.current_stock -= item["quantity"]

                        sale_items.append(
                            {
                                "name": item["name"],
                                "quantity": item["quantity"],
                                "price": item["price"],
                                "total": item["total"],
                            }
                        )

                if self.selected_customer_id:
                    customer = (
                        session.query(Customer)
                        .filter_by(id=self.selected_customer_id)
                        .first()
                    )
                    if customer:
                        customer.total_purchases += 1
                        customer.total_spent += net_total
                        customer.last_purchase_date = datetime.now()

                sale.profit = total_profit

                session.commit()

                receipt_data = {
                    "invoice_number": invoice_number,
                    "sale_date": sale.sale_date,
                    "items": sale_items,
                    "subtotal": subtotal,
                    "discount_amount": discount_amount,
                    "discount_percentage": self.discount_percentage,
                    "net_total": net_total,
                    "cash_received": cash,
                    "change_returned": cash - net_total,
                }

                from .receipt_window import ReceiptWindow

                receipt = ReceiptWindow(receipt_data, self)
                receipt.exec()

                self.cart = []
                self.discount_input.setValue(0)
                self.cash_input.setValue(0)
                self.update_cart_table()
                self.update_totals()
                self.scanner_input.setFocus()

            except Exception as e:
                session.rollback()
                QMessageBox.critical(
                    self, "Error", f"Could not complete sale: {str(e)}"
                )
            finally:
                session.close()
