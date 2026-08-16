"""
Add detailed superstore categories to database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from database.models import Category
from database.init_db import initialize_database


def add_categories():
    """Add detailed superstore categories"""
    db = DatabaseManager()
    session = db.get_session()
    
    categories = [
        # ===== FOOD & GROCERY =====
        'Food & Grocery',
        'Beverages (Soft Drinks, Juices, Water)',
        'Dairy & Eggs',
        'Meat & Poultry',
        'Seafood & Fish',
        'Bakery & Bread',
        'Breakfast Cereals',
        'Pasta, Rice & Noodles',
        'Canned & Packaged Foods',
        'Snacks & Chips',
        'Sweets & Chocolates',
        'Oils, Sauces & Spices',
        'Frozen Foods',
        'Organic & Health Foods',
        
        # ===== FRUITS & VEGETABLES =====
        'Fresh Fruits',
        'Fresh Vegetables',
        
        # ===== PERSONAL CARE =====
        'Shampoo & Conditioner',
        'Soap & Body Wash',
        'Deodorants & Perfumes',
        'Skincare (Face, Body, Sunscreen)',
        'Oral Care (Toothpaste, Mouthwash)',
        'Hair Care (Gel, Wax, Serums)',
        'Men\'s Grooming (Shaving, Beard)',
        'Feminine Hygiene',
        'Baby Care (Diapers, Powder, Wipes)',
        'Vitamins & Supplements',
        
        # ===== HOUSEHOLD =====
        'Cleaning Supplies (Detergent, Bleach)',
        'Kitchenware (Utensils, Cookware)',
        'Home Decor (Cushions, Rugs)',
        'Furniture (Sofas, Tables, Chairs)',
        'Bedding & Linens',
        'Storage & Organization',
        'Bathroom Accessories',
        'Garden & Outdoor',
        'Tools & Hardware',
        'Paint & Wallpaper',
        
        # ===== ELECTRONICS =====
        'Smartphones & Tablets',
        'Laptops & Computers',
        'TVs & Home Theater',
        'Audio & Headphones',
        'Cameras & Photography',
        'Gaming Consoles & Accessories',
        'Smartwatches & Wearables',
        'Computer Accessories (Keyboard, Mouse)',
        'Storage Devices (USB, Hard Drives)',
        'Networking & Routers',
        'Home Appliances (Microwave, Fridge)',
        'Small Appliances (Toaster, Blender)',
        'Lighting & Bulbs',
        'Power & Batteries',
        
        # ===== CLOTHING & FASHION =====
        'Men\'s Clothing (Shirts, Pants, Jackets)',
        'Women\'s Clothing (Dresses, Tops, Skirts)',
        'Kids\' Clothing',
        'Footwear (Shoes, Sandals, Boots)',
        'Accessories (Bags, Belts, Scarves)',
        'Jewelry & Watches',
        'Sportswear & Activewear',
        'Formal Wear & Suits',
        'Underwear & Socks',
        'Seasonal Clothing (Winter, Summer)',
        
        # ===== BEAUTY =====
        'Makeup (Foundation, Lipstick, Mascara)',
        'Nail Care',
        'Facial & Eye Care',
        'Beauty Tools (Brushes, Mirrors)',
        'Hair Styling & Treatments',
        
        # ===== HEALTH & PHARMACY =====
        'First Aid & Bandages',
        'Prescription Medicines',
        'Pain Relief (Tablets, Creams)',
        'Cold & Flu Medicines',
        'Allergy & Sinus',
        'Digestive Health (Antacids, Probiotics)',
        'Vitamins & Minerals',
        
        # ===== BABY & KIDS =====
        'Baby Food & Formula',
        'Baby Clothing',
        'Baby Toys & Activity',
        'Baby Furniture (Cribs, Strollers)',
        'Diapers & Wipes',
        
        # ===== PETS =====
        'Pet Food (Dog, Cat, Birds)',
        'Pet Accessories (Collars, Leashes)',
        'Pet Grooming',
        'Pet Toys & Treats',
        'Pet Health & Care',
        
        # ===== OFFICE & SCHOOL =====
        'Office Supplies (Paper, Pens, Staplers)',
        'Printer & Ink Cartridges',
        'Shredders & Laminators',
        'School Supplies (Notebooks, Bags)',
        'Art & Craft Supplies',
        
        # ===== AUTOMOTIVE =====
        'Car Accessories (Mats, Covers)',
        'Motor Oil & Fluids',
        'Car Cleaning & Care',
        'Batteries & Lighting',
        'Tools & Repair Kits',
        
        # ===== SPORTS & OUTDOORS =====
        'Exercise Equipment',
        'Yoga & Fitness',
        'Camping & Hiking',
        'Cycling & Accessories',
        'Swimming & Pool',
        'Team Sports (Football, Cricket, Basketball)',
        'Fishing & Hunting',
        
        # ===== BOOKS & MEDIA =====
        'Fiction Books',
        'Non-Fiction Books',
        'Children\'s Books',
        'Magazines & Newspapers',
        'E-books & Audiobooks',
        'DVDs & Blu-rays',
        
        # ===== TOYS & GAMES =====
        'Action Figures & Dolls',
        'Board Games & Puzzles',
        'Building Blocks (Lego, Magnetic)',
        'RC Cars & Drones',
        'Educational Toys',
        'Outdoor Toys (Swing, Slide)',
        
        # ===== FURNITURE & HOME IMPROVEMENT =====
        'Living Room Furniture',
        'Bedroom Furniture',
        'Kitchen Furniture',
        'Office Furniture',
        'Garden Furniture',
        'Home Improvement (Doors, Windows)',
        'Flooring & Tiles',
        
        # ===== SEASONAL =====
        'Christmas Decorations',
        'Easter Items',
        'Halloween Items',
        'New Year Items',
        'Summer (Pool, Beach, BBQ)',
        'Winter (Heaters, Coats, Warmers)',
        'Back to School',
        'Valentine\'s Day',
        
        # ===== SERVICES =====
        'Gift Cards & Vouchers',
        'Bakery Services (Cakes, Pastries)',
        'Pharmacy Consultation',
        'Gift Wrapping',
        'Delivery Services',
        
        # ===== OTHER =====
        'Miscellaneous',
        'Clearance & Sale Items',
        'Special Offers',
        'Wholesale & Bulk',
    ]
    
    try:
        for name in categories:
            existing = session.query(Category).filter_by(name=name).first()
            if not existing:
                category = Category(name=name)
                session.add(category)
                print(f"✅ Added category: {name}")
        
        session.commit()
        print(f"\n✅ All {len(categories)} categories added successfully!")
        print(f"   Total categories in database: {session.query(Category).count()}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    # First ensure database exists
    try:
        initialize_database()
        print("✅ Database initialized")
    except:
        pass
    
    add_categories()