"""
UI Styles - Clean Professional
Only uses Qt-supported CSS properties
"""

def get_app_style():
    """Return the professional application stylesheet"""
    return """
    /* ============================================
       GLOBAL STYLES
       ============================================ */
    * {
        font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    }
    
    QMainWindow, QWidget {
        background-color: #f1f5f9;
        color: #0f172a;
    }
    
    /* ============================================
       HEADERS
       ============================================ */
    QLabel#header {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
        padding: 8px 0;
        letter-spacing: -0.3px;
    }
    
    QLabel#title {
        font-size: 20px;
        font-weight: 600;
        color: #0f172a;
    }
    
    QLabel#subtitle {
        font-size: 14px;
        color: #64748b;
        font-weight: 400;
    }
    
    /* ============================================
       CARDS / GROUP BOXES
       ============================================ */
    QGroupBox {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin-top: 12px;
        padding: 20px 20px 20px 20px;
        font-size: 14px;
        font-weight: 600;
        color: #0f172a;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 10px 0 10px;
        background-color: #ffffff;
        font-size: 14px;
        font-weight: 600;
        color: #0f172a;
    }
    
    /* ============================================
       BUTTONS - Clean Professional
       ============================================ */
    QPushButton {
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        color: #ffffff;
        background-color: #0f172a;
        min-height: 18px;
        min-width: 80px;
    }
    
    QPushButton:hover {
        background-color: #1e293b;
    }
    
    QPushButton:pressed {
        background-color: #334155;
    }
    
    QPushButton#primary {
        background-color: #3b82f6;
    }
    QPushButton#primary:hover {
        background-color: #2563eb;
    }
    
    QPushButton#success {
        background-color: #22c55e;
    }
    QPushButton#success:hover {
        background-color: #16a34a;
    }
    
    QPushButton#danger {
        background-color: #ef4444;
    }
    QPushButton#danger:hover {
        background-color: #dc2626;
    }
    
    QPushButton#warning {
        background-color: #f59e0b;
    }
    QPushButton#warning:hover {
        background-color: #d97706;
    }
    
    QPushButton#secondary {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #e2e8f0;
    }
    QPushButton#secondary:hover {
        background-color: #f8fafc;
        border-color: #94a3b8;
    }
    
    /* ============================================
       INPUT FIELDS
       ============================================ */
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        padding: 10px 14px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background-color: #ffffff;
        font-size: 14px;
        min-height: 18px;
        color: #0f172a;
        selection-background-color: #3b82f6;
    }
    
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, 
    QDoubleSpinBox:focus, QComboBox:focus {
        border: 2px solid #3b82f6;
        background-color: #ffffff;
    }
    
    QLineEdit::placeholder {
        color: #94a3b8;
    }
    
    /* Search Input */
    QLineEdit#search {
        padding: 12px 16px;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        font-size: 14px;
        min-height: 36px;
        background-color: #ffffff;
    }
    
    QLineEdit#search:focus {
        border: 2px solid #3b82f6;
    }
    
    /* ============================================
       TABLES
       ============================================ */
    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 4px;
        font-size: 13px;
        gridline-color: #f1f5f9;
    }
    
    QTableWidget::item {
        padding: 12px 10px;
        border-bottom: 1px solid #f1f5f9;
    }
    
    QTableWidget::item:selected {
        background-color: #eff6ff;
        color: #0f172a;
    }
    
    QHeaderView::section {
        background-color: #f8fafc;
        color: #475569;
        padding: 12px 10px;
        border: none;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    /* ============================================
       COMBOBOX
       ============================================ */
    QComboBox {
        padding: 10px 14px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background-color: #ffffff;
        font-size: 14px;
        min-height: 18px;
        color: #0f172a;
    }
    
    QComboBox::drop-down {
        border: none;
        padding-right: 10px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #64748b;
        margin-right: 5px;
    }
    
    QComboBox:hover {
        border-color: #94a3b8;
    }
    
    QComboBox:focus {
        border: 2px solid #3b82f6;
    }
    
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 4px;
        selection-background-color: #eff6ff;
        selection-color: #0f172a;
    }
    
    /* ============================================
       SCROLLBARS
       ============================================ */
    QScrollBar:vertical {
        background-color: transparent;
        width: 6px;
        border-radius: 3px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #cbd5e1;
        border-radius: 3px;
        min-height: 30px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #94a3b8;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        background-color: transparent;
        height: 6px;
        border-radius: 3px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #cbd5e1;
        border-radius: 3px;
        min-width: 30px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #94a3b8;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    /* ============================================
       STATUS BAR
       ============================================ */
    QStatusBar {
        background-color: #ffffff;
        color: #475569;
        padding: 6px 16px;
        font-size: 13px;
        border-top: 1px solid #e2e8f0;
    }
    
    QStatusBar QLabel {
        color: #475569;
    }
    
    /* ============================================
       TABS
       ============================================ */
    QTabWidget::pane {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background-color: #ffffff;
        padding: 16px;
        margin-top: -1px;
    }
    
    QTabBar::tab {
        background-color: transparent;
        padding: 10px 18px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        color: #64748b;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #e2e8f0;
        border-bottom: none;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #f1f5f9;
        color: #0f172a;
    }
    
    /* ============================================
       LABELS
       ============================================ */
    QLabel {
        font-size: 14px;
        color: #0f172a;
    }
    
    QLabel#label_bold {
        font-weight: 600;
        font-size: 14px;
        color: #0f172a;
    }
    
    QLabel#success_text {
        color: #22c55e;
        font-weight: 500;
    }
    
    QLabel#warning_text {
        color: #f59e0b;
        font-weight: 500;
    }
    
    QLabel#danger_text {
        color: #ef4444;
        font-weight: 500;
    }
    
    QLabel#info_text {
        color: #3b82f6;
        font-weight: 500;
    }
    
    /* ============================================
       CHECKBOXES
       ============================================ */
    QCheckBox, QRadioButton {
        font-size: 14px;
        color: #0f172a;
        spacing: 8px;
    }
    
    QCheckBox::indicator, QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #e2e8f0;
        border-radius: 4px;
        background-color: #ffffff;
    }
    
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #3b82f6;
        border-color: #3b82f6;
    }
    
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border-color: #3b82f6;
    }
    
    /* ============================================
       SPINBOX
       ============================================ */
    QSpinBox, QDoubleSpinBox {
        padding: 10px 14px;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background-color: #ffffff;
        font-size: 14px;
        min-height: 18px;
        color: #0f172a;
    }
    
    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 2px solid #3b82f6;
    }
    
    QSpinBox::up-button, QDoubleSpinBox::up-button {
        border-top-right-radius: 8px;
        width: 20px;
    }
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        border-bottom-right-radius: 8px;
        width: 20px;
    }
    
    /* ============================================
       MESSAGE BOX
       ============================================ */
    QMessageBox {
        background-color: #ffffff;
        font-size: 14px;
    }
    
    QMessageBox QPushButton {
        min-width: 80px;
        min-height: 32px;
        padding: 8px 16px;
        border-radius: 8px;
    }
    
    /* ============================================
       DIALOG
       ============================================ */
    QDialog {
        background-color: #f8fafc;
    }
    
    QDialog QPushButton {
        min-width: 100px;
        padding: 10px 24px;
        border-radius: 8px;
    }
    
    /* ============================================
       PROGRESS BAR
       ============================================ */
    QProgressBar {
        border: none;
        border-radius: 6px;
        background-color: #f1f5f9;
        height: 6px;
        text-align: center;
    }
    
    QProgressBar::chunk {
        background-color: #3b82f6;
        border-radius: 6px;
    }
    
    /* ============================================
       TOOL TIPS
       ============================================ */
    QToolTip {
        background-color: #0f172a;
        color: #ffffff;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 12px;
        border: none;
    }
    
    /* ============================================
       MENU BAR
       ============================================ */
    QMenuBar {
        background-color: #ffffff;
        color: #0f172a;
        padding: 4px 12px;
        font-size: 14px;
        font-weight: 500;
        border-bottom: 1px solid #e2e8f0;
    }
    
    QMenuBar::item {
        padding: 8px 16px;
        border-radius: 6px;
    }
    
    QMenuBar::item:selected {
        background-color: #f1f5f9;
    }
    
    QMenu {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 6px;
        font-size: 13px;
    }
    
    QMenu::item {
        padding: 8px 20px;
        border-radius: 6px;
    }
    
    QMenu::item:selected {
        background-color: #eff6ff;
        color: #0f172a;
    }
    """