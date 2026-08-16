"""
Settings Module
Allows shop owner to change shop information and preferences
"""

import sys
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QMessageBox, QTabWidget, QFormLayout, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QScrollArea, QFrame,
    QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QFont

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import DatabaseManager, Setting


class SettingsWindow(QWidget):
    """Settings window for shop configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.setWindowTitle("Shop Settings")
        
        screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        if avail:
            init_w = min(680, int(avail.width() * 0.85))
            init_h = min(720, int(avail.height() * 0.85))
            self.resize(init_w, init_h)
        else:
            self.resize(600, 650)
        
        # Apply styles
        from ui.styles import get_app_style
        self.setStyleSheet(get_app_style())
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 20, 24, 20)
        
        # Title
        title = QLabel("Shop Settings")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Tab 1: General Settings
        general_tab = self.create_general_tab()
        tabs.addTab(self._make_scrollable(general_tab), "General")
        
        # Tab 2: Receipt Settings
        receipt_tab = self.create_receipt_tab()
        tabs.addTab(self._make_scrollable(receipt_tab), "Receipt")
        
        # Tab 3: System Settings
        system_tab = self.create_system_tab()
        tabs.addTab(self._make_scrollable(system_tab), "System")
        
        # Tab 4: Printer Settings
        printer_tab = self.create_printer_tab()
        tabs.addTab(self._make_scrollable(printer_tab), "Printer")
        
        main_layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("success")
        save_btn.setMinimumHeight(45)
        save_btn.setMinimumWidth(150)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Default")
        reset_btn.setObjectName("secondary")
        reset_btn.setMinimumHeight(45)
        reset_btn.setMinimumWidth(150)
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("danger")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    def _make_scrollable(self, widget):
        """Wrap tab content widget in a transparent scroll area"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setWidget(widget)
        return scroll
    
    def create_general_tab(self):
        """Create the general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Shop Information Group
        shop_group = QGroupBox("Shop Information")
        shop_layout = QFormLayout()
        shop_layout.setSpacing(14)
        
        self.shop_name = QLineEdit()
        self.shop_name.setMinimumHeight(36)
        self.shop_name.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        shop_layout.addRow("Shop Name:", self.shop_name)
        
        self.owner_name = QLineEdit()
        self.owner_name.setMinimumHeight(36)
        self.owner_name.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        shop_layout.addRow("Owner Name:", self.owner_name)
        
        self.shop_address = QTextEdit()
        self.shop_address.setMaximumHeight(60)
        self.shop_address.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        shop_layout.addRow("Shop Address:", self.shop_address)
        
        self.phone_number = QLineEdit()
        self.phone_number.setMinimumHeight(36)
        self.phone_number.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        shop_layout.addRow("Phone Number:", self.phone_number)
        
        self.email = QLineEdit()
        self.email.setMinimumHeight(36)
        self.email.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        shop_layout.addRow("Email:", self.email)
        
        shop_group.setLayout(shop_layout)
        layout.addWidget(shop_group)
        
        # Currency Group
        currency_group = QGroupBox("Currency Settings")
        currency_layout = QFormLayout()
        currency_layout.setSpacing(14)
        
        self.currency_symbol = QLineEdit()
        self.currency_symbol.setPlaceholderText("e.g., Rs, $, €")
        self.currency_symbol.setMinimumHeight(36)
        self.currency_symbol.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        currency_layout.addRow("Currency Symbol:", self.currency_symbol)
        
        currency_group.setLayout(currency_layout)
        layout.addWidget(currency_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_receipt_tab(self):
        """Create the receipt settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Receipt Settings Group
        receipt_group = QGroupBox("Receipt Settings")
        receipt_layout = QFormLayout()
        receipt_layout.setSpacing(14)
        
        self.receipt_footer = QTextEdit()
        self.receipt_footer.setMaximumHeight(80)
        self.receipt_footer.setPlaceholderText("Thank you for shopping with us!")
        self.receipt_footer.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        receipt_layout.addRow("Footer Message:", self.receipt_footer)
        
        # Receipt options
        self.show_tax = QCheckBox("Show Tax on Receipt")
        self.show_tax.setStyleSheet("font-size: 14px;")
        receipt_layout.addRow("", self.show_tax)
        
        self.show_profit = QCheckBox("Show Profit on Receipt (Staff only)")
        self.show_profit.setStyleSheet("font-size: 14px;")
        receipt_layout.addRow("", self.show_profit)
        
        receipt_group.setLayout(receipt_layout)
        layout.addWidget(receipt_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_system_tab(self):
        """Create the system settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # System Settings Group
        system_group = QGroupBox("System Settings")
        system_layout = QFormLayout()
        system_layout.setSpacing(14)
        
        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setRange(0, 100)
        self.tax_rate.setSuffix(" %")
        self.tax_rate.setSingleStep(0.5)
        self.tax_rate.setMinimumHeight(36)
        self.tax_rate.setStyleSheet("font-size: 14px;")
        system_layout.addRow("Tax Rate:", self.tax_rate)
        
        self.low_stock_threshold = QSpinBox()
        self.low_stock_threshold.setRange(0, 100)
        self.low_stock_threshold.setSuffix(" units")
        self.low_stock_threshold.setMinimumHeight(36)
        self.low_stock_threshold.setStyleSheet("font-size: 14px;")
        system_layout.addRow("Low Stock Alert Level:", self.low_stock_threshold)
        
        self.auto_backup = QCheckBox("Auto-backup on exit")
        self.auto_backup.setStyleSheet("font-size: 14px;")
        system_layout.addRow("", self.auto_backup)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Database Info Group
        db_group = QGroupBox("Database Information")
        db_layout = QVBoxLayout()
        db_layout.setSpacing(8)
        
        db_info = QLabel(f"Database Location: {self.db.db_path}")
        db_info.setWordWrap(True)
        db_info.setStyleSheet("font-size: 13px; color: #64748b;")
        db_layout.addWidget(db_info)
        
        # Show table count
        try:
            session = self.db.get_session()
            from database.models import Product, Sale, Category, Customer, User, Expense
            product_count = session.query(Product).count()
            sale_count = session.query(Sale).count()
            category_count = session.query(Category).count()
            customer_count = session.query(Customer).count()
            user_count = session.query(User).count()
            expense_count = session.query(Expense).count()
            session.close()
            
            stats_label = QLabel(
                f"Database Stats:\n"
                f"   • Categories: {category_count}\n"
                f"   • Products: {product_count}\n"
                f"   • Customers: {customer_count}\n"
                f"   • Sales: {sale_count}\n"
                f"   • Users: {user_count}\n"
                f"   • Expenses: {expense_count}"
            )
            stats_label.setStyleSheet("font-size: 13px; color: #475569; padding: 8px; background-color: #f8fafc; border-radius: 8px;")
            db_layout.addWidget(stats_label)
        except:
            pass
        
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_printer_tab(self):
        """Create the printer settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Printer Settings Group
        printer_group = QGroupBox("Printer Settings")
        printer_layout = QFormLayout()
        printer_layout.setSpacing(14)
        
        self.printer_type = QComboBox()
        self.printer_type.addItems(['USB', 'Network', 'Serial'])
        self.printer_type.setMinimumHeight(36)
        self.printer_type.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        printer_layout.addRow("Printer Type:", self.printer_type)
        
        self.printer_name = QLineEdit()
        self.printer_name.setPlaceholderText("USB: auto-detect | Network: IP address | Serial: COM port")
        self.printer_name.setMinimumHeight(36)
        self.printer_name.setStyleSheet("font-size: 14px; padding: 6px 12px;")
        printer_layout.addRow("Printer Name/Address:", self.printer_name)
        
        # Printer info
        info_label = QLabel(
            "📌 Printer Setup Guide:\n"
            "• USB: Auto-detected, leave blank\n"
            "• Network: Enter IP address (e.g., 192.168.1.100)\n"
            "• Serial: Enter COM port (e.g., COM3)"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 12px; color: #64748b; padding: 8px; background-color: #f8fafc; border-radius: 8px;")
        printer_layout.addRow("", info_label)
        
        printer_group.setLayout(printer_layout)
        layout.addWidget(printer_group)
        
        # Test Print Button
        test_group = QGroupBox("Test Printer")
        test_layout = QVBoxLayout()
        test_layout.setSpacing(10)
        
        test_btn = QPushButton("🖨️ Test Print")
        test_btn.setObjectName("primary")
        test_btn.setMinimumHeight(45)
        test_btn.clicked.connect(self.test_printer)
        test_layout.addWidget(test_btn)
        
        test_info = QLabel("Click to print a test receipt and verify printer connection.")
        test_info.setWordWrap(True)
        test_info.setStyleSheet("font-size: 12px; color: #94a3b8;")
        test_layout.addWidget(test_info)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def load_settings(self):
        """Load settings from database"""
        session = self.db.get_session()
        try:
            # Load all settings
            settings = session.query(Setting).all()
            setting_dict = {setting.key: setting.value for setting in settings}
            
            # General settings
            self.shop_name.setText(setting_dict.get('shop_name', ''))
            self.owner_name.setText(setting_dict.get('owner_name', ''))
            self.shop_address.setText(setting_dict.get('shop_address', ''))
            self.phone_number.setText(setting_dict.get('phone_number', ''))
            self.email.setText(setting_dict.get('email', ''))
            self.currency_symbol.setText(setting_dict.get('currency_symbol', 'Rs'))
            
            # Receipt settings
            self.receipt_footer.setText(setting_dict.get('receipt_footer', 'Thank you for shopping with us!'))
            
            # Printer settings - FIXED: Use printer_name, not default_printer
            self.printer_name.setText(setting_dict.get('default_printer', ''))
            self.printer_type.setCurrentText(setting_dict.get('printer_type', 'USB'))
            
            # System settings
            try:
                self.tax_rate.setValue(float(setting_dict.get('tax_rate', '0')))
            except:
                self.tax_rate.setValue(0)
            
            # Checkboxes
            self.show_tax.setChecked(setting_dict.get('show_tax', 'False').lower() == 'true')
            self.show_profit.setChecked(setting_dict.get('show_profit', 'False').lower() == 'true')
            self.auto_backup.setChecked(setting_dict.get('auto_backup', 'False').lower() == 'true')
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load settings: {str(e)}")
        finally:
            session.close()
    
    def save_settings(self):
        """Save settings to database"""
        # Validate required fields
        if not self.shop_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "Shop Name is required!")
            return
        
        if not self.currency_symbol.text().strip():
            QMessageBox.warning(self, "Validation Error", "Currency Symbol is required!")
            return
        
        session = self.db.get_session()
        try:
            # Prepare settings dictionary
            settings_data = {
                'shop_name': self.shop_name.text().strip(),
                'owner_name': self.owner_name.text().strip(),
                'shop_address': self.shop_address.toPlainText().strip(),
                'phone_number': self.phone_number.text().strip(),
                'email': self.email.text().strip(),
                'currency_symbol': self.currency_symbol.text().strip(),
                'receipt_footer': self.receipt_footer.toPlainText().strip(),
                'default_printer': self.printer_name.text().strip(),
                'printer_type': self.printer_type.currentText(),
                'tax_rate': str(self.tax_rate.value()),
                'show_tax': str(self.show_tax.isChecked()),
                'show_profit': str(self.show_profit.isChecked()),
                'auto_backup': str(self.auto_backup.isChecked())
            }
            
            # Update or create each setting
            for key, value in settings_data.items():
                setting = session.query(Setting).filter_by(key=key).first()
                if setting:
                    setting.value = value
                else:
                    setting = Setting(key=key, value=value)
                    session.add(setting)
            
            session.commit()
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.close()
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Could not save settings: {str(e)}")
        finally:
            session.close()
    
    def reset_settings(self):
        """Reset settings to default values"""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            default_settings = {
                'shop_name': 'My Shop',
                'owner_name': 'Shop Owner',
                'shop_address': '123 Main Street, City',
                'phone_number': '+92-300-0000000',
                'email': 'info@myshop.com',
                'currency_symbol': 'Rs',
                'receipt_footer': 'Thank you for shopping with us!',
                'default_printer': '',
                'printer_type': 'USB',
                'tax_rate': '0',
                'show_tax': 'False',
                'show_profit': 'False',
                'auto_backup': 'False'
            }
            
            session = self.db.get_session()
            try:
                for key, value in default_settings.items():
                    setting = session.query(Setting).filter_by(key=key).first()
                    if setting:
                        setting.value = value
                    else:
                        setting = Setting(key=key, value=value)
                        session.add(setting)
                
                session.commit()
                QMessageBox.information(self, "Success", "Settings reset to default!")
                self.load_settings()
                
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Could not reset settings: {str(e)}")
            finally:
                session.close()
    
    def test_printer(self):
        """Test printer connection"""
        try:
            from escpos.printer import Usb, Network, Serial, Dummy
            from datetime import datetime
            
            printer_type = self.printer_type.currentText()
            printer_name = self.printer_name.text().strip()
            
            p = None
            
            if printer_type == 'USB':
                try:
                    p = Usb(0x0416, 0x5011)
                except:
                    try:
                        import usb.core
                        devices = usb.core.find(find_all=True)
                        for device in devices:
                            if device.idVendor in [0x0416, 0x0b05, 0x1a86, 0x0483]:
                                try:
                                    p = Usb(device.idVendor, device.idProduct)
                                    break
                                except:
                                    continue
                    except:
                        pass
            elif printer_type == 'Network' and printer_name:
                try:
                    p = Network(printer_name)
                except:
                    pass
            elif printer_type == 'Serial' and printer_name:
                try:
                    p = Serial(printer_name, 9600)
                except:
                    pass
            
            if p is None:
                QMessageBox.warning(
                    self,
                    "Printer Not Found",
                    f"Could not find {printer_type} printer.\n\n"
                    "Please check:\n"
                    "• Printer is connected and powered on\n"
                    "• Correct printer type selected\n"
                    "• Correct IP address/COM port entered"
                )
                return
            
            # Print test receipt
            test_text = f"""
================================
    TEST PRINT
================================
Printer is working correctly!

If you can read this, your
thermal printer is properly
configured and connected.

Date: {datetime.now().strftime("%Y-%m-%d")}
Time: {datetime.now().strftime("%I:%M %p")}
================================
Thank you for testing!
================================

"""
            
            p.text(test_text)
            p.cut()
            p.close()
            
            QMessageBox.information(
                self,
                "Success",
                "✅ Test print completed successfully!\n\n"
                "Check your printer for the test receipt."
            )
            
        except ImportError:
            QMessageBox.warning(
                self,
                "Library Not Installed",
                "ESC/POS printer library not installed.\n\n"
                "Please install it using:\n"
                "pip install python-escpos"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Test Failed",
                f"Could not connect to printer.\n\nError: {str(e)}\n\n"
                "Please check your printer connection and settings."
            )