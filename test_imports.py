"""
Test Imports
Find exactly where the import fails
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("Testing imports step by step...")
print("=" * 50)

try:
    print("\n1. Testing database imports...")
    from database import DatabaseManager, Product, Category
    print("   ✅ Database imports OK")
except Exception as e:
    print(f"   ❌ Database imports FAILED: {e}")
    sys.exit(1)

try:
    print("\n2. Testing ui styles import...")
    from ui.styles import get_app_style
    print("   ✅ UI styles import OK")
except Exception as e:
    print(f"   ❌ UI styles import FAILED: {e}")
    sys.exit(1)

try:
    print("\n3. Testing add_product_dialog import...")
    from modules.products.add_product_dialog import AddProductDialog
    print("   ✅ AddProductDialog import OK")
except Exception as e:
    print(f"   ❌ AddProductDialog import FAILED: {e}")
    sys.exit(1)

try:
    print("\n4. Testing products_window import...")
    from modules.products.products_window import ProductsWindow
    print("   ✅ ProductsWindow import OK")
except Exception as e:
    print(f"   ❌ ProductsWindow import FAILED: {e}")
    sys.exit(1)

try:
    print("\n5. Testing modules.products import...")
    from modules.products import ProductsWindow, AddProductDialog
    print("   ✅ modules.products import OK")
except Exception as e:
    print(f"   ❌ modules.products import FAILED: {e}")
    sys.exit(1)

try:
    print("\n6. Testing full modules import...")
    from modules import ProductsWindow, AddProductDialog
    print("   ✅ Full modules import OK")
except Exception as e:
    print(f"   ❌ Full modules import FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("🎉 All imports successful!")
print("=" * 50)