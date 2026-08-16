"""
Test Settings Module
Launch the settings window to test it
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from modules.settings.settings_window import SettingsWindow
from database import DatabaseManager
from database.init_db import initialize_database

def main():
    """Launch settings window for testing"""
    
    # Initialize database if not already done
    try:
        db = DatabaseManager()
        # Try to query settings to see if database exists
        session = db.get_session()
        session.close()
    except:
        initialize_database()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show settings window
    window = SettingsWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()