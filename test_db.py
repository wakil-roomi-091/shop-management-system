"""
Test Database
Run this to verify database setup
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager, Category, Product, Setting
from database.init_db import initialize_database

def test_database():
    """Test database setup"""
    
    print("🔍 Testing Database Setup...")
    print("-" * 40)
    
    # 1. Initialize database
    print("📊 Initializing database...")
    initialize_database()
    print("✅ Database initialized!")
    
    # 2. Get database manager
    db = DatabaseManager()
    session = db.get_session()
    
    # 3. Test categories
    print("\n📋 Testing categories...")
    categories = session.query(Category).all()
    print(f"✅ Found {len(categories)} categories:")
    for cat in categories[:5]:  # Show first 5
        print(f"   - {cat.name}")
    if len(categories) > 5:
        print(f"   ... and {len(categories) - 5} more")
    
    # 4. Test settings
    print("\n⚙️ Testing settings...")
    settings = session.query(Setting).all()
    print(f"✅ Found {len(settings)} settings:")
    for setting in settings:
        print(f"   - {setting.key}: {setting.value}")
    
    # 5. Test adding a product
    print("\n📦 Testing product creation...")
    category = session.query(Category).first()
    if category:
        product = Product(
            name="Test Product",
            category_id=category.id,
            buying_price=100.0,
            selling_price=150.0,
            current_stock=10,
            min_stock_level=5,
            description="This is a test product"
        )
        session.add(product)
        session.commit()
        print(f"✅ Added test product: {product.name} (ID: {product.id})")
        print(f"   Category: {category.name}")
        print(f"   Stock: {product.current_stock}")
        print(f"   Min Level: {product.min_stock_level}")
        print(f"   Stock Status: {product.stock_status}")
        print(f"   Profit per unit: Rs{product.profit_margin}")
    
    # 6. Clean up test data
    print("\n🧹 Cleaning up test data...")
    session.query(Product).filter_by(name="Test Product").delete()
    session.commit()
    print("✅ Test data cleaned up!")
    
    session.close()
    print("\n" + "=" * 40)
    print("🎉 All tests passed! Database is ready.")
    print("=" * 40)

if __name__ == "__main__":
    test_database()