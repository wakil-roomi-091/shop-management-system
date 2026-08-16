"""
Seed Database with Sample Data
"""

from database import DatabaseManager
from database.models import Product, Category, Customer, Setting
from database.init_db import initialize_database
import random

def seed_data():
    """Add sample data to the database"""
    
    # Initialize database first
    initialize_database()
    
    db = DatabaseManager()
    session = db.get_session()
    
    try:
        # Get categories
        categories = session.query(Category).all()
        if not categories:
            print("❌ No categories found. Please run initialize_database() first.")
            return
        
        # Sample products
        products = [
            ("Samsung Galaxy S24", categories[0].id, 80000, 95000, 20, 5),
            ("iPhone 15 Pro", categories[0].id, 120000, 145000, 15, 5),
            ("Dell XPS Laptop", categories[0].id, 150000, 180000, 10, 5),
            ("Basmati Rice 5kg", categories[1].id, 500, 650, 50, 10),
            ("Cooking Oil 5L", categories[1].id, 800, 1000, 30, 10),
            ("School Bag", categories[2].id, 800, 1200, 25, 5),
            ("T-Shirt", categories[2].id, 500, 800, 40, 10),
            ("Notebook 100pg", categories[3].id, 50, 80, 100, 10),
            ("Pen Pack (10)", categories[3].id, 150, 250, 60, 5),
        ]
        
        for name, cat_id, buy_price, sell_price, stock, min_stock in products:
            existing = session.query(Product).filter_by(name=name).first()
            if not existing:
                product = Product(
                    name=name,
                    category_id=cat_id,
                    buying_price=buy_price,
                    selling_price=sell_price,
                    current_stock=stock,
                    min_stock_level=min_stock,
                    description=f"Sample {name}"
                )
                session.add(product)
                print(f"✅ Added product: {name}")
        
        # Sample customers
        customers = [
            ("Ali Ahmed", "0300-1111111", "ali@email.com", "123 Main St"),
            ("Sara Khan", "0300-2222222", "sara@email.com", "456 Park Ave"),
            ("Usman Malik", "0300-3333333", "usman@email.com", "789 Lake Rd"),
            ("Fatima Noor", "0300-4444444", "fatima@email.com", "321 Garden St"),
        ]
        
        for name, phone, email, address in customers:
            existing = session.query(Customer).filter_by(phone=phone).first()
            if not existing:
                customer = Customer(
                    name=name,
                    phone=phone,
                    email=email,
                    address=address
                )
                session.add(customer)
                print(f"✅ Added customer: {name}")
        
        session.commit()
        print("\n✅ Sample data added successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()