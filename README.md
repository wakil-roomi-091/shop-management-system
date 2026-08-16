# 🏪 Shop Management System

A complete offline retail shop management system with Point of Sale (POS), inventory management, sales reports, expense tracking, and role-based access control.


## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [User Roles](#user-roles)
- [Printing Support](#printing-support)
- [Tech Stack](#tech-stack)
- [Contact](#contact)

## 📖 Overview

The **Shop Management System** is a comprehensive desktop application designed for retail businesses to manage daily operations efficiently. Built with Python and PySide6, it provides a modern, responsive interface that works offline — ideal for shops with limited or no internet connectivity.

### 🎯 Key Benefits

- **100% Offline** — no internet required, data stays on your computer
- **User-Friendly** — intuitive interface with a clean design
- **Role-Based Access** — Admin, Manager, Cashier, and Data Entry roles
- **Print Ready** — print receipts and reports on any printer
- **Data Security** — automatic backups and user authentication
- **Cost Effective** — a free, open-source alternative to expensive POS systems

## ✨ Features

### 🛒 Point of Sale (POS)
- Quick product search by name, barcode, or category
- Cart management with quantity adjustments
- Discount support (percentage or fixed amount)
- Multiple payment methods (Cash, Card, etc.)
- Professional receipt printing
- Auto-invoice generation

### 📦 Inventory Management
- Add, edit, and delete products
- Stock tracking and alerts
- Category management
- Barcode support
- Purchase price and selling price tracking
- Profit margin calculation

### 📊 Reports & Analytics
- **Daily Sales Report** — view sales by day with summaries
- **Monthly Report** — track performance over time
- **Profit Analysis** — see profit margins per transaction
- **Export to PDF** — professional report generation
- **Print Reports** — print directly from the app

### 👥 Customer Management
- Customer database with purchase history
- Track customer spending
- Loyalty program support
- Quick customer lookup

### 💰 Expense Tracking
- Record daily expenses
- Categorize expenses
- Track expense reports
- Profit vs. expense analysis

### 👤 Role-Based Access Control

| Role | Access Level |
|------|--------------|
| **Admin** | Full system access, user management, settings |
| **Manager** | Sales, products, customers, reports, expenses |
| **Cashier** | Sales only |
| **Data Entry** | Product management only |

### 💾 Backup & Restore
- One-click database backup
- Auto-backup on application close
- Restore from backup files
- Backup history management

### 🔧 Settings
- Company information (name, address, phone)
- Currency symbol customization
- Receipt footer text
- Tax settings
- Printer configuration

## ⚙️ Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Steps

```bash
# Clone the repository
git clone https://github.com/<your-username>/shop-management-system.git
cd shop-management-system

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

```bash
python main.py
```

On first launch, you'll be prompted to set up your company details and create an admin account. From there you can add products, set up categories, and start processing sales.

## 👤 User Roles

| Role | Access Level |
|------|--------------|
| **Admin** | Full system access, user management, settings |
| **Manager** | Sales, products, customers, reports, expenses |
| **Cashier** | Sales only |
| **Data Entry** | Product management only |

## 🖨️ Printing Support

The system supports both thermal receipt printers and regular office printers.

### Thermal Printer Support
- ESC/POS protocol support
- USB and network printer connectivity
- Auto-detection of connected printers
- Configurable printer settings

### Regular Printer Support (HP LaserJet, Inkjet, etc.)
- **Receipt Printing** — professional HTML-based receipts on A4 paper
- **Report Printing** — daily and monthly reports with full formatting
- **Print Dialog** — full printer selection and configuration
- **PDF Export** — save receipts and reports as PDF files

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| GUI Framework | PySide6 (Qt for Python) |
| ORM / Database Layer | SQLAlchemy 2.0+ |
| Database | SQLite *(update if you're using something else)* |
| PDF Generation | *(add the library you're using, e.g. ReportLab)* |


## 📧 Contact

**Abdul Wakil** — *(wakila971@gmail.com)*
Project Link: *(add your GitHub repo URL)*