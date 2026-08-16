"""
Add/Edit Product Dialog
Form for adding or editing products
"""

import sys
import os
import random
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QPushButton,
    QMessageBox, QGroupBox, QScrollArea, QFrame,
    QApplication, QWidget
)
from PySide6.QtCore import Qt

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import DatabaseManager, Product, Category


# ===== CATEGORY KEYWORD MAPPING =====
KEYWORD_MAP = {
    'charger': 'Electronics',
    'cable': 'Electronics',
    'phone': 'Electronics',
    'laptop': 'Electronics',
    'computer': 'Electronics',
    'tv': 'Electronics',
    'television': 'Electronics',
    'monitor': 'Electronics',
    'keyboard': 'Electronics',
    'mouse': 'Electronics',
    'printer': 'Electronics',
    'scanner': 'Electronics',
    'router': 'Electronics',
    'modem': 'Electronics',
    'headphone': 'Electronics',
    'earphone': 'Electronics',
    'speaker': 'Electronics',
    'camera': 'Electronics',
    'smartwatch': 'Electronics',
    'tablet': 'Electronics',
    'gaming': 'Electronics',
    'console': 'Electronics',
    'shirt': 'Clothing',
    'pants': 'Clothing',
    'jeans': 'Clothing',
    'jacket': 'Clothing',
    'coat': 'Clothing',
    'sweater': 'Clothing',
    'hoodie': 'Clothing',
    'dress': 'Clothing',
    'skirt': 'Clothing',
    'blouse': 'Clothing',
    'suit': 'Clothing',
    'shoe': 'Footwear',
    'sneaker': 'Footwear',
    'boot': 'Footwear',
    'sandal': 'Footwear',
    'slipper': 'Footwear',
    'rice': 'Groceries',
    'wheat': 'Groceries',
    'flour': 'Groceries',
    'sugar': 'Groceries',
    'salt': 'Groceries',
    'oil': 'Groceries',
    'ghee': 'Groceries',
    'butter': 'Groceries',
    'milk': 'Groceries',
    'bread': 'Groceries',
    'cake': 'Groceries',
    'egg': 'Groceries',
    'chicken': 'Groceries',
    'mutton': 'Groceries',
    'beef': 'Groceries',
    'fish': 'Groceries',
    'apple': 'Groceries',
    'banana': 'Groceries',
    'mango': 'Groceries',
    'orange': 'Groceries',
    'tomato': 'Groceries',
    'potato': 'Groceries',
    'onion': 'Groceries',
    'garlic': 'Groceries',
    'ginger': 'Groceries',
    'shampoo': 'Personal Care',
    'conditioner': 'Personal Care',
    'soap': 'Personal Care',
    'body wash': 'Personal Care',
    'lotion': 'Personal Care',
    'cream': 'Personal Care',
    'deodorant': 'Personal Care',
    'perfume': 'Personal Care',
    'face wash': 'Personal Care',
    'moisturizer': 'Personal Care',
    'sunscreen': 'Personal Care',
    'toothpaste': 'Oral Care',
    'toothbrush': 'Oral Care',
    'mouthwash': 'Oral Care',
    'floss': 'Oral Care',
    'detergent': 'Household',
    'bleach': 'Household',
    'cleaner': 'Household',
    'sofa': 'Furniture',
    'chair': 'Furniture',
    'table': 'Furniture',
    'bed': 'Furniture',
    'wardrobe': 'Furniture',
    'cabinet': 'Furniture',
    'shelf': 'Furniture',
    'desk': 'Furniture',
    'pillow': 'Bedding',
    'blanket': 'Bedding',
    'sheet': 'Bedding',
    'quilt': 'Bedding',
    'towel': 'Bathroom',
    'robe': 'Bathroom',
    'mat': 'Bathroom',
    'plant': 'Garden',
    'pot': 'Kitchenware',
    'pan': 'Kitchenware',
    'knife': 'Kitchenware',
    'spatula': 'Kitchenware',
    'ladle': 'Kitchenware',
    'hammer': 'Tools',
    'screwdriver': 'Tools',
    'wrench': 'Tools',
    'pliers': 'Tools',
    'saw': 'Tools',
    'drill': 'Tools',
    'book': 'Books',
    'novel': 'Books',
    'biography': 'Books',
    'history': 'Books',
    'science': 'Books',
    'pen': 'Stationery',
    'pencil': 'Stationery',
    'notebook': 'Stationery',
    'marker': 'Stationery',
    'highlighter': 'Stationery',
    'stapler': 'Stationery',
    'glue': 'Stationery',
    'scissors': 'Stationery',
    'ruler': 'Stationery',
    'watch': 'Watches',
    'sunglass': 'Sunglasses',
    'toy': 'Toys',
    'doll': 'Toys',
    'lego': 'Toys',
    'puzzle': 'Toys',
    'board game': 'Games',
    'card game': 'Games',
    'chess': 'Games',
    'ball': 'Sports',
    'cricket': 'Sports',
    'bat': 'Sports',
    'football': 'Sports',
    'basketball': 'Sports',
    'tennis': 'Sports',
    'badminton': 'Sports',
    'tent': 'Outdoor',
    'backpack': 'Outdoor',
    'camping': 'Outdoor',
    'hiking': 'Outdoor',
    'car': 'Automotive',
    'auto': 'Automotive',
    'motorcycle': 'Automotive',
    'bike': 'Automotive',
    'pet': 'Pet Supplies',
    'dog': 'Pet Supplies',
    'cat': 'Pet Supplies',
    'bird': 'Pet Supplies',
    'medicine': 'Health',
    'vitamin': 'Health',
    'supplement': 'Health',
    'first aid': 'Health',
    'guitar': 'Musical Instruments',
    'piano': 'Musical Instruments',
    'keyboard': 'Musical Instruments',
    'drums': 'Musical Instruments',
    'violin': 'Musical Instruments',
    'flute': 'Musical Instruments',
    'gift': 'Gifts',
    'necklace': 'Jewelry',
    'ring': 'Jewelry',
    'earring': 'Jewelry',
    'bracelet': 'Jewelry',
    'bangle': 'Jewelry',
    'handbag': 'Fashion Accessories',
    'purse': 'Fashion Accessories',
    'wallet': 'Fashion Accessories',
    'belt': 'Fashion Accessories',
    'scarf': 'Fashion Accessories',
    'balloon': 'Party Supplies',
    'confetti': 'Party Supplies',
    'banner': 'Party Supplies',
}


class AddProductDialog(QDialog):
    """Dialog for adding or editing products"""
    
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.product_id = product_id
        self.is_edit = product_id is not None
        
        self.setWindowTitle("Edit Product" if self.is_edit else "Add Product")
        
        # Apply styles
        from ui.styles import get_app_style
        self.setStyleSheet(get_app_style())
        
        self.setup_ui()
        
        if self.is_edit:
            self.load_product_data()
        
        self.center_on_screen()
    
    def center_on_screen(self):
        screen = self.screen().availableGeometry() if self.screen() else None
        if screen:
            self.resize(min(560, int(screen.width() * 0.90)), min(700, int(screen.height() * 0.90)))
            x = screen.x() + (screen.width() - self.width()) // 2
            y = screen.y() + (screen.height() - self.height()) // 2
            self.move(x, y)
    
    def setup_ui(self):
        """Setup the dialog interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(20, 16, 20, 16)
        
        # Title
        title = QLabel("Edit Product" if self.is_edit else "Add Product")
        title.setObjectName("header")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Fill in the product details below")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Scroll Area for Form Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(4, 4, 4, 4)

        # Form Group
        form_group = QGroupBox()
        form_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                background-color: #ffffff;
                padding: 20px;
                margin-top: 0px;
            }
        """)
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Product Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")
        self.name_input.setMinimumHeight(40)
        self.name_input.textChanged.connect(self.suggest_category)
        form_layout.addRow("Product Name *:", self.name_input)
        
        # Category - Editable (can type new category)
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(40)
        self.category_combo.setEditable(True)
        self.category_combo.setInsertPolicy(QComboBox.NoInsert)
        self.category_combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 6px 12px;
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #0f172a;
                selection-background-color: #eff6ff;
                selection-color: #0f172a;
            }
        """)
        self.load_categories()
        form_layout.addRow("Category *:", self.category_combo)
        
        # Barcode with Generate button
        barcode_layout = QHBoxLayout()
        barcode_layout.setSpacing(8)
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Enter barcode (optional)")
        self.barcode_input.setMinimumHeight(40)
        barcode_layout.addWidget(self.barcode_input)
        
        generate_btn = QPushButton("Generate")
        generate_btn.setObjectName("secondary")
        generate_btn.setFixedHeight(40)
        generate_btn.setFixedWidth(90)
        generate_btn.clicked.connect(self.generate_barcode)
        barcode_layout.addWidget(generate_btn)
        
        form_layout.addRow("Barcode:", barcode_layout)
        
        # Prices
        price_label = QLabel("Pricing")
        price_label.setStyleSheet("font-weight: 600; font-size: 15px; color: #0f172a;")
        form_layout.addRow(price_label)
        
        self.buying_price = QDoubleSpinBox()
        self.buying_price.setRange(0, 999999.99)
        self.buying_price.setPrefix("Rs ")
        self.buying_price.setSingleStep(10)
        self.buying_price.setMinimumHeight(40)
        form_layout.addRow("Buying Price *:", self.buying_price)
        
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setRange(0, 999999.99)
        self.selling_price.setPrefix("Rs ")
        self.selling_price.setSingleStep(10)
        self.selling_price.setMinimumHeight(40)
        form_layout.addRow("Selling Price *:", self.selling_price)
        
        # Stock with Unit Selection
        stock_label = QLabel("Stock Management")
        stock_label.setStyleSheet("font-weight: 600; font-size: 15px; color: #0f172a;")
        form_layout.addRow(stock_label)
        
        # Unit dropdown
        self.unit_combo = QComboBox()
        self.unit_combo.setMinimumHeight(40)
        self.unit_combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 6px 12px;
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #0f172a;
                selection-background-color: #eff6ff;
                selection-color: #0f172a;
            }
        """)
        units = ['Units', 'Kilos (kg)', 'Grams (g)', 'Liters (L)', 'Milliliters (ml)', 
                 'Meters (m)', 'Centimeters (cm)', 'Pieces', 'Pairs', 'Dozens']
        for unit in units:
            self.unit_combo.addItem(unit)
        form_layout.addRow("Unit:", self.unit_combo)
        
        # Stock input with unit label
        stock_layout = QHBoxLayout()
        stock_layout.setSpacing(8)
        
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 999999)
        self.stock_input.setMinimumHeight(40)
        self.stock_input.setStyleSheet("font-size: 14px;")
        stock_layout.addWidget(self.stock_input)
        
        self.stock_unit_label = QLabel("units")
        self.stock_unit_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #64748b;")
        stock_layout.addWidget(self.stock_unit_label)
        stock_layout.addStretch()
        
        form_layout.addRow("Current Stock:", stock_layout)
        
        self.min_stock_input = QSpinBox()
        self.min_stock_input.setRange(0, 9999)
        self.min_stock_input.setMinimumHeight(40)
        self.min_stock_input.setStyleSheet("font-size: 14px;")
        form_layout.addRow("Minimum Stock Level:", self.min_stock_input)
        
        # Connect unit change to update label
        self.unit_combo.currentTextChanged.connect(self.update_unit_label)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Enter product description (optional)")
        form_layout.addRow("Description:", self.description_input)
        
        form_group.setLayout(form_layout)
        scroll_layout.addWidget(form_group)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Product")
        save_btn.setObjectName("success")
        save_btn.setMinimumHeight(45)
        save_btn.setMinimumWidth(150)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 30px;
                font-size: 15px;
                font-weight: 600;
                border-radius: 10px;
            }
        """)
        save_btn.clicked.connect(self.save_product)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                font-size: 15px;
                font-weight: 500;
                border-radius: 10px;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def update_unit_label(self, unit):
        """Update stock unit label based on selected unit"""
        unit_map = {
            'Units': 'units',
            'Kilos (kg)': 'kg',
            'Grams (g)': 'g',
            'Liters (L)': 'L',
            'Milliliters (ml)': 'ml',
            'Meters (m)': 'm',
            'Centimeters (cm)': 'cm',
            'Pieces': 'pieces',
            'Pairs': 'pairs',
            'Dozens': 'dozen'
        }
        self.stock_unit_label.setText(unit_map.get(unit, 'units'))
    
    def load_categories(self):
        """Load categories into combo box"""
        session = self.db.get_session()
        try:
            categories = session.query(Category).order_by(Category.name).all()
            self.category_combo.clear()
            for category in categories:
                self.category_combo.addItem(category.name, category.id)
        except Exception as e:
            print(f"Error loading categories: {e}")
        finally:
            session.close()
    
    def load_product_data(self):
        """Load product data for editing"""
        session = self.db.get_session()
        try:
            product = session.query(Product).filter_by(id=self.product_id).first()
            if product:
                self.name_input.setText(product.name)
                
                # Set category
                index = self.category_combo.findData(product.category_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                
                self.barcode_input.setText(product.barcode or "")
                self.buying_price.setValue(product.buying_price)
                self.selling_price.setValue(product.selling_price)
                self.stock_input.setValue(product.current_stock)
                self.min_stock_input.setValue(product.min_stock_level)
                self.description_input.setText(product.description or "")
                
                # Set unit if exists
                if product.unit:
                    for i in range(self.unit_combo.count()):
                        if product.unit in self.unit_combo.itemText(i).lower():
                            self.unit_combo.setCurrentIndex(i)
                            break
            else:
                QMessageBox.warning(self, "Error", "Product not found!")
                self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load product: {str(e)}")
        finally:
            session.close()
    
    def generate_barcode(self):
        """Generate a random barcode"""
        barcode = f"{random.randint(10000000, 99999999)}{random.randint(1000, 9999)}"
        self.barcode_input.setText(barcode)
    
    def suggest_category(self):
        """Auto-suggest category based on product name"""
        name = self.name_input.text().strip().lower()
        
        if not name:
            return
        
        # Check for direct keyword matches
        for keyword, category in KEYWORD_MAP.items():
            if keyword in name:
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemText(i).lower() == category.lower():
                        self.category_combo.setCurrentIndex(i)
                        return
        
        # If no exact match, try each word in product name
        words = name.split()
        for word in words:
            if len(word) > 2:
                for keyword, category in KEYWORD_MAP.items():
                    if word in keyword or keyword in word:
                        for i in range(self.category_combo.count()):
                            if self.category_combo.itemText(i).lower() == category.lower():
                                self.category_combo.setCurrentIndex(i)
                                return
    
    def save_product(self):
        """Save product to database"""
        # Validate inputs
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Product name is required!")
            return
        
        # Get category - either from combo or from text input
        category_text = self.category_combo.currentText().strip()
        
        if not category_text:
            QMessageBox.warning(self, "Validation Error", "Please select or enter a category!")
            return
        
        # Check if category exists, if not create it
        session = self.db.get_session()
        try:
            category = session.query(Category).filter_by(name=category_text).first()
            if not category:
                # Create new category
                category = Category(name=category_text)
                session.add(category)
                session.flush()
                print(f"✅ New category created: {category_text}")
            
            category_id = category.id
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Could not process category: {str(e)}")
            return
        finally:
            session.close()
        
        if self.buying_price.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Buying price must be greater than 0!")
            return
        
        if self.selling_price.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Selling price must be greater than 0!")
            return
        
        if self.selling_price.value() < self.buying_price.value():
            reply = QMessageBox.question(
                self,
                "Price Warning",
                f"Selling price (Rs{self.selling_price.value():,.2f}) is less than buying price (Rs{self.buying_price.value():,.2f}).\nThis will result in a loss on each sale.\nContinue anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        session = self.db.get_session()
        try:
            # Get unit
            unit_text = self.unit_combo.currentText()
            # Extract just the unit name without parentheses
            if '(' in unit_text and ')' in unit_text:
                unit = unit_text.split('(')[1].split(')')[0]
            else:
                unit = unit_text.lower()
            
            # Prepare product data
            product_data = {
                'name': self.name_input.text().strip(),
                'category_id': category_id,
                'barcode': self.barcode_input.text().strip() or None,
                'buying_price': self.buying_price.value(),
                'selling_price': self.selling_price.value(),
                'current_stock': self.stock_input.value(),
                'min_stock_level': self.min_stock_input.value(),
                'description': self.description_input.toPlainText().strip() or None,
                'unit': unit
            }
            
            if self.is_edit:
                # Update existing product
                product = session.query(Product).filter_by(id=self.product_id).first()
                if product:
                    for key, value in product_data.items():
                        setattr(product, key, value)
                    session.commit()
                    QMessageBox.information(self, "Success", "Product updated successfully!")
                    self.accept()
            else:
                # Create new product
                product = Product(**product_data)
                session.add(product)
                session.commit()
                QMessageBox.information(self, "Success", f"Product '{product.name}' added successfully!")
                self.accept()
                
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Could not save product: {str(e)}")
        finally:
            session.close()