"""
Reports Window
Sales reports, profit analysis, and exports
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
    QLabel,
    QMessageBox,
    QGroupBox,
    QDateEdit,
    QTabWidget,
    QFrame,
    QHeaderView,
    QComboBox,
    QFileDialog,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from datetime import datetime, timedelta
try:
    import pytz
except ImportError:
    pytz = None
from sqlalchemy import func, extract
from sqlalchemy.orm import subqueryload

# Add parent directory to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from database import DatabaseManager, Sale, SaleItem, Product, Setting
from modules.sales.receipt_window import ReceiptWindow


class ReportsWindow(QWidget):
    """Main Reports Window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()

        self.setWindowTitle("Reports")
        self.setGeometry(100, 100, 1200, 750)

        # Apply styles
        from ui.styles import get_app_style

        self.setStyleSheet(get_app_style())

        self.setup_ui()
        self.load_settings()

    def _localize_time(self, dt):
        """Convert UTC datetime to local time (Pakistan Standard Time) if tzinfo present"""
        if dt is None:
            return dt
        if dt.tzinfo is not None and pytz:
            pakistan_tz = pytz.timezone("Asia/Karachi")
            return dt.astimezone(pakistan_tz)
        return dt

    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_label = QLabel("Reports & Analytics")
        header_label.setObjectName("header")
        main_layout.addWidget(header_label)

        tabs = QTabWidget()
        daily_tab = self.create_daily_tab()
        tabs.addTab(daily_tab, "Daily Report")
        monthly_tab = self.create_monthly_tab()
        tabs.addTab(monthly_tab, "Monthly Report")
        main_layout.addWidget(tabs)

        self.setLayout(main_layout)

    def create_daily_tab(self):
        """Create daily report tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Date Selector
        date_group = QGroupBox("Select Date")
        date_layout = QHBoxLayout()

        date_layout.addWidget(QLabel("Date:"))
        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setMinimumHeight(35)
        self.date_picker.dateChanged.connect(self.load_daily_report)
        date_layout.addWidget(self.date_picker)

        date_layout.addStretch()

        load_btn = QPushButton("Load Report")
        load_btn.setObjectName("primary")
        load_btn.setMinimumHeight(35)
        load_btn.setMinimumWidth(120)
        load_btn.clicked.connect(self.load_daily_report)
        date_layout.addWidget(load_btn)

        date_group.setLayout(date_layout)
        layout.addWidget(date_group)

        # Summary Cards
        summary_group = QGroupBox("Summary")
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)

        sales_card = QFrame()
        sales_card.setStyleSheet("""
            QFrame {
                background-color: #eff6ff;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #bfdbfe;
            }
        """)
        sales_card_layout = QVBoxLayout()
        sales_card_layout.addWidget(QLabel("Total Sales"))
        self.daily_total_sales = QLabel("Rs 0.00")
        self.daily_total_sales.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #2563eb;"
        )
        sales_card_layout.addWidget(self.daily_total_sales)
        sales_card.setLayout(sales_card_layout)
        summary_layout.addWidget(sales_card)

        profit_card = QFrame()
        profit_card.setStyleSheet("""
            QFrame {
                background-color: #f0fdf4;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #bbf7d0;
            }
        """)
        profit_card_layout = QVBoxLayout()
        profit_card_layout.addWidget(QLabel("Total Profit"))
        self.daily_total_profit = QLabel("Rs 0.00")
        self.daily_total_profit.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #16a34a;"
        )
        profit_card_layout.addWidget(self.daily_total_profit)
        profit_card.setLayout(profit_card_layout)
        summary_layout.addWidget(profit_card)

        bills_card = QFrame()
        bills_card.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #fde68a;
            }
        """)
        bills_card_layout = QVBoxLayout()
        bills_card_layout.addWidget(QLabel("Total Bills"))
        self.daily_total_bills = QLabel("0")
        self.daily_total_bills.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #d97706;"
        )
        bills_card_layout.addWidget(self.daily_total_bills)
        bills_card.setLayout(bills_card_layout)
        summary_layout.addWidget(bills_card)

        items_card = QFrame()
        items_card.setStyleSheet("""
            QFrame {
                background-color: #fef2f2;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #fecaca;
            }
        """)
        items_card_layout = QVBoxLayout()
        items_card_layout.addWidget(QLabel("Items Sold"))
        self.daily_items_sold = QLabel("0")
        self.daily_items_sold.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #dc2626;"
        )
        items_card_layout.addWidget(self.daily_items_sold)
        items_card.setLayout(items_card_layout)
        summary_layout.addWidget(items_card)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Detailed Table
        table_group = QGroupBox("Sales Details")
        table_layout = QVBoxLayout()

        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(7)
        self.daily_table.setHorizontalHeaderLabels(
            ["Invoice", "Time", "Items", "Subtotal", "Discount", "Total", "Profit"]
        )
        self.daily_table.setAlternatingRowColors(True)
        self.daily_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.daily_table.verticalHeader().hide()
        self.daily_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.daily_table.verticalHeader().setDefaultSectionSize(50)

        self.daily_table.setColumnWidth(0, 130)  # Invoice
        self.daily_table.setColumnWidth(2, 90)   # Items
        self.daily_table.setColumnWidth(3, 120)  # Subtotal
        self.daily_table.setColumnWidth(4, 120)  # Discount
        self.daily_table.setColumnWidth(5, 130)  # Total
        self.daily_table.setColumnWidth(6, 130)  # Profit

        header = self.daily_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Time / Details stretch
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        header.setSectionResizeMode(5, QHeaderView.Interactive)
        header.setSectionResizeMode(6, QHeaderView.Interactive)

        self.daily_table.doubleClicked.connect(self.view_sale_details)

        self.daily_table.setStyleSheet("""
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

        table_layout.addWidget(self.daily_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Export Buttons
        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)
        export_layout.addStretch()

        print_btn = QPushButton("🖨️ Print Report")
        print_btn.setObjectName("secondary")
        print_btn.setMinimumHeight(45)
        print_btn.setMinimumWidth(150)
        print_btn.clicked.connect(self.print_daily_report)
        export_layout.addWidget(print_btn)

        pdf_btn = QPushButton("📄 Export to PDF")
        pdf_btn.setObjectName("primary")
        pdf_btn.setMinimumHeight(45)
        pdf_btn.setMinimumWidth(180)
        pdf_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                padding: 10px 25px;
                border-radius: 8px;
            }
        """)
        pdf_btn.clicked.connect(self.export_daily_pdf)
        export_layout.addWidget(pdf_btn)

        layout.addLayout(export_layout)

        tab.setLayout(layout)
        return tab

    def create_monthly_tab(self):
        """Create monthly report tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Month Selector
        month_group = QGroupBox("Select Month")
        month_layout = QHBoxLayout()

        month_layout.addWidget(QLabel("Year:"))
        self.year_combo = QComboBox()
        self.year_combo.setMinimumHeight(35)
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.currentTextChanged.connect(self.load_monthly_report)
        month_layout.addWidget(self.year_combo)

        month_layout.addWidget(QLabel("Month:"))
        self.month_combo = QComboBox()
        self.month_combo.setMinimumHeight(35)
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        self.month_combo.addItems(months)
        self.month_combo.setCurrentIndex(datetime.now().month - 1)
        self.month_combo.currentTextChanged.connect(self.load_monthly_report)
        month_layout.addWidget(self.month_combo)

        month_layout.addStretch()

        load_btn = QPushButton("Load Report")
        load_btn.setObjectName("primary")
        load_btn.setMinimumHeight(35)
        load_btn.setMinimumWidth(120)
        load_btn.clicked.connect(self.load_monthly_report)
        month_layout.addWidget(load_btn)

        month_group.setLayout(month_layout)
        layout.addWidget(month_group)

        # Summary Cards
        summary_group = QGroupBox("Monthly Summary")
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)

        sales_card = QFrame()
        sales_card.setStyleSheet("""
            QFrame {
                background-color: #eff6ff;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #bfdbfe;
            }
        """)
        sales_card_layout = QVBoxLayout()
        sales_card_layout.addWidget(QLabel("Total Sales"))
        self.monthly_total_sales = QLabel("Rs 0.00")
        self.monthly_total_sales.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #2563eb;"
        )
        sales_card_layout.addWidget(self.monthly_total_sales)
        sales_card.setLayout(sales_card_layout)
        summary_layout.addWidget(sales_card)

        profit_card = QFrame()
        profit_card.setStyleSheet("""
            QFrame {
                background-color: #f0fdf4;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #bbf7d0;
            }
        """)
        profit_card_layout = QVBoxLayout()
        profit_card_layout.addWidget(QLabel("Total Profit"))
        self.monthly_total_profit = QLabel("Rs 0.00")
        self.monthly_total_profit.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #16a34a;"
        )
        profit_card_layout.addWidget(self.monthly_total_profit)
        profit_card.setLayout(profit_card_layout)
        summary_layout.addWidget(profit_card)

        bills_card = QFrame()
        bills_card.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #fde68a;
            }
        """)
        bills_card_layout = QVBoxLayout()
        bills_card_layout.addWidget(QLabel("Total Bills"))
        self.monthly_total_bills = QLabel("0")
        self.monthly_total_bills.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #d97706;"
        )
        bills_card_layout.addWidget(self.monthly_total_bills)
        bills_card.setLayout(bills_card_layout)
        summary_layout.addWidget(bills_card)

        items_card = QFrame()
        items_card.setStyleSheet("""
            QFrame {
                background-color: #fef2f2;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #fecaca;
            }
        """)
        items_card_layout = QVBoxLayout()
        items_card_layout.addWidget(QLabel("Items Sold"))
        self.monthly_items_sold = QLabel("0")
        self.monthly_items_sold.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #dc2626;"
        )
        items_card_layout.addWidget(self.monthly_items_sold)
        items_card.setLayout(items_card_layout)
        summary_layout.addWidget(items_card)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Table
        table_group = QGroupBox("Monthly Sales Details")
        table_layout = QVBoxLayout()

        self.monthly_table = QTableWidget()
        self.monthly_table.setColumnCount(7)
        self.monthly_table.setHorizontalHeaderLabels(
            [
                "Date",
                "Invoices",
                "Items Sold",
                "Total Sales",
                "Total Discount",
                "Net Sales",
                "Total Profit",
            ]
        )
        self.monthly_table.setAlternatingRowColors(True)
        self.monthly_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.monthly_table.verticalHeader().hide()
        self.monthly_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.monthly_table.verticalHeader().setDefaultSectionSize(50)

        self.monthly_table.setColumnWidth(1, 100)  # Invoices
        self.monthly_table.setColumnWidth(2, 100)  # Items Sold
        self.monthly_table.setColumnWidth(3, 130)  # Total Sales
        self.monthly_table.setColumnWidth(4, 130)  # Total Discount
        self.monthly_table.setColumnWidth(5, 130)  # Net Sales
        self.monthly_table.setColumnWidth(6, 130)  # Total Profit

        header = self.monthly_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Date column stretches
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        header.setSectionResizeMode(5, QHeaderView.Interactive)
        header.setSectionResizeMode(6, QHeaderView.Interactive)

        self.monthly_table.doubleClicked.connect(self.view_monthly_sale_details)

        self.monthly_table.setStyleSheet("""
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

        table_layout.addWidget(self.monthly_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Export Buttons
        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)
        export_layout.addStretch()

        print_btn = QPushButton("🖨️ Print Report")
        print_btn.setObjectName("secondary")
        print_btn.setMinimumHeight(45)
        print_btn.setMinimumWidth(150)
        print_btn.clicked.connect(self.print_monthly_report)
        export_layout.addWidget(print_btn)

        pdf_btn = QPushButton("📄 Export to PDF")
        pdf_btn.setObjectName("primary")
        pdf_btn.setMinimumHeight(45)
        pdf_btn.setMinimumWidth(180)
        pdf_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                padding: 10px 25px;
                border-radius: 8px;
            }
        """)
        pdf_btn.clicked.connect(self.export_monthly_pdf)
        export_layout.addWidget(pdf_btn)

        layout.addLayout(export_layout)

        tab.setLayout(layout)
        return tab

    def view_sale_details(self, index):
        """View sale details when a row is double-clicked in daily report"""
        row = index.row()
        if row < 0:
            return

        invoice = self.daily_table.item(row, 0).text()

        session = self.db.get_session()
        try:
            sale = session.query(Sale).filter_by(invoice_number=invoice).first()

            if not sale:
                QMessageBox.warning(self, "Not Found", f"Sale {invoice} not found.")
                return

            items = []
            for item in sale.items:
                product = session.query(Product).filter_by(id=item.product_id).first()
                items.append(
                    {
                        "name": (
                            product.name
                            if product
                            else f"Product ID: {item.product_id}"
                        ),
                        "quantity": item.quantity,
                        "price": item.unit_price,
                        "total": item.total_price,
                    }
                )

            receipt_data = {
                "invoice_number": sale.invoice_number,
                "sale_date": sale.sale_date,
                "items": items,
                "subtotal": sale.total_amount,
                "discount_amount": sale.discount_amount,
                "discount_percentage": sale.discount_percentage,
                "net_total": sale.net_amount,
                "cash_received": sale.cash_received,
                "change_returned": sale.change_returned,
            }

            receipt = ReceiptWindow(receipt_data, self)
            receipt.exec()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Could not load sale details: {str(e)}"
            )
        finally:
            session.close()

    def view_monthly_sale_details(self, index):
        """View sale details when a row is double-clicked in monthly report"""
        row = index.row()
        if row < 0:
            return

        date_str = self.monthly_table.item(row, 0).text()

        try:
            date = datetime.strptime(date_str, "%b %d, %Y")
        except Exception:
            QMessageBox.warning(self, "Error", "Could not parse date.")
            return

        session = self.db.get_session()
        try:
            start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_date = datetime(date.year, date.month, date.day, 23, 59, 59)

            sales = (
                session.query(Sale)
                .options(subqueryload(Sale.items))
                .filter(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
                .all()
            )

            if not sales:
                QMessageBox.information(
                    self, "No Sales", "No sales found for this date."
                )
                return

            msg = f"📋 Sales on {date_str}\n\n"
            msg += "-" * 30 + "\n"
            total_items = 0
            for sale in sales:
                local_time = self._localize_time(sale.sale_date)
                time_display = local_time.strftime('%I:%M %p') if local_time else '--'
                msg += f"🕐 {time_display} | {sale.invoice_number} | {self.currency} {sale.net_amount:,.2f}\n"
                total_items += len(sale.items)

            msg += "-" * 30 + "\n"
            msg += f"Total Bills: {len(sales)}\n"
            msg += f"Total Items: {total_items}\n"
            msg += f"Total Sales: {self.currency} {sum(s.net_amount for s in sales):,.2f}"

            QMessageBox.information(self, "Daily Summary", msg)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load sales: {str(e)}")
        finally:
            session.close()

    def print_daily_report(self):
        """Print daily report using Windows printer with professional executive HTML layout"""
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog
            from PySide6.QtGui import QTextDocument

            report_html = self._build_daily_report_html()

            doc = QTextDocument()
            doc.setHtml(report_html)

            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)

            if dialog.exec() == QPrintDialog.Accepted:
                doc.print_(printer)
                QMessageBox.information(self, "Success", "✅ Daily report sent to printer!")

        except ImportError:
            QMessageBox.warning(
                self,
                "Print Error",
                "Qt Print Support not available.\n\nPlease use the 'Export to PDF' option.",
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Print Error",
                f"Could not print: {str(e)}\n\nPlease use the 'Export to PDF' option.",
            )

    def _build_daily_report_html(self):
        """Build professional styled HTML daily sales report"""
        date = self.date_picker.date().toPython()

        # Get settings
        session = self.db.get_session()
        try:
            settings = {}
            rows = session.query(Setting).all()
            for row in rows:
                settings[row.key] = row.value

            shop_name = settings.get("shop_name", "My Shop")
            shop_address = settings.get("shop_address", "123 Main Street")
            shop_phone = settings.get("phone_number", "+92-300-0000000")
        except Exception:
            shop_name = "My Shop"
            shop_address = "123 Main Street"
            shop_phone = "+92-300-0000000"
        finally:
            session.close()

        # Build table rows
        rows_html = ""
        for row in range(self.daily_table.rowCount()):
            invoice = self.daily_table.item(row, 0).text() if self.daily_table.item(row, 0) else "-"
            time = self.daily_table.item(row, 1).text() if self.daily_table.item(row, 1) else "-"
            items = self.daily_table.item(row, 2).text() if self.daily_table.item(row, 2) else "0"
            subtotal = self.daily_table.item(row, 3).text() if self.daily_table.item(row, 3) else "0.00"
            discount = self.daily_table.item(row, 4).text() if self.daily_table.item(row, 4) else "0.00"
            total = self.daily_table.item(row, 5).text() if self.daily_table.item(row, 5) else "0.00"
            profit = self.daily_table.item(row, 6).text() if self.daily_table.item(row, 6) else "0.00"

            bg = "#f8fafc" if row % 2 == 1 else "#ffffff"
            rows_html += f"""
            <tr style="background-color: {bg};">
                <td style="padding: 7px 6px; font-weight: 600; text-align: left; border-bottom: 1px solid #e2e8f0;">{invoice}</td>
                <td style="padding: 7px 6px; text-align: center; color: #475569; border-bottom: 1px solid #e2e8f0;">{time}</td>
                <td style="padding: 7px 6px; text-align: center; border-bottom: 1px solid #e2e8f0;">{items}</td>
                <td style="padding: 7px 6px; text-align: right; border-bottom: 1px solid #e2e8f0;">{subtotal}</td>
                <td style="padding: 7px 6px; text-align: right; color: #ef4444; border-bottom: 1px solid #e2e8f0;">{discount}</td>
                <td style="padding: 7px 6px; text-align: right; font-weight: 700; color: #2563eb; border-bottom: 1px solid #e2e8f0;">{total}</td>
                <td style="padding: 7px 6px; text-align: right; font-weight: 600; color: #16a34a; border-bottom: 1px solid #e2e8f0;">{profit}</td>
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
                padding: 20px;
                color: #0f172a;
                background: #ffffff;
                font-size: 13px;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #0f172a;
                padding-bottom: 12px;
                margin-bottom: 16px;
            }}
            .store-name {{
                font-size: 22px;
                font-weight: 800;
                text-transform: uppercase;
                margin-bottom: 3px;
            }}
            .report-title {{
                font-size: 16px;
                font-weight: 700;
                color: #2563eb;
                margin-top: 6px;
                margin-bottom: 2px;
            }}
            .kpi-grid {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 10px;
                margin-bottom: 18px;
            }}
            .kpi-card {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
            }}
            .kpi-title {{
                font-size: 11px;
                text-transform: uppercase;
                font-weight: 700;
                color: #64748b;
                margin-bottom: 4px;
            }}
            .kpi-value {{
                font-size: 18px;
                font-weight: 800;
                color: #0f172a;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
            }}
            .data-table th {{
                background-color: #0f172a;
                color: #ffffff;
                padding: 8px 6px;
                font-size: 11px;
                text-transform: uppercase;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 24px;
                padding-top: 12px;
                border-top: 1px solid #cbd5e1;
                font-size: 11px;
                color: #94a3b8;
            }}
        </style>
        </head>
        <body>
            <div class="header">
                <div class="store-name">{shop_name}</div>
                <div style="color: #64748b; font-size: 12px;">{shop_address} · Phone: {shop_phone}</div>
                <div class="report-title">DAILY SALES REPORT</div>
                <div style="font-weight: 600; color: #475569;">{date.strftime('%A, %B %d, %Y')}</div>
            </div>

            <table class="kpi-grid">
                <tr>
                    <td class="kpi-card" style="border-top: 3px solid #2563eb;">
                        <div class="kpi-title">Total Sales</div>
                        <div class="kpi-value" style="color: #2563eb;">{self.daily_total_sales.text()}</div>
                    </td>
                    <td class="kpi-card" style="border-top: 3px solid #16a34a;">
                        <div class="kpi-title">Total Profit</div>
                        <div class="kpi-value" style="color: #16a34a;">{self.daily_total_profit.text()}</div>
                    </td>
                    <td class="kpi-card" style="border-top: 3px solid #f59e0b;">
                        <div class="kpi-title">Total Invoices</div>
                        <div class="kpi-value" style="color: #f59e0b;">{self.daily_total_bills.text()}</div>
                    </td>
                    <td class="kpi-card" style="border-top: 3px solid #6366f1;">
                        <div class="kpi-title">Items Sold</div>
                        <div class="kpi-value" style="color: #6366f1;">{self.daily_items_sold.text()}</div>
                    </td>
                </tr>
            </table>

            <table class="data-table">
                <thead>
                    <tr>
                        <th style="text-align: left;">Invoice</th>
                        <th style="text-align: center;">Time</th>
                        <th style="text-align: center;">Items</th>
                        <th style="text-align: right;">Subtotal</th>
                        <th style="text-align: right;">Discount</th>
                        <th style="text-align: right;">Total</th>
                        <th style="text-align: right;">Profit</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html if rows_html else '<tr><td colspan="7" style="text-align: center; padding: 20px; color: #64748b;">No sales transactions recorded for this date.</td></tr>'}
                </tbody>
            </table>

            <div class="footer">
                Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} · Shop Management System
            </div>
        </body>
        </html>
        """
        return html

    def print_monthly_report(self):
        """Print monthly report using Windows printer with professional executive HTML layout"""
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog
            from PySide6.QtGui import QTextDocument

            report_html = self._build_monthly_report_html()

            doc = QTextDocument()
            doc.setHtml(report_html)

            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)

            if dialog.exec() == QPrintDialog.Accepted:
                doc.print_(printer)
                QMessageBox.information(self, "Success", "✅ Monthly report sent to printer!")

        except ImportError:
            QMessageBox.warning(
                self,
                "Print Error",
                "Qt Print Support not available.\n\nPlease use the 'Export to PDF' option.",
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Print Error",
                f"Could not print: {str(e)}\n\nPlease use the 'Export to PDF' option.",
            )

    def _build_monthly_report_html(self):
        """Build professional styled HTML monthly sales report"""
        year = self.year_combo.currentText()
        month = self.month_combo.currentText()

        # Get settings
        session = self.db.get_session()
        try:
            settings = {}
            rows = session.query(Setting).all()
            for row in rows:
                settings[row.key] = row.value

            shop_name = settings.get("shop_name", "My Shop")
            shop_address = settings.get("shop_address", "123 Main Street")
            shop_phone = settings.get("phone_number", "+92-300-0000000")
        except Exception:
            shop_name = "My Shop"
            shop_address = "123 Main Street"
            shop_phone = "+92-300-0000000"
        finally:
            session.close()

        # Build table rows
        rows_html = ""
        for row in range(self.monthly_table.rowCount()):
            date = self.monthly_table.item(row, 0).text() if self.monthly_table.item(row, 0) else "-"
            invoices = self.monthly_table.item(row, 1).text() if self.monthly_table.item(row, 1) else "0"
            items = self.monthly_table.item(row, 2).text() if self.monthly_table.item(row, 2) else "0"
            total = self.monthly_table.item(row, 3).text() if self.monthly_table.item(row, 3) else "0.00"
            discount = self.monthly_table.item(row, 4).text() if self.monthly_table.item(row, 4) else "0.00"
            net = self.monthly_table.item(row, 5).text() if self.monthly_table.item(row, 5) else "0.00"
            profit = self.monthly_table.item(row, 6).text() if self.monthly_table.item(row, 6) else "0.00"

            bg = "#f8fafc" if row % 2 == 1 else "#ffffff"
            rows_html += f"""
            <tr style="background-color: {bg};">
                <td style="padding: 7px 6px; font-weight: 600; text-align: left; border-bottom: 1px solid #e2e8f0;">{date}</td>
                <td style="padding: 7px 6px; text-align: center; border-bottom: 1px solid #e2e8f0;">{invoices}</td>
                <td style="padding: 7px 6px; text-align: center; border-bottom: 1px solid #e2e8f0;">{items}</td>
                <td style="padding: 7px 6px; text-align: right; border-bottom: 1px solid #e2e8f0;">{total}</td>
                <td style="padding: 7px 6px; text-align: right; color: #ef4444; border-bottom: 1px solid #e2e8f0;">{discount}</td>
                <td style="padding: 7px 6px; text-align: right; font-weight: 700; color: #2563eb; border-bottom: 1px solid #e2e8f0;">{net}</td>
                <td style="padding: 7px 6px; text-align: right; font-weight: 600; color: #16a34a; border-bottom: 1px solid #e2e8f0;">{profit}</td>
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
                padding: 20px;
                color: #0f172a;
                background: #ffffff;
                font-size: 13px;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #0f172a;
                padding-bottom: 12px;
                margin-bottom: 16px;
            }}
            .store-name {{
                font-size: 22px;
                font-weight: 800;
                text-transform: uppercase;
                margin-bottom: 3px;
            }}
            .report-title {{
                font-size: 16px;
                font-weight: 700;
                color: #2563eb;
                margin-top: 6px;
                margin-bottom: 2px;
            }}
            .kpi-grid {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 10px;
                margin-bottom: 18px;
            }}
            .kpi-card {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
            }}
            .kpi-title {{
                font-size: 11px;
                text-transform: uppercase;
                font-weight: 700;
                color: #64748b;
                margin-bottom: 4px;
            }}
            .kpi-value {{
                font-size: 18px;
                font-weight: 800;
                color: #0f172a;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
            }}
            .data-table th {{
                background-color: #0f172a;
                color: #ffffff;
                padding: 8px 6px;
                font-size: 11px;
                text-transform: uppercase;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 24px;
                padding-top: 12px;
                border-top: 1px solid #cbd5e1;
                font-size: 11px;
                color: #94a3b8;
            }}
        </style>
        </head>
        <body>
            <div class="header">
                <div class="store-name">{shop_name}</div>
                <div style="color: #64748b; font-size: 12px;">{shop_address} · Phone: {shop_phone}</div>
                <div class="report-title">MONTHLY SALES REPORT</div>
                <div style="font-weight: 600; color: #475569;">{month} {year}</div>
            </div>

            <table class="kpi-grid">
                <tr>
                    <td class="kpi-card" style="border-top: 3px solid #2563eb;">
                        <div class="kpi-title">Monthly Sales</div>
                        <div class="kpi-value" style="color: #2563eb;">{self.monthly_total_sales.text()}</div>
                    </td>
                    <td class="kpi-card" style="border-top: 3px solid #16a34a;">
                        <div class="kpi-title">Monthly Profit</div>
                        <div class="kpi-value" style="color: #16a34a;">{self.monthly_total_profit.text()}</div>
                    </td>
                    <td class="kpi-card" style="border-top: 3px solid #f59e0b;">
                        <div class="kpi-title">Total Invoices</div>
                        <div class="kpi-value" style="color: #f59e0b;">{self.monthly_total_bills.text()}</div>
                    </td>
                    <td class="kpi-card" style="border-top: 3px solid #6366f1;">
                        <div class="kpi-title">Items Sold</div>
                        <div class="kpi-value" style="color: #6366f1;">{self.monthly_items_sold.text()}</div>
                    </td>
                </tr>
            </table>

            <table class="data-table">
                <thead>
                    <tr>
                        <th style="text-align: left;">Date</th>
                        <th style="text-align: center;">Invoices</th>
                        <th style="text-align: center;">Items Sold</th>
                        <th style="text-align: right;">Total Sales</th>
                        <th style="text-align: right;">Total Discount</th>
                        <th style="text-align: right;">Net Sales</th>
                        <th style="text-align: right;">Profit</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html if rows_html else '<tr><td colspan="7" style="text-align: center; padding: 20px; color: #64748b;">No sales transactions recorded for this month.</td></tr>'}
                </tbody>
            </table>

            <div class="footer">
                Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} · Shop Management System
            </div>
        </body>
        </html>
        """
        return html
        lines.append("=" * 60)

        return "\n".join(lines)

    def load_settings(self):
        """Load currency symbol"""
        session = self.db.get_session()
        try:
            currency = session.query(Setting).filter_by(key="currency_symbol").first()
            self.currency = currency.value if currency else "Rs"
        except Exception:
            self.currency = "Rs"
        finally:
            session.close()

        self.load_daily_report()
        self.load_monthly_report()

    def load_daily_report(self):
        """Load daily report data"""
        date = self.date_picker.date().toPython()
        start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59)

        session = self.db.get_session()
        try:
            sales = (
                session.query(Sale)
                .options(subqueryload(Sale.items))
                .filter(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
                .order_by(Sale.sale_date.desc())
                .all()
            )

            total_sales = sum(s.net_amount for s in sales)
            total_profit = sum(s.profit for s in sales)
            total_bills = len(sales)
            total_items = sum(len(s.items) for s in sales)

            self.daily_total_sales.setText(f"{self.currency}{total_sales:,.2f}")
            self.daily_total_profit.setText(f"{self.currency}{total_profit:,.2f}")
            self.daily_total_bills.setText(str(total_bills))
            self.daily_items_sold.setText(str(total_items))

            self.daily_table.setRowCount(len(sales))

            for row, sale in enumerate(sales):
                item_count = len(sale.items)
                self.daily_table.setItem(row, 0, QTableWidgetItem(sale.invoice_number))
                local_time = self._localize_time(sale.sale_date)
                time_str = local_time.strftime("%b %d, %Y %I:%M %p") if local_time else "--"
                self.daily_table.setItem(row, 1, QTableWidgetItem(time_str))
                self.daily_table.setItem(row, 2, QTableWidgetItem(str(item_count)))
                self.daily_table.setItem(
                    row, 3, QTableWidgetItem(f"{self.currency}{sale.total_amount:,.2f}")
                )
                self.daily_table.setItem(
                    row,
                    4,
                    QTableWidgetItem(f"{self.currency}{sale.discount_amount:,.2f}"),
                )
                self.daily_table.setItem(
                    row, 5, QTableWidgetItem(f"{self.currency}{sale.net_amount:,.2f}")
                )
                self.daily_table.setItem(
                    row, 6, QTableWidgetItem(f"{self.currency}{sale.profit:,.2f}")
                )

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load daily report: {str(e)}")
        finally:
            session.close()

    def load_monthly_report(self):
        """Load monthly report data"""
        year = int(self.year_combo.currentText())
        month = self.month_combo.currentIndex() + 1

        session = self.db.get_session()
        try:
            sales = (
                session.query(Sale)
                .options(subqueryload(Sale.items))
                .filter(
                    extract("year", Sale.sale_date) == year,
                    extract("month", Sale.sale_date) == month,
                )
                .order_by(Sale.sale_date)
                .all()
            )

            total_sales = sum(s.net_amount for s in sales)
            total_profit = sum(s.profit for s in sales)
            total_bills = len(sales)
            total_items = sum(len(s.items) for s in sales)

            self.monthly_total_sales.setText(f"{self.currency}{total_sales:,.2f}")
            self.monthly_total_profit.setText(f"{self.currency}{total_profit:,.2f}")
            self.monthly_total_bills.setText(str(total_bills))
            self.monthly_items_sold.setText(str(total_items))

            daily_data = {}
            for sale in sales:
                day = sale.sale_date.day
                if day not in daily_data:
                    daily_data[day] = {
                        "sales": [],
                        "items": 0,
                        "total": 0,
                        "discount": 0,
                        "net": 0,
                        "profit": 0,
                    }
                item_count = len(sale.items)
                daily_data[day]["sales"].append(sale)
                daily_data[day]["items"] += item_count
                daily_data[day]["total"] += sale.total_amount
                daily_data[day]["discount"] += sale.discount_amount
                daily_data[day]["net"] += sale.net_amount
                daily_data[day]["profit"] += sale.profit

            self.monthly_table.setRowCount(len(daily_data))

            for row, (day, data) in enumerate(sorted(daily_data.items())):
                date_obj = datetime(year, month, day)
                self.monthly_table.setItem(
                    row, 0, QTableWidgetItem(date_obj.strftime("%b %d, %Y"))
                )
                self.monthly_table.setItem(
                    row, 1, QTableWidgetItem(str(len(data["sales"])))
                )
                self.monthly_table.setItem(row, 2, QTableWidgetItem(str(data["items"])))
                self.monthly_table.setItem(
                    row, 3, QTableWidgetItem(f"{self.currency}{data['total']:,.2f}")
                )
                self.monthly_table.setItem(
                    row, 4, QTableWidgetItem(f"{self.currency}{data['discount']:,.2f}")
                )
                self.monthly_table.setItem(
                    row, 5, QTableWidgetItem(f"{self.currency}{data['net']:,.2f}")
                )
                self.monthly_table.setItem(
                    row, 6, QTableWidgetItem(f"{self.currency}{data['profit']:,.2f}")
                )

        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Could not load monthly report: {str(e)}"
            )
        finally:
            session.close()

    def export_daily_pdf(self):
        """Export daily report to PDF"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                SimpleDocTemplate,
                Table,
                TableStyle,
                Paragraph,
                Spacer,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER

            date = self.date_picker.date().toPython()
            date_str = date.strftime("%Y-%m-%d")

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF Report",
                f"Daily_Sales_Report_{date_str}.pdf",
                "PDF Files (*.pdf)",
            )

            if not file_path:
                return

            # Get settings
            session = self.db.get_session()
            try:
                settings = {}
                rows = session.query(Setting).all()
                for row in rows:
                    settings[row.key] = row.value

                shop_name = settings.get("shop_name", "My Shop")
                shop_address = settings.get("shop_address", "123 Main Street")
                shop_phone = settings.get("phone_number", "+92-300-0000000")
            except Exception:
                shop_name = "My Shop"
                shop_address = "123 Main Street"
                shop_phone = "+92-300-0000000"
            finally:
                session.close()

            # Create PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                topMargin=20 * mm,
                bottomMargin=20 * mm,
                leftMargin=20 * mm,
                rightMargin=20 * mm,
            )

            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#0f172a"),
                alignment=TA_CENTER,
                spaceAfter=6,
            )

            subtitle_style = ParagraphStyle(
                "CustomSubtitle",
                parent=styles["Normal"],
                fontSize=12,
                textColor=colors.HexColor("#64748b"),
                alignment=TA_CENTER,
                spaceAfter=12,
            )

            section_title_style = ParagraphStyle(
                "SectionTitle",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#0f172a"),
                spaceAfter=10,
                spaceBefore=14,
            )

            summary_label_style = ParagraphStyle(
                "SummaryLabel",
                parent=styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#64748b"),
                alignment=TA_CENTER,
            )

            summary_value_style = ParagraphStyle(
                "SummaryValue",
                parent=styles["Normal"],
                fontSize=16,
                textColor=colors.HexColor("#0f172a"),
                alignment=TA_CENTER,
                spaceAfter=4,
            )

            # Build content
            elements = []

            # Header
            elements.append(Paragraph(shop_name, title_style))
            elements.append(Paragraph(shop_address, subtitle_style))
            elements.append(Paragraph(f"Phone: {shop_phone}", subtitle_style))
            elements.append(Spacer(1, 6 * mm))

            # Report Title
            elements.append(
                Paragraph(
                    "Daily Sales Report",
                    ParagraphStyle(
                        "ReportTitle",
                        parent=styles["Heading2"],
                        fontSize=16,
                        textColor=colors.HexColor("#2563eb"),
                        alignment=TA_CENTER,
                        spaceAfter=4,
                    ),
                )
            )
            elements.append(Paragraph(date.strftime("%A, %B %d, %Y"), subtitle_style))
            elements.append(Spacer(1, 6 * mm))

            # Summary Cards
            summary_data = []
            summary_data.append(
                [
                    Paragraph("💰 Total Sales", summary_label_style),
                    Paragraph(self.daily_total_sales.text(), summary_value_style),
                ]
            )
            summary_data.append(
                [
                    Paragraph("📈 Total Profit", summary_label_style),
                    Paragraph(self.daily_total_profit.text(), summary_value_style),
                ]
            )
            summary_data.append(
                [
                    Paragraph("🧾 Total Bills", summary_label_style),
                    Paragraph(self.daily_total_bills.text(), summary_value_style),
                ]
            )
            summary_data.append(
                [
                    Paragraph("📦 Items Sold", summary_label_style),
                    Paragraph(self.daily_items_sold.text(), summary_value_style),
                ]
            )

            summary_table = Table(summary_data, colWidths=[50 * mm, 50 * mm])
            summary_table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                        ("BORDERCOLOR", (0, 0), (-1, -1), colors.HexColor("#e2e8f0")),
                        ("BORDERWIDTH", (0, 0), (-1, -1), 1),
                        ("ROUNDEDCORNERS", (0, 0), (-1, -1), 8),
                        ("PADDING", (0, 0), (-1, -1), 12),
                    ]
                )
            )
            elements.append(summary_table)
            elements.append(Spacer(1, 8 * mm))

            # Details Table
            elements.append(Paragraph("Sales Details", section_title_style))
            elements.append(Spacer(1, 4 * mm))

            # Get data from table
            table_data = []
            # Header
            table_data.append(
                [
                    Paragraph("Invoice", styles["Normal"]),
                    Paragraph("Time", styles["Normal"]),
                    Paragraph("Items", styles["Normal"]),
                    Paragraph("Subtotal", styles["Normal"]),
                    Paragraph("Discount", styles["Normal"]),
                    Paragraph("Total", styles["Normal"]),
                    Paragraph("Profit", styles["Normal"]),
                ]
            )

            for row in range(self.daily_table.rowCount()):
                invoice = self.daily_table.item(row, 0).text()
                time = self.daily_table.item(row, 1).text()
                items = self.daily_table.item(row, 2).text()
                subtotal = self.daily_table.item(row, 3).text()
                discount = self.daily_table.item(row, 4).text()
                total = self.daily_table.item(row, 5).text()
                profit = self.daily_table.item(row, 6).text()

                table_data.append(
                    [
                        Paragraph(invoice, styles["Normal"]),
                        Paragraph(time, styles["Normal"]),
                        Paragraph(items, styles["Normal"]),
                        Paragraph(subtotal, styles["Normal"]),
                        Paragraph(discount, styles["Normal"]),
                        Paragraph(total, styles["Normal"]),
                        Paragraph(profit, styles["Normal"]),
                    ]
                )

            col_widths = [30 * mm, 35 * mm, 25 * mm, 30 * mm, 30 * mm, 30 * mm, 30 * mm]

            detail_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            detail_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("TOPPADDING", (0, 0), (-1, 0), 8),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("TOPPADDING", (0, 1), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                        ("BACKGROUND", (0, 2), (-1, -2), colors.white),
                        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                    ]
                )
            )

            elements.append(detail_table)
            elements.append(Spacer(1, 8 * mm))

            # Footer
            pakistan_tz = pytz.timezone("Asia/Karachi")
            now = datetime.now(pakistan_tz)

            footer_style = ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor("#94a3b8"),
                alignment=TA_CENTER,
            )
            elements.append(
                Paragraph(
                    f"Report generated on {now.strftime('%A, %B %d, %Y at %I:%M %p')}",
                    footer_style,
                )
            )
            elements.append(Paragraph("© 2026 Shop Management System", footer_style))

            # Build PDF
            doc.build(elements)

            QMessageBox.information(
                self,
                "Success",
                f"Daily report exported successfully!\n\nSaved to: {file_path}",
            )

        except ImportError:
            QMessageBox.warning(
                self,
                "Error",
                "ReportLab library is not installed.\nPlease install: pip install reportlab",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not export PDF: {str(e)}")

    def export_monthly_pdf(self):
        """Export monthly report to PDF"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                SimpleDocTemplate,
                Table,
                TableStyle,
                Paragraph,
                Spacer,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER

            year = self.year_combo.currentText()
            month = self.month_combo.currentText()
            month_num = self.month_combo.currentIndex() + 1

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF Report",
                f"Monthly_Sales_Report_{year}_{month_num:02d}.pdf",
                "PDF Files (*.pdf)",
            )

            if not file_path:
                return

            # Get settings
            session = self.db.get_session()
            try:
                settings = {}
                rows = session.query(Setting).all()
                for row in rows:
                    settings[row.key] = row.value

                shop_name = settings.get("shop_name", "My Shop")
                shop_address = settings.get("shop_address", "123 Main Street")
                shop_phone = settings.get("phone_number", "+92-300-0000000")
            except Exception:
                shop_name = "My Shop"
                shop_address = "123 Main Street"
                shop_phone = "+92-300-0000000"
            finally:
                session.close()

            # Create PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                topMargin=20 * mm,
                bottomMargin=20 * mm,
                leftMargin=20 * mm,
                rightMargin=20 * mm,
            )

            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#0f172a"),
                alignment=TA_CENTER,
                spaceAfter=6,
            )

            subtitle_style = ParagraphStyle(
                "CustomSubtitle",
                parent=styles["Normal"],
                fontSize=12,
                textColor=colors.HexColor("#64748b"),
                alignment=TA_CENTER,
                spaceAfter=12,
            )

            section_title_style = ParagraphStyle(
                "SectionTitle",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#0f172a"),
                spaceAfter=10,
                spaceBefore=14,
            )

            summary_label_style = ParagraphStyle(
                "SummaryLabel",
                parent=styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#64748b"),
                alignment=TA_CENTER,
            )

            summary_value_style = ParagraphStyle(
                "SummaryValue",
                parent=styles["Normal"],
                fontSize=16,
                textColor=colors.HexColor("#0f172a"),
                alignment=TA_CENTER,
                spaceAfter=4,
            )

            # Build content
            elements = []

            # Header
            elements.append(Paragraph(shop_name, title_style))
            elements.append(Paragraph(shop_address, subtitle_style))
            elements.append(Paragraph(f"Phone: {shop_phone}", subtitle_style))
            elements.append(Spacer(1, 6 * mm))

            # Report Title
            elements.append(
                Paragraph(
                    "Monthly Sales Report",
                    ParagraphStyle(
                        "ReportTitle",
                        parent=styles["Heading2"],
                        fontSize=16,
                        textColor=colors.HexColor("#2563eb"),
                        alignment=TA_CENTER,
                        spaceAfter=4,
                    ),
                )
            )
            elements.append(Paragraph(f"{month} {year}", subtitle_style))
            elements.append(Spacer(1, 6 * mm))

            # Summary Cards
            summary_data = []
            summary_data.append(
                [
                    Paragraph("💰 Total Sales", summary_label_style),
                    Paragraph(self.monthly_total_sales.text(), summary_value_style),
                ]
            )
            summary_data.append(
                [
                    Paragraph("📈 Total Profit", summary_label_style),
                    Paragraph(self.monthly_total_profit.text(), summary_value_style),
                ]
            )
            summary_data.append(
                [
                    Paragraph("🧾 Total Bills", summary_label_style),
                    Paragraph(self.monthly_total_bills.text(), summary_value_style),
                ]
            )
            summary_data.append(
                [
                    Paragraph("📦 Items Sold", summary_label_style),
                    Paragraph(self.monthly_items_sold.text(), summary_value_style),
                ]
            )

            summary_table = Table(summary_data, colWidths=[50 * mm, 50 * mm])
            summary_table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                        ("BORDERCOLOR", (0, 0), (-1, -1), colors.HexColor("#e2e8f0")),
                        ("BORDERWIDTH", (0, 0), (-1, -1), 1),
                        ("ROUNDEDCORNERS", (0, 0), (-1, -1), 8),
                        ("PADDING", (0, 0), (-1, -1), 12),
                    ]
                )
            )
            elements.append(summary_table)
            elements.append(Spacer(1, 8 * mm))

            # Details Table
            elements.append(Paragraph("Daily Breakdown", section_title_style))
            elements.append(Spacer(1, 4 * mm))

            # Get data from table
            table_data = []
            # Header
            table_data.append(
                [
                    Paragraph("Date", styles["Normal"]),
                    Paragraph("Invoices", styles["Normal"]),
                    Paragraph("Items", styles["Normal"]),
                    Paragraph("Total Sales", styles["Normal"]),
                    Paragraph("Discount", styles["Normal"]),
                    Paragraph("Net Sales", styles["Normal"]),
                    Paragraph("Profit", styles["Normal"]),
                ]
            )

            for row in range(self.monthly_table.rowCount()):
                date = self.monthly_table.item(row, 0).text()
                invoices = self.monthly_table.item(row, 1).text()
                items = self.monthly_table.item(row, 2).text()
                total = self.monthly_table.item(row, 3).text()
                discount = self.monthly_table.item(row, 4).text()
                net = self.monthly_table.item(row, 5).text()
                profit = self.monthly_table.item(row, 6).text()

                table_data.append(
                    [
                        Paragraph(date, styles["Normal"]),
                        Paragraph(invoices, styles["Normal"]),
                        Paragraph(items, styles["Normal"]),
                        Paragraph(total, styles["Normal"]),
                        Paragraph(discount, styles["Normal"]),
                        Paragraph(net, styles["Normal"]),
                        Paragraph(profit, styles["Normal"]),
                    ]
                )

            col_widths = [35 * mm, 25 * mm, 25 * mm, 30 * mm, 30 * mm, 30 * mm, 30 * mm]

            detail_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            detail_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("TOPPADDING", (0, 0), (-1, 0), 8),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("TOPPADDING", (0, 1), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                        ("BACKGROUND", (0, 2), (-1, -2), colors.white),
                        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                    ]
                )
            )

            elements.append(detail_table)
            elements.append(Spacer(1, 8 * mm))

            # Footer
            pakistan_tz = pytz.timezone("Asia/Karachi")
            now = datetime.now(pakistan_tz)

            footer_style = ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor("#94a3b8"),
                alignment=TA_CENTER,
            )
            elements.append(
                Paragraph(
                    f"Report generated on {now.strftime('%A, %B %d, %Y at %I:%M %p')}",
                    footer_style,
                )
            )
            elements.append(Paragraph("© 2026 Shop Management System", footer_style))

            # Build PDF
            doc.build(elements)

            QMessageBox.information(
                self,
                "Success",
                f"Monthly report exported successfully!\n\nSaved to: {file_path}",
            )

        except ImportError:
            QMessageBox.warning(
                self,
                "Error",
                "ReportLab library is not installed.\nPlease install: pip install reportlab",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not export PDF: {str(e)}")
