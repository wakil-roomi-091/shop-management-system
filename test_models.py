"""
Test Models
Quick check to ensure models are working
"""

from database.models import Category, Product, Sale, SaleItem, InventoryHistory, Setting

print("✅ All models imported successfully!")
print(f"📦 Category: {Category.__tablename__}")
print(f"📦 Product: {Product.__tablename__}")
print(f"📦 Sale: {Sale.__tablename__}")
print(f"📦 SaleItem: {SaleItem.__tablename__}")
print(f"📦 InventoryHistory: {InventoryHistory.__tablename__}")
print(f"📦 Setting: {Setting.__tablename__}")
print("\n🎉 Models are ready! No errors found.")