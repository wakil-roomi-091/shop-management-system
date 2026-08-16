"""
Test Reports Module
Launch the reports window
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from modules.reports.reports_window import ReportsWindow
from database import DatabaseManager
from database.init_db import initialize_database

def main():
    """Launch reports window for testing"""
    
    # Initialize database if not already done
    try:
        db = DatabaseManager()
        session = db.get_session()
        session.close()
    except:
        initialize_database()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show reports window
    window = ReportsWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()