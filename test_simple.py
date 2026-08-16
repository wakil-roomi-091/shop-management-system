"""
Simple Test
Just check if the products module can be found
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Current Python path:")
for p in sys.path:
    print(f"  {p}")

print("\nChecking if products folder exists...")
products_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules", "products")
print(f"Products path: {products_path}")
print(f"Exists: {os.path.exists(products_path)}")

if os.path.exists(products_path):
    print(f"Contents of products folder:")
    for item in os.listdir(products_path):
        print(f"  - {item}")

print("\nTrying to import modules.products...")
try:
    import modules.products
    print(f"✅ modules.products imported!")
    print(f"   Location: {modules.products.__file__}")
except ImportError as e:
    print(f"❌ modules.products import failed: {e}")

print("\nTrying to import from modules.products...")
try:
    from modules.products import AddProductDialog
    print("✅ AddProductDialog imported successfully!")
except ImportError as e:
    print(f"❌ AddProductDialog import failed: {e}")