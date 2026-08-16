"""
Receipt Window
Professional invoice/receipt display after sale
"""

import sys
import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QPushButton,
    QLabel,
    QFrame,
    QMessageBox,
    QFileDialog,
    QScrollArea,
)
from PySide6.QtCore import Qt
from datetime import datetime
import pytz

# Add parent directory to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from database import DatabaseManager, Setting


class ReceiptWindow(QDialog):
    """Professional Receipt/Invoice Window matching approved mockup"""

    def __init__(self, sale_data, parent=None):
        super().__init__(parent)
        self.sale_data = sale_data
        self.db = DatabaseManager()
        self.currency = "Rs"

        self.setWindowTitle("Invoice / Receipt")
        self.setModal(True)
        self.setMinimumSize(450, 580)
        self.setMaximumWidth(580)
        self.resize(480, 680)

        # Apply styles
        from ui.styles import get_app_style

        self.setStyleSheet(get_app_style())

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup the receipt interface exactly matching the visual mockup"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area for receipt
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #5a6b82; border: none; }")

        # Outer canvas container with slate background
        outer_container = QWidget()
        outer_container.setStyleSheet("background: #5a6b82;")
        outer_layout = QVBoxLayout(outer_container)
        outer_layout.setContentsMargins(28, 24, 28, 24)

        # White receipt paper card
        receipt_container = QFrame()
        receipt_container.setStyleSheet("""
            QFrame#receiptCard {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #cbd5e1;
            }
        """)
        receipt_container.setObjectName("receiptCard")
        receipt_layout = QVBoxLayout(receipt_container)
        receipt_layout.setContentsMargins(28, 28, 28, 28)
        receipt_layout.setSpacing(8)

        # ===== 1. HEADER =====
        self.shop_name_label = QLabel("MY SHOP")
        self.shop_name_label.setAlignment(Qt.AlignCenter)
        self.shop_name_label.setStyleSheet("""
            font-size: 22px;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: 0.5px;
            padding-bottom: 2px;
            background: transparent;
        """)
        receipt_layout.addWidget(self.shop_name_label)

        self.shop_address_label = QLabel("123 Main Street, City")
        self.shop_address_label.setAlignment(Qt.AlignCenter)
        self.shop_address_label.setStyleSheet("""
            font-size: 12px;
            color: #475569;
            background: transparent;
        """)
        receipt_layout.addWidget(self.shop_address_label)

        self.shop_phone_label = QLabel("Phone: +92-300-0000000")
        self.shop_phone_label.setAlignment(Qt.AlignCenter)
        self.shop_phone_label.setStyleSheet("""
            font-size: 12px;
            color: #475569;
            background: transparent;
        """)
        receipt_layout.addWidget(self.shop_phone_label)

        # Dashed Separator below header
        header_sep = QFrame()
        header_sep.setFrameShape(QFrame.HLine)
        header_sep.setFixedHeight(1)
        header_sep.setStyleSheet("border: none; border-top: 1px dashed #cbd5e1; background: transparent; margin-top: 6px; margin-bottom: 6px;")
        receipt_layout.addWidget(header_sep)

        # ===== 2. INVOICE METADATA =====
        meta_grid = QGridLayout()
        meta_grid.setContentsMargins(0, 2, 0, 4)
        meta_grid.setHorizontalSpacing(16)
        meta_grid.setVerticalSpacing(6)

        # Row 0 Left: Invoice #
        inv_box = QHBoxLayout()
        inv_box.setSpacing(4)
        inv_title = QLabel("Invoice #:")
        inv_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a; background: transparent;")
        self.invoice_number_label = QLabel("INV-000001")
        self.invoice_number_label.setStyleSheet("font-size: 13px; font-weight: 400; color: #0f172a; background: transparent;")
        inv_box.addWidget(inv_title)
        inv_box.addWidget(self.invoice_number_label)
        inv_box.addStretch()
        meta_grid.addLayout(inv_box, 0, 0)

        # Row 0 Right: Date
        date_box = QHBoxLayout()
        date_box.setSpacing(4)
        date_title = QLabel("Date:")
        date_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a; background: transparent;")
        self.date_label = QLabel("")
        self.date_label.setStyleSheet("font-size: 13px; font-weight: 400; color: #0f172a; background: transparent;")
        date_box.addStretch()
        date_box.addWidget(date_title)
        date_box.addWidget(self.date_label)
        meta_grid.addLayout(date_box, 0, 1)

        # Row 1 Left: Customer
        cust_box = QHBoxLayout()
        cust_box.setSpacing(4)
        cust_title = QLabel("Customer:")
        cust_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a; background: transparent;")
        self.customer_name_label = QLabel("Walk-in Customer")
        self.customer_name_label.setStyleSheet("font-size: 13px; font-weight: 400; color: #0f172a; background: transparent;")
        cust_box.addWidget(cust_title)
        cust_box.addWidget(self.customer_name_label)
        cust_box.addStretch()
        meta_grid.addLayout(cust_box, 1, 0)

        # Row 1 Right: Time
        time_box = QHBoxLayout()
        time_box.setSpacing(4)
        time_title = QLabel("Time:")
        time_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a; background: transparent;")
        self.time_label = QLabel("")
        self.time_label.setStyleSheet("font-size: 13px; font-weight: 400; color: #0f172a; background: transparent;")
        time_box.addStretch()
        time_box.addWidget(time_title)
        time_box.addWidget(self.time_label)
        meta_grid.addLayout(time_box, 1, 1)

        # Combined date_time_label for export compatibility
        self.date_time_label = QLabel("")

        receipt_layout.addLayout(meta_grid)

        # Dashed Separator below metadata
        meta_sep = QFrame()
        meta_sep.setFrameShape(QFrame.HLine)
        meta_sep.setFixedHeight(1)
        meta_sep.setStyleSheet("border: none; border-top: 1px dashed #cbd5e1; background: transparent; margin-top: 6px; margin-bottom: 6px;")
        receipt_layout.addWidget(meta_sep)

        # ===== 3. ITEMS SECTION =====
        items_section = QVBoxLayout()
        items_section.setSpacing(0)
        items_section.setContentsMargins(0, 0, 0, 4)

        # Column Header Row
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 2, 0, 4)
        header_layout.setSpacing(8)

        item_h = QLabel("ITEM DESCRIPTION")
        item_h.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px; background: transparent;")
        qty_h = QLabel("QTY")
        qty_h.setAlignment(Qt.AlignCenter)
        qty_h.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px; background: transparent;")
        price_h = QLabel("PRICE")
        price_h.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        price_h.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px; background: transparent;")
        total_h = QLabel("TOTAL")
        total_h.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_h.setStyleSheet("font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px; background: transparent;")

        header_layout.addWidget(item_h, stretch=5)
        header_layout.addWidget(qty_h, stretch=1)
        header_layout.addWidget(price_h, stretch=2)
        header_layout.addWidget(total_h, stretch=2)
        items_section.addWidget(header_widget)

        # Continuous separator under table headers
        item_hdr_sep = QFrame()
        item_hdr_sep.setFrameShape(QFrame.HLine)
        item_hdr_sep.setFixedHeight(1)
        item_hdr_sep.setStyleSheet("border: none; border-top: 1px solid #cbd5e1; background: transparent; margin-bottom: 6px;")
        items_section.addWidget(item_hdr_sep)

        # Items List Layout
        self.items_list_layout = QVBoxLayout()
        self.items_list_layout.setSpacing(6)
        self.items_list_layout.setContentsMargins(0, 0, 0, 4)
        items_section.addLayout(self.items_list_layout)

        receipt_layout.addLayout(items_section)

        # ===== 4 & 5. TOTALS & PAYMENT SECTION =====
        totals_container = QWidget()
        totals_container.setStyleSheet("background: transparent;")
        totals_layout = QVBoxLayout(totals_container)
        totals_layout.setContentsMargins(0, 8, 0, 4)
        totals_layout.setSpacing(5)

        # Subtotal
        subtotal_layout = QHBoxLayout()
        subtotal_lbl = QLabel("Subtotal:")
        subtotal_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a; background: transparent;")
        subtotal_layout.addStretch()
        subtotal_layout.addWidget(subtotal_lbl)
        self.subtotal_label = QLabel(f"{self.currency} 0.00")
        self.subtotal_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #0f172a; background: transparent;")
        subtotal_layout.addWidget(self.subtotal_label)
        totals_layout.addLayout(subtotal_layout)

        # Discount (hidden if 0)
        self.discount_container = QWidget()
        self.discount_container.setStyleSheet("background: transparent;")
        discount_layout = QHBoxLayout(self.discount_container)
        discount_layout.setContentsMargins(0, 0, 0, 0)
        discount_lbl = QLabel("Discount:")
        discount_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a; background: transparent;")
        discount_layout.addStretch()
        discount_layout.addWidget(discount_lbl)
        self.discount_label = QLabel(f"-{self.currency} 0.00")
        self.discount_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #0f172a; background: transparent;")
        discount_layout.addWidget(self.discount_label)
        totals_layout.addWidget(self.discount_container)

        # Thin solid separator above total
        total_sep_top = QFrame()
        total_sep_top.setFrameShape(QFrame.HLine)
        total_sep_top.setFixedHeight(1)
        total_sep_top.setStyleSheet("border: none; border-top: 1.5px solid #0f172a; background: transparent; margin: 4px 0;")
        totals_layout.addWidget(total_sep_top)

        # TOTAL (Bold 18px dark text)
        total_layout = QHBoxLayout()
        total_lbl = QLabel("TOTAL:")
        total_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #0f172a; letter-spacing: 0.5px; background: transparent;")
        total_layout.addStretch()
        total_layout.addWidget(total_lbl)
        self.total_label = QLabel(f"{self.currency} 0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #0f172a; background: transparent;")
        total_layout.addWidget(self.total_label)
        totals_layout.addLayout(total_layout)

        # Thin solid separator below total
        total_sep_bot = QFrame()
        total_sep_bot.setFrameShape(QFrame.HLine)
        total_sep_bot.setFixedHeight(1)
        total_sep_bot.setStyleSheet("border: none; border-top: 1.5px solid #0f172a; background: transparent; margin: 4px 0;")
        totals_layout.addWidget(total_sep_bot)

        # Cash Received
        cash_layout = QHBoxLayout()
        cash_lbl = QLabel("Cash Received:")
        cash_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a; background: transparent;")
        cash_layout.addStretch()
        cash_layout.addWidget(cash_lbl)
        self.cash_label = QLabel(f"{self.currency} 0.00")
        self.cash_label.setStyleSheet("font-size: 13px; font-weight: 400; color: #0f172a; background: transparent;")
        cash_layout.addWidget(self.cash_label)
        totals_layout.addLayout(cash_layout)

        # Change Returned
        change_layout = QHBoxLayout()
        change_lbl = QLabel("Change Returned:")
        change_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a; background: transparent;")
        change_layout.addStretch()
        change_layout.addWidget(change_lbl)
        self.change_label = QLabel(f"{self.currency} 0.00")
        self.change_label.setStyleSheet("font-size: 13px; font-weight: 400; color: #0f172a; background: transparent;")
        change_layout.addWidget(self.change_label)
        totals_layout.addLayout(change_layout)

        receipt_layout.addWidget(totals_container)

        # ===== 6. FOOTER =====
        footer_sep = QFrame()
        footer_sep.setFrameShape(QFrame.HLine)
        footer_sep.setFixedHeight(1)
        footer_sep.setStyleSheet("border: none; border-top: 1px dashed #cbd5e1; background: transparent; margin-top: 12px; margin-bottom: 8px;")
        receipt_layout.addWidget(footer_sep)

        self.footer_label = QLabel("Thank you for shopping with us!")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: #475569;
            padding: 2px 0;
            background: transparent;
        """)
        receipt_layout.addWidget(self.footer_label)

        self.policy_label = QLabel("Items once sold can be exchanged within 7 days with receipt.")
        self.policy_label.setAlignment(Qt.AlignCenter)
        self.policy_label.setStyleSheet("""
            font-size: 11px;
            color: #64748b;
            padding-bottom: 2px;
            background: transparent;
        """)
        receipt_layout.addWidget(self.policy_label)

        receipt_layout.addStretch()

        outer_layout.addWidget(receipt_container)
        scroll.setWidget(outer_container)
        main_layout.addWidget(scroll)

        # ===== 7. BOTTOM ACTION BAR (DOCKED WHITE BAR) =====
        action_bar = QFrame()
        action_bar.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-top: 1px solid #e2e8f0;
            }
            QPushButton#printBtn {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
                border-radius: 8px;
                padding: 10px 16px;
                border: none;
            }
            QPushButton#printBtn:hover {
                background-color: #1d4ed8;
            }
            QPushButton#pdfBtn {
                background-color: #ffffff;
                color: #1e293b;
                font-weight: 600;
                font-size: 13px;
                border-radius: 8px;
                padding: 10px 16px;
                border: 1px solid #cbd5e1;
            }
            QPushButton#pdfBtn:hover {
                background-color: #f8fafc;
                border-color: #94a3b8;
            }
            QPushButton#closeBtn {
                background-color: #fef2f2;
                color: #b91c1c;
                font-weight: 600;
                font-size: 13px;
                border-radius: 8px;
                padding: 10px 16px;
                border: 1px solid #fecaca;
            }
            QPushButton#closeBtn:hover {
                background-color: #fee2e2;
                border-color: #f87171;
            }
        """)
        button_layout = QHBoxLayout(action_bar)
        button_layout.setContentsMargins(20, 14, 20, 16)
        button_layout.setSpacing(12)

        print_btn = QPushButton("🖨️  Print Receipt")
        print_btn.setObjectName("printBtn")
        print_btn.setMinimumHeight(44)
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.clicked.connect(self.print_receipt)
        button_layout.addWidget(print_btn)

        pdf_btn = QPushButton("📄  Download PDF")
        pdf_btn.setObjectName("pdfBtn")
        pdf_btn.setMinimumHeight(44)
        pdf_btn.setCursor(Qt.PointingHandCursor)
        pdf_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(pdf_btn)

        close_btn = QPushButton("✕  Close")
        close_btn.setObjectName("closeBtn")
        close_btn.setMinimumHeight(44)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        main_layout.addWidget(action_bar)

        self.setLayout(main_layout)

        # Populate receipt data
        self.populate_receipt()

    def load_settings(self):
        """Load shop settings from database"""
        session = self.db.get_session()
        try:
            settings = {}
            rows = session.query(Setting).all()
            for row in rows:
                settings[row.key] = row.value

            self.shop_name_label.setText(settings.get("shop_name", "MY SHOP").upper())
            self.shop_address_label.setText(
                settings.get("shop_address", "123 Main Street, City")
            )
            self.shop_phone_label.setText(
                f"Phone: {settings.get('phone_number', '+92-300-0000000')}"
            )

            footer = settings.get("receipt_footer", "Thank you for shopping with us!")
            self.footer_label.setText(footer)

            self.currency = settings.get("currency_symbol", "Rs")

        except Exception as e:
            print(f"Error loading settings: {e}")
            self.currency = "Rs"
        finally:
            session.close()

    def populate_receipt(self):
        """Populate receipt with sale data"""
        data = self.sale_data

        self.invoice_number_label.setText(data.get("invoice_number", "INV-000001"))

        if data.get("sale_date"):
            sale_date = data["sale_date"]
            if isinstance(sale_date, str):
                try:
                    sale_date = datetime.fromisoformat(sale_date)
                except Exception:
                    pass
            if isinstance(sale_date, datetime):
                if sale_date.tzinfo is None:
                    local_time = sale_date.replace(tzinfo=pytz.UTC)
                else:
                    local_time = sale_date
                pakistan_tz = pytz.timezone("Asia/Karachi")
                local_time = local_time.astimezone(pakistan_tz)
                self.date_label.setText(local_time.strftime("%b %d, %Y"))
                self.time_label.setText(local_time.strftime("%I:%M %p"))
                self.date_time_label.setText(local_time.strftime("%A, %B %d, %Y  %I:%M %p"))
            else:
                self.date_label.setText(str(sale_date))
                self.time_label.setText("")
                self.date_time_label.setText(str(sale_date))
        else:
            now = datetime.now()
            self.date_label.setText(now.strftime("%b %d, %Y"))
            self.time_label.setText(now.strftime("%I:%M %p"))
            self.date_time_label.setText(now.strftime("%A, %B %d, %Y  %I:%M %p"))

        customer_name = data.get("customer_name") or "Walk-in Customer"
        self.customer_name_label.setText(str(customer_name))

        # Clear any existing item rows
        while self.items_list_layout.count():
            child = self.items_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    nested = child.layout().takeAt(0)
                    if nested.widget():
                        nested.widget().deleteLater()

        items = data.get("items", [])
        for item in items:
            row_widget = QWidget()
            row_widget.setStyleSheet("background: transparent;")
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 3, 0, 3)
            row_layout.setSpacing(8)

            name = item.get("name", "Item")
            qty = item.get("quantity", 1)
            unit_price = item.get("price", 0.0)
            tot_price = item.get("total", item.get("total_price", unit_price * qty))

            name_lbl = QLabel(str(name))
            name_lbl.setWordWrap(True)
            name_lbl.setStyleSheet("font-size: 13px; font-weight: 500; color: #0f172a; background: transparent;")

            qty_lbl = QLabel(str(qty))
            qty_lbl.setAlignment(Qt.AlignCenter)
            qty_lbl.setStyleSheet("font-size: 13px; color: #475569; background: transparent;")

            price_lbl = QLabel(f"{self.currency} {unit_price:,.2f}")
            price_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            price_lbl.setStyleSheet("font-size: 13px; color: #475569; background: transparent;")

            total_lbl = QLabel(f"{self.currency} {tot_price:,.2f}")
            total_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_lbl.setStyleSheet("font-size: 13px; font-weight: 500; color: #0f172a; background: transparent;")

            row_layout.addWidget(name_lbl, stretch=5)
            row_layout.addWidget(qty_lbl, stretch=1)
            row_layout.addWidget(price_lbl, stretch=2)
            row_layout.addWidget(total_lbl, stretch=2)

            self.items_list_layout.addWidget(row_widget)

        subtotal = data.get("subtotal", 0.0)
        discount = data.get("discount_amount", 0.0)
        net_total = data.get("net_total", 0.0)
        cash = data.get("cash_received", 0.0)
        change = data.get("change_returned", 0.0)

        self.subtotal_label.setText(f"{self.currency} {subtotal:,.2f}")

        if discount > 0:
            self.discount_label.setText(f"-{self.currency} {discount:,.2f}")
            self.discount_container.setVisible(True)
        else:
            self.discount_container.setVisible(False)

        self.total_label.setText(f"{self.currency} {net_total:,.2f}")
        self.cash_label.setText(f"{self.currency} {cash:,.2f}")
        self.change_label.setText(f"{self.currency} {change:,.2f}")

    def print_receipt(self):
        """Print receipt using Windows printer with professional HTML layout"""
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog
            from PySide6.QtGui import QTextDocument

            # Build rich HTML receipt
            receipt_html = self._build_receipt_html()

            # Create document with HTML styling
            doc = QTextDocument()
            doc.setHtml(receipt_html)

            # Show print dialog
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)

            if dialog.exec() == QPrintDialog.Accepted:
                doc.print_(printer)
                QMessageBox.information(self, "Success", "✅ Receipt sent to printer!")

        except ImportError:
            QMessageBox.warning(
                self,
                "Print Error",
                "Qt Print Support not available.\n\nPlease use the 'Download PDF' option.",
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Print Error",
                f"Could not print: {str(e)}\n\nPlease use the 'Download PDF' option.",
            )

    def _build_receipt_html(self):
        """Build professional styled HTML receipt for printer and previews"""
        data = self.sale_data

        # Get shop details
        session = self.db.get_session()
        try:
            settings = {}
            rows = session.query(Setting).all()
            for row in rows:
                settings[row.key] = row.value

            shop_name = settings.get("shop_name", "My Shop")
            shop_address = settings.get("shop_address", "123 Main Street")
            shop_phone = settings.get("phone_number", "+92-300-0000000")
            footer = settings.get("receipt_footer", "Thank you for shopping with us!")
        except Exception:
            shop_name = "My Shop"
            shop_address = "123 Main Street"
            shop_phone = "+92-300-0000000"
            footer = "Thank you for shopping with us!"
        finally:
            session.close()

        invoice_num = data.get("invoice_number", "INV-000001")
        date_str = self.date_time_label.text() or datetime.now().strftime("%d-%b-%Y %I:%M %p")
        customer_name = data.get("customer_name", "Walk-in Customer") or "Walk-in Customer"

        # Build items rows
        items_html = ""
        for item in data.get("items", []):
            name = item.get("name", "Item")
            qty = item.get("quantity", 1)
            unit_price = item.get("price", 0.0)
            total_price = item.get("total_price", unit_price * qty)

            items_html += f"""
            <tr>
                <td style="padding: 6px 4px; font-weight: 600; color: #0f172a; text-align: left;">{name}</td>
                <td style="padding: 6px 4px; text-align: center; color: #475569;">{qty}</td>
                <td style="padding: 6px 4px; text-align: right; color: #475569;">{self.currency} {unit_price:,.2f}</td>
                <td style="padding: 6px 4px; text-align: right; font-weight: 600; color: #0f172a;">{self.currency} {total_price:,.2f}</td>
            </tr>
            """

        subtotal = data.get("subtotal", 0.0)
        discount = data.get("discount_amount", 0.0)
        total = data.get("net_total", 0.0)
        cash = data.get("cash_received", 0.0)
        change = data.get("change_returned", 0.0)

        discount_row = ""
        if discount > 0:
            discount_row = f"""
            <tr>
                <td colspan="3" style="padding: 4px 4px; text-align: right; color: #ef4444; font-size: 13px;">Discount:</td>
                <td style="padding: 4px 4px; text-align: right; color: #ef4444; font-weight: 600; font-size: 13px;">-{self.currency} {discount:,.2f}</td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 15px;
                color: #0f172a;
                background-color: #ffffff;
                font-size: 13px;
                line-height: 1.4;
            }}
            .receipt-box {{
                max-width: 380px;
                margin: 0 auto;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px dashed #cbd5e1;
                padding-bottom: 12px;
                margin-bottom: 12px;
            }}
            .shop-title {{
                font-size: 20px;
                font-weight: 800;
                letter-spacing: 0.5px;
                margin-bottom: 3px;
                text-transform: uppercase;
            }}
            .shop-sub {{
                font-size: 12px;
                color: #64748b;
                margin-bottom: 2px;
            }}
            .meta-table {{
                width: 100%;
                font-size: 12px;
                margin-bottom: 12px;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 8px;
            }}
            .meta-table td {{
                padding: 2px 0;
            }}
            .items-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
                margin-bottom: 12px;
            }}
            .items-table th {{
                border-bottom: 1.5px solid #0f172a;
                border-top: 1.5px solid #0f172a;
                padding: 6px 4px;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .items-table td {{
                border-bottom: 1px solid #f1f5f9;
            }}
            .summary-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 6px;
                border-top: 1.5px solid #0f172a;
                padding-top: 8px;
            }}
            .total-row td {{
                border-top: 1.5px solid #0f172a;
                border-bottom: 1.5px solid #0f172a;
                padding: 8px 4px;
                font-size: 16px;
                font-weight: 800;
            }}
            .footer {{
                text-align: center;
                margin-top: 16px;
                padding-top: 12px;
                border-top: 2px dashed #cbd5e1;
                font-size: 11px;
                color: #64748b;
            }}
        </style>
        </head>
        <body>
            <div class="receipt-box">
                <div class="header">
                    <div class="shop-title">{shop_name}</div>
                    <div class="shop-sub">{shop_address}</div>
                    <div class="shop-sub">Tel: {shop_phone}</div>
                </div>
                
                <table class="meta-table">
                    <tr>
                        <td style="color: #64748b;">Invoice #: <strong>{invoice_num}</strong></td>
                        <td style="text-align: right; color: #64748b;">Customer: <strong>{customer_name}</strong></td>
                    </tr>
                    <tr>
                        <td colspan="2" style="color: #64748b;">Date: {date_str}</td>
                    </tr>
                </table>

                <table class="items-table">
                    <thead>
                        <tr>
                            <th style="text-align: left;">Item</th>
                            <th style="text-align: center;">Qty</th>
                            <th style="text-align: right;">Rate</th>
                            <th style="text-align: right;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>

                <table class="summary-table">
                    <tr>
                        <td colspan="3" style="padding: 4px 4px; text-align: right; color: #64748b; font-size: 13px;">Subtotal:</td>
                        <td style="padding: 4px 4px; text-align: right; font-weight: 600; font-size: 13px;">{self.currency} {subtotal:,.2f}</td>
                    </tr>
                    {discount_row}
                    <tr class="total-row">
                        <td colspan="3" style="text-align: right;">NET PAYABLE:</td>
                        <td style="text-align: right; color: #2563eb;">{self.currency} {total:,.2f}</td>
                    </tr>
                    <tr>
                        <td colspan="3" style="padding: 4px 4px; text-align: right; color: #64748b; font-size: 12px;">Cash Received:</td>
                        <td style="padding: 4px 4px; text-align: right; font-weight: 600; font-size: 12px;">{self.currency} {cash:,.2f}</td>
                    </tr>
                    <tr>
                        <td colspan="3" style="padding: 4px 4px; text-align: right; color: #64748b; font-size: 12px;">Change Returned:</td>
                        <td style="padding: 4px 4px; text-align: right; font-weight: 600; color: #16a34a; font-size: 12px;">{self.currency} {change:,.2f}</td>
                    </tr>
                </table>

                <div class="footer">
                    <p style="margin: 3px 0; font-weight: 600; color: #0f172a;">{footer}</p>
                    <p style="margin: 2px 0;">Items once sold can be exchanged within 7 days with receipt.</p>
                    <p style="margin: 4px 0 0 0; letter-spacing: 2px; font-weight: 700;">* * * * *</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def export_pdf(self):
        """Export professional receipt to PDF with multi-page flowable table"""
        try:
            from reportlab.lib.pagesizes import A5
            from reportlab.lib import colors
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                SimpleDocTemplate,
                Table,
                TableStyle,
                Paragraph,
                Spacer,
                HRFlowable,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

            invoice_no = self.sale_data.get("invoice_number", "invoice")
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Receipt PDF",
                f"Receipt_{invoice_no}.pdf",
                "PDF Files (*.pdf)",
            )

            if not file_path:
                return

            # Get shop details
            session = self.db.get_session()
            try:
                settings = {}
                rows = session.query(Setting).all()
                for row in rows:
                    settings[row.key] = row.value

                shop_name = settings.get("shop_name", "My Shop")
                shop_address = settings.get("shop_address", "123 Main Street")
                shop_phone = settings.get("phone_number", "+92-300-0000000")
                footer = settings.get(
                    "receipt_footer", "Thank you for shopping with us!"
                )
            except Exception:
                shop_name = "My Shop"
                shop_address = "123 Main Street"
                shop_phone = "+92-300-0000000"
                footer = "Thank you for shopping with us!"
            finally:
                session.close()

            # Page Setup: A5 standard format (148mm x 210mm)
            # Printable width = 148mm - 2*10mm = 128mm
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A5,
                topMargin=10 * mm,
                bottomMargin=10 * mm,
                leftMargin=10 * mm,
                rightMargin=10 * mm,
            )

            styles = getSampleStyleSheet()

            store_title_style = ParagraphStyle(
                "StoreTitle",
                parent=styles["Normal"],
                fontSize=16,
                leading=18,
                fontName="Helvetica-Bold",
                textColor=colors.HexColor("#0f172a"),
                alignment=TA_CENTER,
            )

            store_sub_style = ParagraphStyle(
                "StoreSub",
                parent=styles["Normal"],
                fontSize=9,
                leading=12,
                fontName="Helvetica",
                textColor=colors.HexColor("#64748b"),
                alignment=TA_CENTER,
            )

            meta_style = ParagraphStyle(
                "MetaText",
                parent=styles["Normal"],
                fontSize=9,
                leading=12,
                fontName="Helvetica",
                textColor=colors.HexColor("#334155"),
            )

            meta_bold_style = ParagraphStyle(
                "MetaBold",
                parent=styles["Normal"],
                fontSize=9,
                leading=12,
                fontName="Helvetica-Bold",
                textColor=colors.HexColor("#0f172a"),
            )

            item_title_style = ParagraphStyle(
                "ItemTitle",
                parent=styles["Normal"],
                fontSize=9,
                leading=11,
                fontName="Helvetica-Bold",
                textColor=colors.HexColor("#0f172a"),
            )

            cell_style = ParagraphStyle(
                "CellText",
                parent=styles["Normal"],
                fontSize=9,
                leading=11,
                fontName="Helvetica",
                textColor=colors.HexColor("#334155"),
            )

            cell_center_style = ParagraphStyle(
                "CellCenter",
                parent=styles["Normal"],
                fontSize=9,
                leading=11,
                fontName="Helvetica",
                textColor=colors.HexColor("#334155"),
                alignment=TA_CENTER,
            )

            cell_right_style = ParagraphStyle(
                "CellRight",
                parent=styles["Normal"],
                fontSize=9,
                leading=11,
                fontName="Helvetica-Bold",
                textColor=colors.HexColor("#0f172a"),
                alignment=TA_RIGHT,
            )

            footer_style = ParagraphStyle(
                "FooterText",
                parent=styles["Normal"],
                fontSize=8,
                leading=11,
                fontName="Helvetica",
                textColor=colors.HexColor("#64748b"),
                alignment=TA_CENTER,
            )

            elements = []

            # 1. Store Header
            elements.append(Paragraph(shop_name.upper(), store_title_style))
            elements.append(Spacer(1, 1.5 * mm))
            elements.append(Paragraph(shop_address, store_sub_style))
            elements.append(Paragraph(f"Tel: {shop_phone}", store_sub_style))
            elements.append(Spacer(1, 3 * mm))
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=6))

            # 2. Metadata Grid (Invoice, Date, Customer)
            customer_name = self.sale_data.get("customer_name", "Walk-in Customer") or "Walk-in Customer"
            date_str = self.date_time_label.text() or datetime.now().strftime("%d-%b-%Y %I:%M %p")

            meta_data = [
                [
                    Paragraph(f"<b>Invoice #:</b> {invoice_no}", meta_style),
                    Paragraph(f"<b>Customer:</b> {customer_name}", meta_style),
                ],
                [
                    Paragraph(f"<b>Date:</b> {date_str}", meta_style),
                    Paragraph("<b>Cashier:</b> Active Session", meta_style),
                ],
            ]
            meta_table = Table(meta_data, colWidths=[64 * mm, 64 * mm])
            meta_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]))
            elements.append(meta_table)
            elements.append(Spacer(1, 3 * mm))

            # 3. Itemized Table: ColWidths = [58mm, 18mm, 24mm, 28mm] = 128mm (fits A5 exactly)
            items_table_data = [
                [
                    Paragraph("<b>ITEM DESCRIPTION</b>", item_title_style),
                    Paragraph("<b>QTY</b>", cell_center_style),
                    Paragraph("<b>PRICE</b>", cell_right_style),
                    Paragraph("<b>TOTAL</b>", cell_right_style),
                ]
            ]

            for item in self.sale_data.get("items", []):
                name = item.get("name", "Product")
                qty = str(item.get("quantity", 1))
                unit_price = f"{self.currency} {item.get('price', 0.0):,.2f}"
                tot_price = f"{self.currency} {item.get('total_price', item.get('price', 0.0) * item.get('quantity', 1)):,.2f}"

                items_table_data.append([
                    Paragraph(name, cell_style),
                    Paragraph(qty, cell_center_style),
                    Paragraph(unit_price, cell_right_style),
                    Paragraph(tot_price, cell_right_style),
                ])

            item_col_widths = [58 * mm, 16 * mm, 26 * mm, 28 * mm]
            item_table = Table(items_table_data, colWidths=item_col_widths, repeatRows=1)
            item_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("LINEABOVE", (0, 0), (-1, 0), 1.2, colors.HexColor("#0f172a")),
                ("LINEBELOW", (0, 0), (-1, 0), 1.2, colors.HexColor("#0f172a")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
                ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
            ]))
            elements.append(item_table)
            elements.append(Spacer(1, 4 * mm))

            # 4. Summary & Totals Block
            subtotal_val = self.sale_data.get("subtotal", 0.0)
            discount_val = self.sale_data.get("discount_amount", 0.0)
            net_val = self.sale_data.get("net_total", 0.0)
            cash_val = self.sale_data.get("cash_received", 0.0)
            change_val = self.sale_data.get("change_returned", 0.0)

            summary_rows = [
                ["", "", "Subtotal:", f"{self.currency} {subtotal_val:,.2f}"],
            ]
            if discount_val > 0:
                summary_rows.append(["", "", "Discount:", f"-{self.currency} {discount_val:,.2f}"])
            summary_rows.append(["", "", "NET TOTAL:", f"{self.currency} {net_val:,.2f}"])
            summary_rows.append(["", "", "Cash Paid:", f"{self.currency} {cash_val:,.2f}"])
            summary_rows.append(["", "", "Change Due:", f"{self.currency} {change_val:,.2f}"])

            sum_table = Table(summary_rows, colWidths=[40 * mm, 30 * mm, 30 * mm, 28 * mm])
            sum_style_commands = [
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                ("FONTNAME", (2, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (2, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LINEABOVE", (2, 0), (3, 0), 1, colors.HexColor("#cbd5e1")),
            ]

            # Find row index of NET TOTAL
            net_row_idx = 1 if discount_val == 0 else 2
            sum_style_commands.extend([
                ("FONTNAME", (2, net_row_idx), (3, net_row_idx), "Helvetica-Bold"),
                ("FONTSIZE", (2, net_row_idx), (3, net_row_idx), 11),
                ("TEXTCOLOR", (3, net_row_idx), (3, net_row_idx), colors.HexColor("#2563eb")),
                ("LINEABOVE", (2, net_row_idx), (3, net_row_idx), 1.2, colors.HexColor("#0f172a")),
                ("LINEBELOW", (2, net_row_idx), (3, net_row_idx), 1.2, colors.HexColor("#0f172a")),
            ])

            sum_table.setStyle(TableStyle(sum_style_commands))
            elements.append(sum_table)
            elements.append(Spacer(1, 6 * mm))

            # 5. Footer and Return Policy
            elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
            elements.append(Paragraph(f"<b>{footer}</b>", footer_style))
            elements.append(Spacer(1, 1 * mm))
            elements.append(Paragraph("Goods once sold can be exchanged within 7 days with this original receipt.", footer_style))
            elements.append(Spacer(1, 1 * mm))
            elements.append(Paragraph("<b>* * * Thank you for your business * * *</b>", footer_style))

            # Build Document
            doc.build(elements)

            QMessageBox.information(
                self, "Success", f"Professional receipt PDF saved successfully!\n\n{file_path}"
            )

        except ImportError:
            QMessageBox.warning(
                self,
                "Error",
                "ReportLab library is not installed.\nPlease install: pip install reportlab",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not export PDF: {str(e)}")
