"""
Database Manager
Handles database connection, session management, and basic operations
"""

import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_path():
    """Get the correct database path for both development and packaged app"""
    if getattr(sys, "frozen", False):
        # Running as compiled .exe - look in the same folder as the .exe
        return os.path.join(os.path.dirname(sys.executable), "shop.db")
    else:
        # Running as Python script - look in the project folder
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shop.db"
        )


def get_app_root():
    """Get the application root directory (where .exe or main.py is located)"""
    if getattr(sys, "frozen", False):
        # Running as compiled .exe
        return os.path.dirname(sys.executable)
    else:
        # Running as Python script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DatabaseManager:
    """Singleton class for managing database operations"""

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize database connection"""
        # Database file path - dynamically determined
        self.db_path = get_db_path()

        # Create engine with SQLite
        self._engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,  # Set to True for debugging SQL queries
            connect_args={
                "check_same_thread": False,  # Allow multi-threading
                "timeout": 10,  # Wait 10 seconds for locked database
            },
        )

        # Create session factory
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

        # Create tables if they don't exist
        self.create_tables()

        logger.info(f"Database initialized at: {self.db_path}")

    def create_tables(self):
        """Create all tables defined in models"""
        try:
            Base.metadata.create_all(self._engine)
            logger.info("Database tables created/verified successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def get_session(self) -> Session:
        """Get a new database session"""
        try:
            return self._session_factory()
        except SQLAlchemyError as e:
            logger.error(f"Error creating session: {e}")
            raise

    def get_engine(self):
        """Get database engine"""
        return self._engine

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        inspector = inspect(self._engine)
        return table_name in inspector.get_table_names()

    def get_table_names(self):
        """Get all table names"""
        inspector = inspect(self._engine)
        return inspector.get_table_names()

    def backup_database(self, backup_path: str = None) -> bool:
        """Create a backup of the database file"""
        try:
            import shutil

            # If no backup path provided, create one in the app root
            if backup_path is None:
                app_root = get_app_root()
                backups_dir = os.path.join(app_root, "backups")

                # Create backups directory if it doesn't exist
                if not os.path.exists(backups_dir):
                    os.makedirs(backups_dir)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(backups_dir, f"backup_{timestamp}.db")

            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False

    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup file"""
        try:
            import shutil

            # Close all sessions first
            self._engine.dispose()
            # Restore file
            shutil.copy2(backup_path, self.db_path)
            # Reconnect
            self._initialize()
            logger.info(f"Database restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return False
