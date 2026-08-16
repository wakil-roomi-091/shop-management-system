"""
Database Models
Defines all database tables using SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class Category(Base):
    """Product Categories Table"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>"


class Product(Base):
    """Products Table"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    buying_price = Column(Float, nullable=False, default=0.0)
    selling_price = Column(Float, nullable=False, default=0.0)
    current_stock = Column(Integer, nullable=False, default=0)
    min_stock_level = Column(Integer, nullable=False, default=5)
    barcode = Column(String(50), unique=True, nullable=True)
    description = Column(Text, nullable=True)
    unit = Column(String(20), default='units')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
    inventory_history = relationship("InventoryHistory", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(name='{self.name}', price={self.selling_price}, stock={self.current_stock})>"
    
    @property
    def profit_margin(self):
        """Calculate profit margin per unit"""
        return self.selling_price - self.buying_price
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.current_stock <= self.min_stock_level
    
    @property
    def stock_status(self):
        """Get stock status: 'Normal', 'Warning', or 'Critical'"""
        if self.current_stock > self.min_stock_level:
            return "Normal"
        elif self.current_stock == self.min_stock_level:
            return "Warning"
        else:
            return "Critical"


class Customer(Base):
    """Customers Table - Track customer information"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    total_purchases = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    last_purchase_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sales = relationship("Sale", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(name='{self.name}', phone='{self.phone}')>"


class User(Base):
    """Users Table - Authentication and roles"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='cashier')
    full_name = Column(String(100), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sales = relationship("Sale", back_populates="user")
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class Sale(Base):
    """Sales Table - Main sales record"""
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(20), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    total_amount = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, nullable=False, default=0.0)
    discount_percentage = Column(Float, nullable=False, default=0.0)
    net_amount = Column(Float, nullable=False, default=0.0)
    cash_received = Column(Float, nullable=False, default=0.0)
    change_returned = Column(Float, nullable=False, default=0.0)
    profit = Column(Float, nullable=False, default=0.0)
    sale_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="sales")
    
    def __repr__(self):
        return f"<Sale(invoice='{self.invoice_number}', net={self.net_amount})>"


class SaleItem(Base):
    """Sale Items Table - Individual items in a sale"""
    __tablename__ = 'sale_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_per_product = Column(Float, nullable=False, default=0.0)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
    
    def __repr__(self):
        return f"<SaleItem(product_id={self.product_id}, qty={self.quantity})>"


class InventoryHistory(Base):
    """Inventory History Table - Tracks all stock changes"""
    __tablename__ = 'inventory_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    change_type = Column(String(20), nullable=False)  # 'ADD', 'REMOVE', 'SOLD', 'ADJUST'
    quantity_change = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="inventory_history")
    
    def __repr__(self):
        return f"<InventoryHistory(product_id={self.product_id}, change={self.quantity_change})>"


class Expense(Base):
    """Expenses Table - Track business expenses"""
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)  # Rent, Salary, Utilities, etc.
    description = Column(String(200), nullable=True)
    amount = Column(Float, nullable=False)
    expense_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Expense(category='{self.category}', amount={self.amount})>"


class Setting(Base):
    """Settings Table - Store application settings"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Setting(key='{self.key}', value='{self.value}')>"