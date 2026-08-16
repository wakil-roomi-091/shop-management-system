"""
Test Dashboard Module
Launch the dashboard window
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow
from modules.dashboard import DashboardWindow
from database import DatabaseManager
from database.init_db import initialize_database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shop Management System")
        self.setGeometry(100, 100, 1200, 750)
        
        # Create dashboard
        dashboard = DashboardWindow(self)
        self.setCentralWidget(dashboard)


def main():
    """Launch dashboard for testing"""
    
    # Initialize database
    try:
        db = DatabaseManager()
        session = db.get_session()
        session.close()
    except:
        initialize_database()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create main window with dashboard
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()