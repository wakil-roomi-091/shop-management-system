"""
Modules Package
Contains all application modules
"""

from .settings import SettingsWindow
from .products import ProductsWindow, AddProductDialog
from .sales import SalesWindow
from .reports import ReportsWindow
from .dashboard import DashboardWindow
from .customers import CustomersWindow
from .backup import BackupWindow
from .usermanager import UserManagerWindow

__all__ = [
    'SettingsWindow',
    'ProductsWindow',
    'AddProductDialog',
    'SalesWindow',
    'ReportsWindow',
    'DashboardWindow',
    'CustomersWindow',
    'BackupWindow',
    'UserManagerWindow'
]