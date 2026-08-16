"""
Data Validators
Input validation for all modules
"""

import re
from datetime import datetime


class Validator:
    """Common validation methods"""
    
    @staticmethod
    def validate_product_name(name):
        """Validate product name"""
        if not name or not name.strip():
            return False, "Product name is required"
        if len(name.strip()) < 2:
            return False, "Product name must be at least 2 characters"
        if len(name.strip()) > 200:
            return False, "Product name cannot exceed 200 characters"
        return True, ""
    
    @staticmethod
    def validate_barcode(barcode):
        """Validate barcode"""
        if not barcode:
            return True, ""  # Barcode is optional
        if not barcode.isdigit():
            return False, "Barcode must contain only numbers"
        if len(barcode) < 8:
            return False, "Barcode must be at least 8 digits"
        return True, ""
    
    @staticmethod
    def validate_price(price):
        """Validate price"""
        if price < 0:
            return False, "Price cannot be negative"
        if price > 999999.99:
            return False, "Price exceeds maximum allowed"
        return True, ""
    
    @staticmethod
    def validate_stock(quantity):
        """Validate stock quantity"""
        if quantity < 0:
            return False, "Stock cannot be negative"
        if quantity > 999999:
            return False, "Stock exceeds maximum allowed"
        return True, ""
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number"""
        if not phone:
            return True, ""  # Phone is optional
        # Remove spaces, dashes, plus sign
        clean = re.sub(r'[\s\-\(\)\+]', '', phone)
        if not clean.isdigit():
            return False, "Phone must contain only numbers, spaces, or dashes"
        if len(clean) < 7:
            return False, "Phone must be at least 7 digits"
        if len(clean) > 15:
            return False, "Phone cannot exceed 15 digits"
        return True, ""
    
    @staticmethod
    def validate_email(email):
        """Validate email"""
        if not email:
            return True, ""  # Email is optional
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Please enter a valid email address"
        return True, ""
    
    @staticmethod
    def validate_username(username):
        """Validate username"""
        if not username or not username.strip():
            return False, "Username is required"
        if len(username.strip()) < 3:
            return False, "Username must be at least 3 characters"
        if len(username.strip()) > 50:
            return False, "Username cannot exceed 50 characters"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        return True, ""
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        # Optional: Add more password requirements
        return True, ""
    
    @staticmethod
    def validate_selling_price_against_buying(selling_price, buying_price):
        """Validate selling price against buying price"""
        if selling_price < buying_price:
            return False, f"Selling price ({selling_price}) is less than buying price ({buying_price}). This will result in loss."
        return True, ""


