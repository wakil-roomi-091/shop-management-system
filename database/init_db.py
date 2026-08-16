"""
Initialize Database
Creates tables and populates with default data
"""

from .db_manager import DatabaseManager
from .models import Category, Setting
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize database with default data"""
    
    db = DatabaseManager()
    session = db.get_session()
    
    try:
        # Create default categories
        default_categories = [
            'Electronics',
            'Groceries',
            'Clothing',
            'Books',
            'Stationery',
            'Health & Beauty',
            'Home & Kitchen',
            'Toys & Games',
            'Sports & Outdoors',
            'Auto Parts',
            'Other'
        ]
        
        for category_name in default_categories:
            existing = session.query(Category).filter_by(name=category_name).first()
            if not existing:
                category = Category(name=category_name)
                session.add(category)
                logger.info(f"Added category: {category_name}")
        
        # Create default settings
        default_settings = {
            'shop_name': 'My Shop',
            'owner_name': 'Shop Owner',
            'shop_address': '123 Main Street, City',
            'phone_number': '+92-300-0000000',
            'email': 'info@myshop.com',
            'currency_symbol': 'Rs',
            'receipt_footer': 'Thank you for shopping with us!',
            'default_printer': 'Default',
            'tax_rate': '0.0'
        }
        
        for key, value in default_settings.items():
            existing = session.query(Setting).filter_by(key=key).first()
            if not existing:
                setting = Setting(key=key, value=value)
                session.add(setting)
                logger.info(f"Added setting: {key} = {value}")
        
        # Commit all changes
        session.commit()
        logger.info("Database initialization completed successfully!")
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    # Setup logging for standalone execution
    logging.basicConfig(level=logging.INFO)
    initialize_database()
    print("Database initialized successfully!")