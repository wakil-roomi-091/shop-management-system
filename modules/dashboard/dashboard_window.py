"""
Dashboard Window - Premium redesign
Modern home screen with KPI cards, sales chart, recent sales,
top-selling products, and low-stock badges.
"""

import sys
import os
from datetime import datetime, timedelta
try:
    import pytz
except ImportError:
    pytz = None

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QVariantAnimation,
)
from PySide6.QtGui import QColor, QPainter
from sqlalchemy import func
from sqlalchemy.orm import joinedload

try:
    from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

    HAS_QTCHARTS = True
except ImportError:
    HAS_QTCHARTS = False

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from database import DatabaseManager, Sale, SaleItem, Product, Setting

# ---------------------------------------------------------------- palette


class Palette:
    WHITE = "#FFFFFF"
    BG = "#F8FAFC"
    BORDER = "#E2E8F0"
    PRIMARY = "#2563EB"
    SUCCESS = "#16A34A"
    WARNING = "#F59E0B"
    DANGER = "#DC2626"
    TEXT_DARK = "#0F172A"
    TEXT_MUTED = "#64748B"
    TEXT_LABEL = "#475569"


def rgba(hex_color, alpha):
    """Convert a #RRGGBB hex string to a CSS rgba() string."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def make_shadow(blur=16, y_offset=3, alpha=25):
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(15, 23, 42, alpha))
    return effect


def panel_frame(title=None, object_name="panel"):
    """Create a white, rounded, shadowed container."""
    frame = QFrame()
    frame.setObjectName(object_name)
    frame.setStyleSheet(f"""
        QFrame#{object_name} {{
            background-color: {Palette.WHITE};
            border: 1px solid {Palette.BORDER};
            border-radius: 16px;
        }}
    """)
    frame.setGraphicsEffect(make_shadow(blur=14, y_offset=2))

    outer = QVBoxLayout(frame)
    outer.setContentsMargins(20, 18, 20, 18)
    outer.setSpacing(12)

    if title:
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"font-size: 15px; font-weight: 600; color: {Palette.TEXT_DARK};"
        )
        outer.addWidget(title_label)

    return frame, outer


# ------------------------------------------------------------------ cards


class StatCard(QFrame):
    """KPI card with icon, animated value, and a trend badge."""

    def __init__(self, icon, label, accent_color, parent=None):
        super().__init__(parent)
        self.accent_color = accent_color
        self._anims = []

        self.setObjectName("statCard")
        self.setMinimumHeight(118)
        self.setCursor(Qt.PointingHandCursor)

        self._shadow = make_shadow(blur=16, y_offset=3)
        self.setGraphicsEffect(self._shadow)

        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: {Palette.WHITE};
                border: 1px solid {Palette.BORDER};
                border-radius: 16px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        top_row = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 22px;")
        top_row.addWidget(icon_label)
        top_row.addStretch()
        self.trend_label = QLabel("")
        top_row.addWidget(self.trend_label)
        layout.addLayout(top_row)

        title_label = QLabel(label)
        title_label.setStyleSheet(
            f"font-size: 13px; font-weight: 500; color: {Palette.TEXT_LABEL};"
        )
        layout.addWidget(title_label)

        self.value_label = QLabel("--")
        self.value_label.setStyleSheet(
            f"font-size: 26px; font-weight: 600; color: {accent_color};"
        )
        layout.addWidget(self.value_label)

    def enterEvent(self, event):
        self._animate_shadow(26)
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: {Palette.WHITE};
                border: 1px solid {self.accent_color};
                border-radius: 16px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_shadow(16)
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: {Palette.WHITE};
                border: 1px solid {Palette.BORDER};
                border-radius: 16px;
            }}
        """)
        super().leaveEvent(event)

    def _animate_shadow(self, target_blur):
        anim = QPropertyAnimation(self._shadow, b"blurRadius", self)
        anim.setDuration(180)
        anim.setStartValue(self._shadow.blurRadius())
        anim.setEndValue(target_blur)
        anim.finished.connect(lambda: self._anims.remove(anim) if anim in self._anims else None)
        anim.start()
        self._anims.append(anim)

    def set_trend(self, percent):
        if percent is None:
            self.trend_label.setText("")
            return
        arrow = "▲" if percent >= 0 else "▼"
        color = Palette.SUCCESS if percent >= 0 else Palette.DANGER
        self.trend_label.setText(f"{arrow} {abs(percent):.0f}%")
        self.trend_label.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {color};"
        )

    def set_value(self, target, prefix="", decimals=0, animate=True):
        if not animate:
            self._render_value(prefix, target, decimals)
            return

        anim = QVariantAnimation(self)
        anim.setDuration(700)
        anim.setStartValue(0.0)
        anim.setEndValue(float(target))
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.valueChanged.connect(lambda v: self._render_value(prefix, v, decimals))
        anim.finished.connect(lambda: self._anims.remove(anim) if anim in self._anims else None)
        anim.start()
        self._anims.append(anim)

    def _render_value(self, prefix, value, decimals):
        if decimals:
            self.value_label.setText(f"{prefix}{value:,.{decimals}f}")
        else:
            self.value_label.setText(f"{prefix}{int(round(value)):,}")


class ActionCard(QFrame):
    """Clickable quick-action tile."""

    def __init__(self, icon, label, handler, parent=None):
        super().__init__(parent)
        self._handler = handler
        self._anims = []

        self.setObjectName("actionCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(84)

        self._shadow = make_shadow(blur=0, y_offset=0, alpha=0)
        self.setGraphicsEffect(self._shadow)

        self.setStyleSheet(f"""
            QFrame#actionCard {{
                background-color: {Palette.WHITE};
                border: 1px solid {Palette.BORDER};
                border-radius: 12px;
            }}
            QFrame#actionCard:hover {{
                border: 1px solid {Palette.PRIMARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 22px;")
        layout.addWidget(icon_label)

        text_label = QLabel(label)
        text_label.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: {Palette.TEXT_DARK};"
        )
        layout.addWidget(text_label)
        layout.addStretch()

    def enterEvent(self, event):
        self._animate_shadow(18)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_shadow(0)
        super().leaveEvent(event)

    def _animate_shadow(self, target):
        anim = QPropertyAnimation(self._shadow, b"blurRadius", self)
        anim.setDuration(150)
        anim.setStartValue(self._shadow.blurRadius())
        anim.setEndValue(target)
        anim.finished.connect(lambda: self._anims.remove(anim) if anim in self._anims else None)
        anim.start()
        self._anims.append(anim)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._handler:
            self._handler()
        super().mousePressEvent(event)


class TopProductRow(QWidget):
    """One row in the Top Selling Products list."""

    def __init__(self, rank, name, qty, max_qty, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(5)

        top = QHBoxLayout()
        rank_label = QLabel(f"{rank}. {name}")
        rank_label.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: {Palette.TEXT_DARK};"
        )
        top.addWidget(rank_label)
        top.addStretch()
        qty_label = QLabel(f"{qty} sold")
        qty_label.setStyleSheet(f"font-size: 12px; color: {Palette.TEXT_MUTED};")
        top.addWidget(qty_label)
        layout.addLayout(top)

        bar_bg = QFrame()
        bar_bg.setFixedHeight(8)
        bar_bg.setStyleSheet(f"background-color: {Palette.BG}; border-radius: 4px;")
        bar_layout = QHBoxLayout(bar_bg)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)

        pct = max(4, int((qty / max_qty) * 100)) if max_qty else 4
        fill = QFrame()
        fill.setStyleSheet(f"background-color: {Palette.PRIMARY}; border-radius: 4px;")
        bar_layout.addWidget(fill, pct)
        remainder = QFrame()
        remainder.setStyleSheet("background: transparent;")
        bar_layout.addWidget(remainder, max(0, 100 - pct))

        layout.addWidget(bar_bg)


class LowStockRow(QWidget):
    """One row in the Low Stock panel."""

    def __init__(self, name, stock, min_level, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)

        is_critical = stock == 0
        dot = "●" if is_critical else "●"
        color = Palette.DANGER if is_critical else Palette.WARNING

        name_label = QLabel(f"{dot} {name}")
        name_label.setStyleSheet(
            f"font-size: 13px; font-weight: 500; color: {Palette.TEXT_DARK};"
        )
        layout.addWidget(name_label)
        layout.addStretch()

        badge_text = "Out of stock" if is_critical else f"{stock} left"
        badge = QLabel(badge_text)
        badge.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {color};
            background-color: {rgba(color, 0.12)};
            border-radius: 10px;
            padding: 3px 10px;
        """)
        layout.addWidget(badge)


class SimpleBarChart(QWidget):
    """Lightweight fallback bar chart."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []
        self.setMinimumHeight(200)

    def set_data(self, data):
        self._data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if not self._data:
            return

        width, height = self.width(), self.height()
        padding = 10
        usable_h = height - 2 * padding
        max_val = max((v for _, v in self._data), default=1) or 1

        n = len(self._data)
        gap = 3
        bar_w = max(2.0, (width - 2 * padding - gap * (n - 1)) / n)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(Palette.PRIMARY))

        x = float(padding)
        for _, value in self._data:
            bar_h = (value / max_val) * usable_h if max_val else 0
            y = height - padding - bar_h
            painter.drawRoundedRect(int(x), int(y), int(bar_w), int(bar_h), 3, 3)
            x += bar_w + gap


# -------------------------------------------------------------- dashboard


class DashboardWindow(QWidget):
    """Main Dashboard Window"""

    DATA_REFRESH_MS = 60000

    def __init__(self, parent=None):
        super().__init__(parent)

        self.db = DatabaseManager()
        self._first_load = True
        self._owner_name = "there"

        self.setWindowTitle("Dashboard")
        self.setStyleSheet(f"background-color: {Palette.BG};")

        self._build_ui()
        self.load_data()

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)

        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.load_data)
        self.data_timer.start(self.DATA_REFRESH_MS)

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        outer_layout.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {Palette.BG};")
        scroll.setWidget(content)

        main_layout = QVBoxLayout(content)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        main_layout.addLayout(self._build_header())
        main_layout.addLayout(self._build_stats_grid())
        main_layout.addLayout(self._build_chart_and_actions_row())
        main_layout.addLayout(self._build_products_and_lowstock_row())
        main_layout.addWidget(self._build_recent_sales_panel())

    def _build_header(self):
        layout = QVBoxLayout()
        layout.setSpacing(2)

        top_row = QHBoxLayout()
        self.greeting_label = QLabel("")
        self.greeting_label.setStyleSheet(
            f"font-size: 32px; font-weight: 700; color: {Palette.TEXT_DARK};"
        )
        top_row.addWidget(self.greeting_label)
        top_row.addStretch()

        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"font-size: 14px; color: {Palette.TEXT_MUTED};")
        top_row.addWidget(self.time_label)
        layout.addLayout(top_row)

        self.subtitle_label = QLabel("Here's what's happening in your store today.")
        self.subtitle_label.setStyleSheet(
            f"font-size: 14px; color: {Palette.TEXT_MUTED};"
        )
        layout.addWidget(self.subtitle_label)

        self.month_summary_label = QLabel("")
        self.month_summary_label.setStyleSheet(
            f"font-size: 12px; color: {Palette.TEXT_MUTED};"
        )
        layout.addWidget(self.month_summary_label)

        self.update_time()
        return layout

    def _build_stats_grid(self):
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(14)

        self.cards = {
            "sales": StatCard("💰", "Today's Sales", Palette.PRIMARY),
            "profit": StatCard("📈", "Today's Profit", Palette.SUCCESS),
            "bills": StatCard("🧾", "Today's Bills", Palette.WARNING),
            "products": StatCard("📦", "Total Products", "#9333EA"),
            "low_stock": StatCard("⚠️", "Low Stock Products", Palette.DANGER),
        }
        self._rearrange_stats_grid()
        return self.stats_grid

    def _rearrange_stats_grid(self):
        """Arrange cards in 5 columns on wide screens, or 3+2 on compact screens"""
        while self.stats_grid.count():
            self.stats_grid.takeAt(0)

        screen = QApplication.primaryScreen()
        width = self.width() if self.width() > 200 else (screen.availableGeometry().width() if screen else 1200)

        card_list = list(self.cards.values())
        if width < 1200:
            # 2 rows: 3 on top, 2 on bottom
            for i in range(3):
                self.stats_grid.addWidget(card_list[i], 0, i)
            for j in range(3, 5):
                self.stats_grid.addWidget(card_list[j], 1, j - 3, 1, 1 if j == 3 else 2)
        else:
            # 1 row of 5
            for i, card in enumerate(card_list):
                self.stats_grid.addWidget(card, 0, i)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "stats_grid") and hasattr(self, "cards"):
            self._rearrange_stats_grid()

    def _build_chart_and_actions_row(self):
        row = QHBoxLayout()
        row.setSpacing(20)
        row.addWidget(self._build_chart_panel(), 2)
        row.addWidget(self._build_quick_actions_panel(), 1)
        return row

    def _build_chart_panel(self):
        frame, layout = panel_frame("Today's Sales", "salesChartPanel")

        if HAS_QTCHARTS:
            self.chart_view = self._make_qt_chart_view()
            layout.addWidget(self.chart_view)
        else:
            self.chart_view = SimpleBarChart()
            layout.addWidget(self.chart_view)
            note = QLabel(
                "Tip: run 'pip install PySide6-Addons' for an interactive chart."
            )
            note.setStyleSheet(f"font-size: 11px; color: {Palette.TEXT_MUTED};")
            layout.addWidget(note)

        return frame

    def _make_qt_chart_view(self):
        self._chart = QChart()
        self._chart.setBackgroundVisible(False)
        self._chart.legend().hide()
        self._chart.setAnimationOptions(QChart.SeriesAnimations)

        self._chart_series = QLineSeries()
        pen = self._chart_series.pen()
        pen.setWidth(3)
        pen.setColor(QColor(Palette.PRIMARY))
        self._chart_series.setPen(pen)
        self._chart.addSeries(self._chart_series)

        self._axis_x = QValueAxis()
        self._axis_x.setLabelFormat("%d:00")
        self._axis_x.setRange(0, 23)
        self._axis_x.setTickCount(6)
        self._chart.addAxis(self._axis_x, Qt.AlignBottom)
        self._chart_series.attachAxis(self._axis_x)

        self._axis_y = QValueAxis()
        self._axis_y.setRange(0, 10)
        self._chart.addAxis(self._axis_y, Qt.AlignLeft)
        self._chart_series.attachAxis(self._axis_y)

        view = QChartView(self._chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setMinimumHeight(220)
        view.setStyleSheet("background: transparent;")
        return view

    def _build_quick_actions_panel(self):
        frame, layout = panel_frame("Quick Actions", "quickActionsPanel")

        grid = QGridLayout()
        grid.setSpacing(10)
        actions = [
            ("➕", "New Sale", self.go_to_sales),
            ("📦", "Products", self.go_to_products),
            ("📊", "Reports", self.go_to_reports),
            ("⚙️", "Settings", self.go_to_settings),
        ]
        for i, (icon, label, handler) in enumerate(actions):
            card = ActionCard(icon, label, handler)
            grid.addWidget(card, i // 2, i % 2)

        layout.addLayout(grid)
        return frame

    def _build_products_and_lowstock_row(self):
        row = QHBoxLayout()
        row.setSpacing(20)
        row.addWidget(self._build_top_products_panel(), 1)
        row.addWidget(self._build_low_stock_panel(), 1)
        return row

    def _build_top_products_panel(self):
        frame, layout = panel_frame("Top Selling Products (This Month)", "topProductsPanel")
        self.top_products_container = QVBoxLayout()
        self.top_products_container.setSpacing(4)
        layout.addLayout(self.top_products_container)
        self.top_products_empty_label = QLabel("No sales recorded yet this month.")
        self.top_products_empty_label.setStyleSheet(
            f"font-size: 13px; color: {Palette.TEXT_MUTED};"
        )
        layout.addWidget(self.top_products_empty_label)
        return frame

    def _build_low_stock_panel(self):
        frame, layout = panel_frame("Low Stock", "lowStockPanel")
        self.low_stock_container = QVBoxLayout()
        self.low_stock_container.setSpacing(2)
        layout.addLayout(self.low_stock_container)
        self.low_stock_empty_label = QLabel("✅ All products have sufficient stock")
        self.low_stock_empty_label.setStyleSheet(
            f"font-size: 13px; color: {Palette.SUCCESS}; font-weight: 500;"
        )
        layout.addWidget(self.low_stock_empty_label)
        return frame

    def _build_recent_sales_panel(self):
        """Build the recent sales table with professional styling"""
        frame, layout = panel_frame("Recent Sales", "recentSalesPanel")

        self.recent_sales_table = QTableWidget(0, 4)
        self.recent_sales_table.setHorizontalHeaderLabels(
            ["Invoice", "Customer", "Amount", "Time"]
        )

        # Hide vertical row numbers
        self.recent_sales_table.verticalHeader().hide()

        # Professional table styling matching other tables
        self.recent_sales_table.setAlternatingRowColors(True)
        self.recent_sales_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.recent_sales_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.recent_sales_table.setFocusPolicy(Qt.NoFocus)
        self.recent_sales_table.setShowGrid(False)

        # Set column widths and stretch modes
        self.recent_sales_table.setColumnWidth(0, 130)  # Invoice
        self.recent_sales_table.setColumnWidth(2, 130)  # Amount
        self.recent_sales_table.setColumnWidth(3, 160)  # Time

        # Allow Customer column to stretch and fill all remaining space
        header = self.recent_sales_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)

        # Set row height
        self.recent_sales_table.verticalHeader().setDefaultSectionSize(50)
        self.recent_sales_table.setMinimumHeight(220)

        # Professional styling with bold headers and vertical dividers
        self.recent_sales_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background-color: white;
                gridline-color: #e2e8f0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px 10px;
                border-right: 1px solid #e2e8f0;
            }
            QTableWidget::item:last {
                border-right: none;
            }
            QTableWidget::item:selected {
                background-color: #eff6ff;
                color: #0f172a;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #0f172a;
                padding: 12px 10px;
                border: none;
                border-right: 1px solid #e2e8f0;
                border-bottom: 2px solid #e2e8f0;
                font-size: 13px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTableWidget::item:alternate {
                background-color: #f8fafc;
            }
        """)

        layout.addWidget(self.recent_sales_table)
        return frame

    # --------------------------------------------------------------- data

    def update_time(self):
        now = datetime.now()
        hour = now.hour
        if hour < 12:
            greeting, emoji = "Good Morning", "☀️"
        elif hour < 17:
            greeting, emoji = "Good Afternoon", "🌤️"
        else:
            greeting, emoji = "Good Evening", "🌙"

        self.greeting_label.setText(f"{greeting}, {self._owner_name} {emoji}")
        self.time_label.setText(now.strftime("%I:%M %p"))

    def load_data(self):
        session = self.db.get_session()
        try:
            currency_symbol = self._get_setting(session, "currency_symbol", "Rs")
            self._owner_name = self._get_setting(session, "owner_name", "there")

            # Get today's data
            today_total, today_profit, today_bills = self._period_totals(
                session, days_ago=0
            )
            yesterday_total, yesterday_profit, yesterday_bills = self._period_totals(
                session, days_ago=1
            )
            monthly_total, monthly_profit = self._month_totals(session)

            # Get product counts
            total_products = session.query(Product).count()

            # ✅ FIX: Use correct field name for stock
            low_stock_products = (
                session.query(Product)
                .filter(Product.current_stock <= Product.min_stock_level)
                .order_by(Product.current_stock.asc())
                .all()
            )

            animate = self._first_load

            # Update cards
            self.cards["sales"].set_value(
                today_total, prefix=currency_symbol, decimals=2, animate=animate
            )
            self.cards["sales"].set_trend(
                self._pct_change(today_total, yesterday_total)
            )

            self.cards["profit"].set_value(
                today_profit, prefix=currency_symbol, decimals=2, animate=animate
            )
            self.cards["profit"].set_trend(
                self._pct_change(today_profit, yesterday_profit)
            )

            self.cards["bills"].set_value(today_bills, animate=animate)
            self.cards["bills"].set_trend(
                self._pct_change(today_bills, yesterday_bills)
            )

            self.cards["products"].set_value(total_products, animate=animate)
            self.cards["low_stock"].set_value(len(low_stock_products), animate=animate)

            # Update month summary
            self.month_summary_label.setText(
                f"This month: {currency_symbol}{monthly_total:,.0f} in sales · "
                f"{currency_symbol}{monthly_profit:,.0f} profit"
            )

            # Render sections
            self._render_low_stock(low_stock_products[:8])
            self._render_top_products(self._top_products(session))
            self._render_recent_sales(self._recent_sales(session), currency_symbol)
            self._render_chart(self._hourly_sales_today(session))

            self._first_load = False

        except Exception as e:
            print(f"Error loading dashboard: {e}")
            import traceback

            traceback.print_exc()
        finally:
            session.close()

    @staticmethod
    def _get_setting(session, key, default):
        row = session.query(Setting).filter_by(key=key).first()
        return row.value if row and row.value else default

    @staticmethod
    def _period_totals(session, days_ago=0):
        target_date = (datetime.now() - timedelta(days=days_ago)).date()
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())

        total, profit, bills = (
            session.query(
                func.coalesce(func.sum(Sale.net_amount), 0),
                func.coalesce(func.sum(Sale.profit), 0),
                func.count(Sale.id),
            )
            .filter(Sale.sale_date.between(start, end))
            .one()
        )

        return float(total), float(profit), int(bills)

    @staticmethod
    def _month_totals(session):
        today = datetime.now().date()
        start = datetime(today.year, today.month, 1)

        total, profit = (
            session.query(
                func.coalesce(func.sum(Sale.net_amount), 0),
                func.coalesce(func.sum(Sale.profit), 0),
            )
            .filter(Sale.sale_date >= start)
            .one()
        )

        return float(total), float(profit)

    @staticmethod
    def _pct_change(current, previous):
        if not previous:
            return None
        return ((current - previous) / previous) * 100

    @staticmethod
    def _hourly_sales_today(session):
        today = datetime.now().date()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())

        rows = (
            session.query(
                func.strftime("%H", Sale.sale_date).label("hour"),
                func.sum(Sale.net_amount).label("total"),
            )
            .filter(Sale.sale_date.between(start, end))
            .group_by("hour")
            .all()
        )
        totals = {int(h): float(t or 0) for h, t in rows}
        return [(hour, totals.get(hour, 0.0)) for hour in range(24)]

    @staticmethod
    def _top_products(session, limit=5):
        since = datetime(datetime.now().year, datetime.now().month, 1)
        rows = (
            session.query(Product.name, func.sum(SaleItem.quantity).label("qty"))
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .filter(Sale.sale_date >= since)
            .group_by(Product.id)
            .order_by(func.sum(SaleItem.quantity).desc())
            .limit(limit)
            .all()
        )
        return [(name, int(qty)) for name, qty in rows]

    @staticmethod
    def _recent_sales(session, limit=6):
        return (
            session.query(Sale)
            .options(joinedload(Sale.customer))
            .order_by(Sale.sale_date.desc())
            .limit(limit)
            .all()
        )

    # ------------------------------------------------------------ render

    def _render_chart(self, hourly_totals):
        if HAS_QTCHARTS:
            self._chart_series.clear()
            max_val = 0
            for hour, total in hourly_totals:
                self._chart_series.append(hour, total)
                max_val = max(max_val, total)
            self._axis_y.setRange(0, max_val * 1.2 if max_val else 10)
        else:
            self.chart_view.set_data([(f"{h}:00", t) for h, t in hourly_totals])

    def _render_low_stock(self, low_stock_products):
        self._clear_layout(self.low_stock_container)
        has_items = bool(low_stock_products)
        self.low_stock_empty_label.setVisible(not has_items)
        for product in low_stock_products:
            row = LowStockRow(
                product.name, product.current_stock, product.min_stock_level
            )
            self.low_stock_container.addWidget(row)

    def _render_top_products(self, top_products):
        self._clear_layout(self.top_products_container)
        has_items = bool(top_products)
        self.top_products_empty_label.setVisible(not has_items)
        if not has_items:
            return
        max_qty = max(qty for _, qty in top_products)
        for i, (name, qty) in enumerate(top_products, start=1):
            row = TopProductRow(i, name, qty, max_qty)
            self.top_products_container.addWidget(row)

    def _render_recent_sales(self, sales, currency_symbol="Rs"):
        """Render recent sales with proper formatting and timezone"""
        table = self.recent_sales_table
        table.setRowCount(len(sales))

        for row_idx, sale in enumerate(sales):
            invoice = getattr(sale, "invoice_number", None) or f"INV-{sale.id:05d}"

            if sale.customer:
                customer_name = sale.customer.name
            else:
                customer_name = "Walk-in"

            amount = f"{currency_symbol}{sale.net_amount:,.2f}"

            # If tzinfo is attached, convert to Pakistan time; otherwise it's already local
            if sale.sale_date:
                if sale.sale_date.tzinfo is not None and pytz:
                    pakistan_tz = pytz.timezone("Asia/Karachi")
                    local_time = sale.sale_date.astimezone(pakistan_tz)
                else:
                    local_time = sale.sale_date
                time_str = local_time.strftime("%b %d, %Y %I:%M %p")
            else:
                time_str = "--"

            # Set items with proper alignment
            values = [invoice, customer_name, amount, time_str]
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                table.setItem(row_idx, col_idx, item)

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    # ---------------------------------------------------------- navigation

    def _navigate(self, key):
        """Navigate to a module using the parent MainWindow."""
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, "navigate_to"):
                parent.navigate_to(key)
                return
            parent = parent.parent()
        print(f"Cannot navigate to '{key}': MainWindow not found in parent chain")

    def go_to_sales(self):
        self._navigate("sales")

    def go_to_products(self):
        self._navigate("products")

    def go_to_reports(self):
        self._navigate("reports")

    def go_to_settings(self):
        self._navigate("settings")
