"""
Thermal Printer Support
ESC/POS thermal printer integration
"""

import os
import sys
from datetime import datetime
import pytz

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager, Setting


class ThermalPrinter:
    """Handle thermal printer operations"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.printer_name = None
        self.shop_name = "My Shop"
        self.shop_address = "123 Main Street"
        self.shop_phone = "+92-300-0000000"
        self.currency = "Rs"
        self.footer = "Thank you for shopping with us!"
        
        self.load_settings()
    
    def load_settings(self):
        """Load printer settings from database"""
        session = self.db.get_session()
        try:
            settings = {}
            rows = session.query(Setting).all()
            for row in rows:
                settings[row.key] = row.value
            
            self.printer_name = settings.get('default_printer', None)
            self.shop_name = settings.get('shop_name', 'My Shop')
            self.shop_address = settings.get('shop_address', '123 Main Street')
            self.shop_phone = settings.get('phone_number', '+92-300-0000000')
            self.currency = settings.get('currency_symbol', 'Rs')
            self.footer = settings.get('receipt_footer', 'Thank you for shopping with us!')
            
        except Exception as e:
            print(f"Error loading printer settings: {e}")
        finally:
            session.close()
    
    def print_receipt(self, sale_data):
        """Print receipt using thermal printer"""
        try:
            # Try to import escpos
            try:
                from escpos.printer import Usb, Network, Serial, Dummy
                HAS_ESC_POS = True
            except ImportError:
                HAS_ESC_POS = False
                print("ESC/POS library not installed. Install with: pip install python-escpos")
                return False
            
            # Get printer type from settings
            printer_type = 'usb'  # Default
            
            # Try to connect to printer
            try:
                if printer_type == 'usb':
                    printer = Usb(0x0416, 0x5011)  # Common VID/PID for thermal printers
                elif printer_type == 'network':
                    printer = Network("192.168.1.100")  # IP address
                else:
                    # Try auto-detection
                    printer = Usb()
            except:
                # Fallback to dummy printer for testing
                printer = Dummy()
                print("Using dummy printer for testing")
            
            # Build receipt content
            receipt = self._build_receipt_content(sale_data)
            
            # Print
            printer.text(receipt)
            printer.cut()
            
            return True
            
        except Exception as e:
            print(f"Error printing receipt: {e}")
            return False
    
    def _build_receipt_content(self, sale_data):
        """Build receipt text content"""
        # Local time
        pakistan_tz = pytz.timezone('Asia/Karachi')
        now = datetime.now(pakistan_tz)
        
        lines = []
        
        # Header
        lines.append("=" * 32)
        lines.append(f"{self.shop_name:^32}")
        lines.append(f"{self.shop_address:^32}")
        lines.append(f"Tel: {self.shop_phone:^32}")
        lines.append("=" * 32)
        lines.append("")
        
        # Invoice Info
        invoice = sale_data.get('invoice_number', 'INV-000001')
        lines.append(f"Invoice: {invoice}")
        lines.append(f"Date: {now.strftime('%Y-%m-%d %I:%M %p')}")
        lines.append("")
        lines.append("-" * 32)
        
        # Items
        lines.append(f"{'Item':<18} {'Qty':>4} {'Price':>10}")
        lines.append("-" * 32)
        
        for item in sale_data.get('items', []):
            name = item['name'][:18]
            qty = item['quantity']
            price = f"{self.currency}{item['price']:,.2f}"
            lines.append(f"{name:<18} {qty:>4} {price:>10}")
        
        lines.append("-" * 32)
        
        # Totals
        subtotal = sale_data.get('subtotal', 0)
        discount = sale_data.get('discount_amount', 0)
        total = sale_data.get('net_total', 0)
        cash = sale_data.get('cash_received', 0)
        change = sale_data.get('change_returned', 0)
        
        lines.append(f"{'Subtotal:':<22} {self.currency}{subtotal:>8,.2f}")
        if discount > 0:
            lines.append(f"{'Discount:':<22} {self.currency}{discount:>8,.2f}")
        lines.append("-" * 32)
        lines.append(f"{'TOTAL:':<22} {self.currency}{total:>8,.2f}")
        lines.append("")
        lines.append(f"{'Cash:':<22} {self.currency}{cash:>8,.2f}")
        lines.append(f"{'Change:':<22} {self.currency}{change:>8,.2f}")
        lines.append("")
        lines.append("=" * 32)
        
        # Footer
        lines.append(f"{self.footer:^32}")
        lines.append("Thank you for your business!")
        lines.append("=" * 32)
        lines.append("")
        lines.append("")
        
        return "\n".join(lines)
    
    def get_available_printers(self):
        """Get list of available printers"""
        printers = []
        
        try:
            import win32print
            for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS):
                printers.append(printer[2])
        except:
            # Linux/Mac - use lpinfo
            try:
                import subprocess
                result = subprocess.run(['lpinfo', '-v'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'direct usb' in line.lower():
                        printers.append(line.strip())
            except:
                printers.append("No printers found")
        
        return printers