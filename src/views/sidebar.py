"""
Sidebar View - Vertical sidebar with category buttons and scroll navigation
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
from typing import List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.category import Category
from views.widgets.button_widget import CategoryButton


class Sidebar(QWidget):
    """Vertical sidebar with category buttons and scroll navigation"""

    # Signal emitted when a category button is clicked
    category_clicked = pyqtSignal(str)  # category_id

    # Signal emitted when settings button is clicked
    settings_clicked = pyqtSignal()

    # Signal emitted when favorites button is clicked
    favorites_clicked = pyqtSignal()

    # Signal emitted when stats button is clicked
    stats_clicked = pyqtSignal()

    # Signal emitted when category filter button is clicked
    category_filter_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.category_buttons = {}
        self.active_button = None
        self.scroll_area = None

        self.init_ui()

    def init_ui(self):
        """Initialize sidebar UI"""
        # Set fixed width
        self.setFixedWidth(70)
        self.setMinimumHeight(400)

        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-left: 1px solid #1e1e1e;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # App title/logo
        title_label = QLabel("WS")
        title_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #007acc;
                padding: 15px;
                font-size: 16pt;
                font-weight: bold;
                border-bottom: 2px solid #007acc;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Scroll up button
        self.scroll_up_button = QPushButton("▲")
        self.scroll_up_button.setFixedSize(70, 30)
        self.scroll_up_button.setToolTip("Desplazar arriba")
        self.scroll_up_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scroll_up_button.setStyleSheet("""
            QPushButton {
                background-color: #1e1e1e;
                color: #007acc;
                border: none;
                border-bottom: 1px solid #3d3d3d;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #00a0ff;
            }
            QPushButton:pressed {
                background-color: #007acc;
                color: #ffffff;
            }
            QPushButton:disabled {
                color: #555555;
                background-color: #252525;
            }
        """)
        self.scroll_up_button.clicked.connect(self.scroll_up)
        main_layout.addWidget(self.scroll_up_button)

        # Category Filter button (FC)
        self.category_filter_button = QPushButton("FC")
        self.category_filter_button.setFixedSize(70, 40)
        self.category_filter_button.setToolTip("Filtro de Categorías")
        self.category_filter_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.category_filter_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea,
                    stop:1 #764ba2
                );
                color: white;
                border: none;
                border-bottom: 1px solid #3d3d3d;
                font-size: 11pt;
                font-weight: bold;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3,
                    stop:1 #653a8b
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4457bc,
                    stop:1 #542974
                );
            }
        """)
        self.category_filter_button.clicked.connect(self.on_category_filter_clicked)
        main_layout.addWidget(self.category_filter_button)

        # Scroll area for category buttons
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #2b2b2b;
            }
        """)

        # Container widget for buttons
        buttons_container = QWidget()
        self.buttons_layout = QVBoxLayout(buttons_container)
        self.buttons_layout.setContentsMargins(0, 5, 0, 5)
        self.buttons_layout.setSpacing(5)
        self.buttons_layout.addStretch()

        self.scroll_area.setWidget(buttons_container)
        main_layout.addWidget(self.scroll_area)

        # Scroll down button
        self.scroll_down_button = QPushButton("▼")
        self.scroll_down_button.setFixedSize(70, 30)
        self.scroll_down_button.setToolTip("Desplazar abajo")
        self.scroll_down_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scroll_down_button.setStyleSheet("""
            QPushButton {
                background-color: #1e1e1e;
                color: #007acc;
                border: none;
                border-top: 1px solid #3d3d3d;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #00a0ff;
            }
            QPushButton:pressed {
                background-color: #007acc;
                color: #ffffff;
            }
            QPushButton:disabled {
                color: #555555;
                background-color: #252525;
            }
        """)
        self.scroll_down_button.clicked.connect(self.scroll_down)
        main_layout.addWidget(self.scroll_down_button)

        # Favorites button
        self.favorites_button = QPushButton("⭐")
        self.favorites_button.setFixedSize(70, 60)
        self.favorites_button.setToolTip("Favoritos")
        self.favorites_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorites_button.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                color: #cccccc;
                border: none;
                border-top: 1px solid #1e1e1e;
                font-size: 20pt;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #F39C12;
            }
            QPushButton:pressed {
                background-color: #F39C12;
                color: #ffffff;
            }
        """)
        self.favorites_button.clicked.connect(self.on_favorites_clicked)
        main_layout.addWidget(self.favorites_button)

        # Stats button
        self.stats_button = QPushButton("📊")
        self.stats_button.setFixedSize(70, 60)
        self.stats_button.setToolTip("Estadísticas")
        self.stats_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stats_button.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                color: #cccccc;
                border: none;
                border-top: 1px solid #1e1e1e;
                font-size: 20pt;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #4EC9B0;
            }
            QPushButton:pressed {
                background-color: #4EC9B0;
                color: #ffffff;
            }
        """)
        self.stats_button.clicked.connect(self.on_stats_clicked)
        main_layout.addWidget(self.stats_button)

        # Settings button at the bottom
        self.settings_button = QPushButton("⚙")
        self.settings_button.setFixedSize(70, 60)
        self.settings_button.setToolTip("Configuración")
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #252525;
                color: #cccccc;
                border: none;
                border-top: 1px solid #1e1e1e;
                font-size: 20pt;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #007acc;
            }
            QPushButton:pressed {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        self.settings_button.clicked.connect(self.on_settings_clicked)
        main_layout.addWidget(self.settings_button)

        # Update scroll button states
        self.update_scroll_buttons()

    def scroll_up(self):
        """Scroll the category list up"""
        scrollbar = self.scroll_area.verticalScrollBar()
        current_value = scrollbar.value()
        new_value = max(0, current_value - 50)  # Scroll by button height (45px + spacing)

        # Animate scroll
        self.animate_scroll(current_value, new_value)

    def scroll_down(self):
        """Scroll the category list down"""
        scrollbar = self.scroll_area.verticalScrollBar()
        current_value = scrollbar.value()
        new_value = min(scrollbar.maximum(), current_value + 50)  # Scroll by button height (45px + spacing)

        # Animate scroll
        self.animate_scroll(current_value, new_value)

    def animate_scroll(self, start_value, end_value):
        """Animate scroll movement"""
        scrollbar = self.scroll_area.verticalScrollBar()

        # Create animation
        self.scroll_animation = QPropertyAnimation(scrollbar, b"value")
        self.scroll_animation.setDuration(200)
        self.scroll_animation.setStartValue(start_value)
        self.scroll_animation.setEndValue(end_value)
        self.scroll_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.scroll_animation.finished.connect(self.update_scroll_buttons)
        self.scroll_animation.start()

    def update_scroll_buttons(self):
        """Update scroll button enabled/disabled state"""
        if not self.scroll_area:
            return

        scrollbar = self.scroll_area.verticalScrollBar()

        # Disable up button if at top
        self.scroll_up_button.setEnabled(scrollbar.value() > 0)

        # Disable down button if at bottom
        self.scroll_down_button.setEnabled(scrollbar.value() < scrollbar.maximum())

    def load_categories(self, categories: List[Category]):
        """Load and create buttons for categories"""
        # Clear existing buttons
        self.clear_buttons()

        # Create button for each category
        for category in categories:
            if not category.is_active:
                continue

            button = CategoryButton(category.id, category.name)
            button.clicked.connect(lambda checked, cat_id=category.id: self.on_category_clicked(cat_id))

            self.category_buttons[category.id] = button
            # Insert before the stretch
            self.buttons_layout.insertWidget(self.buttons_layout.count() - 1, button)

        # Update scroll buttons after loading
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.update_scroll_buttons)
        self.update_scroll_buttons()

    def clear_buttons(self):
        """Clear all category buttons"""
        for button in self.category_buttons.values():
            button.deleteLater()
        self.category_buttons.clear()
        self.active_button = None

    def on_category_clicked(self, category_id: str):
        """Handle category button click"""
        # Update active button
        if self.active_button:
            self.active_button.set_active(False)

        clicked_button = self.category_buttons.get(category_id)
        if clicked_button:
            clicked_button.set_active(True)
            self.active_button = clicked_button

        # Emit signal
        self.category_clicked.emit(category_id)

    def set_active_category(self, category_id: str):
        """Set active category programmatically"""
        if self.active_button:
            self.active_button.set_active(False)

        button = self.category_buttons.get(category_id)
        if button:
            button.set_active(True)
            self.active_button = button

    def on_favorites_clicked(self):
        """Handle favorites button click"""
        self.favorites_clicked.emit()

    def on_stats_clicked(self):
        """Handle stats button click"""
        self.stats_clicked.emit()

    def on_settings_clicked(self):
        """Handle settings button click"""
        self.settings_clicked.emit()

    def on_category_filter_clicked(self):
        """Handle category filter button click"""
        self.category_filter_clicked.emit()
