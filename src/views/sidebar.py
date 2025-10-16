"""
Sidebar View - Vertical sidebar with category buttons
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.category import Category
from views.widgets.button_widget import CategoryButton


class Sidebar(QWidget):
    """Vertical sidebar with category buttons"""

    # Signal emitted when a category button is clicked
    category_clicked = pyqtSignal(str)  # category_id

    # Signal emitted when settings button is clicked
    settings_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.category_buttons = {}
        self.active_button = None

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
                border-right: 1px solid #1e1e1e;
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

        # Container for category buttons
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setContentsMargins(0, 10, 0, 10)
        self.buttons_layout.setSpacing(5)
        main_layout.addLayout(self.buttons_layout)

        # Add stretch to push buttons to top
        main_layout.addStretch()

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
            self.buttons_layout.addWidget(button)

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

    def on_settings_clicked(self):
        """Handle settings button click"""
        self.settings_clicked.emit()
