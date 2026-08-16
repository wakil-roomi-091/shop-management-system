# 🏪 Shop Management System

A complete offline retail shop management system with Point of Sale (POS), inventory management, sales reports, expenses tracking, and role-based access control.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.6%2B-green.svg)](https://doc.qt.io/qtforpython-6/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red.svg)](https://www.sqlalchemy.org/)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [User Roles](#user-roles)
- [Printing Support](#printing-support)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## 📖 Overview

The **Shop Management System** is a comprehensive desktop application designed for retail businesses to manage daily operations efficiently. Built with Python and PySide6, it provides a modern, responsive interface that works offline - perfect for shops with limited or no internet connectivity.

### 🎯 Key Benefits
- **100% Offline** - No internet required, data stays on your computer
- **User-Friendly** - Intuitive interface with clean design
- **Role-Based Access** - Admin, Manager, Cashier, and Data Entry roles
- **Print Ready** - Print receipts and reports on any printer
- **Data Security** - Automatic backups and user authentication
- **Cost Effective** - Free and open-source alternative to expensive POS systems

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
- **Daily Sales Report** - View sales by day with summaries
- **Monthly Report** - Track performance over time
- **Profit Analysis** - See profit margins per transaction
- **Export to PDF** - Professional report generation
- **Print Reports** - Print directly from the app

### 👥 Customer Management
- Customer database with purchase history
- Track customer spending
- Loyalty program support
- Quick customer lookup

### 💰 Expenses Tracking
- Record daily expenses
- Categorize expenses
- Track expense reports
- Profit vs expense analysis

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

## 🖨️ Printing Support

The system supports both thermal receipt printers and regular office printers:

### Thermal Printer Support
- ESC/POS protocol support
- USB and network printer connectivity
- Auto-detection of connected printers
- Configurable printer settings

### Regular Printer Support (HP LaserJet, Inkjet, etc.)
- **Receipt Printing** - Professional HTML-based receipts on A4 paper
- **Report Printing** - Daily and monthly reports with complete formatting
- **Windows Print Dialog** - Full printer selection and configuration
- **PDF Export** - Save receipts and reports as PDF files

## 📸 Screenshots

<details>
<summary>Click to view screenshots</summary>

### Dashboard