"""
Test Customers Module
Launch the customer management window
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from modules.customers import CustomersWindow
from database import DatabaseManager
from database.init_db import initialize_database


def main():
    """Launch customers window for testing"""
    
    # Initialize database
    try:
        db = DatabaseManager()
        session = db.get_session()
        session.close()
    except:
        initialize_database()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show customers window
    window = CustomersWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()