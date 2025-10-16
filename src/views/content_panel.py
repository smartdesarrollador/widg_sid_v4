"""
Content Panel View - Expandable panel with items
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.category import Category
from models.item import Item
from views.widgets.item_widget import ItemButton


class ContentPanel(QWidget):
    """Expandable content panel displaying category items"""

    # Signal emitted when an item is clicked
    item_clicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_category = None
        self.is_expanded = False
        self.target_width = 300
        self.collapsed_width = 0

        self.init_ui()

    def init_ui(self):
        """Initialize the panel UI"""
        # Set fixed width (collapsed initially)
        self.setFixedWidth(self.collapsed_width)
        self.setMinimumHeight(400)

        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-left: 1px solid #1e1e1e;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header with category name
        self.header_label = QLabel("Select a category")
        self.header_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 15px;
                font-size: 12pt;
                font-weight: bold;
                border-bottom: 2px solid #007acc;
            }
        """)
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.header_label)

        # Scroll area for items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #252525;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 10px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """)

        # Container for items
        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(0)
        self.items_layout.addStretch()

        scroll_area.setWidget(self.items_container)
        main_layout.addWidget(scroll_area)

        # Animation for expand/collapse
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def load_category(self, category: Category):
        """Load and display items from a category"""
        self.current_category = category

        # Update header
        self.header_label.setText(category.name)

        # Clear existing items
        self.clear_items()

        # Add new items
        for item in category.items:
            item_button = ItemButton(item)
            item_button.item_clicked.connect(self.on_item_clicked)
            self.items_layout.insertWidget(self.items_layout.count() - 1, item_button)

        # Expand panel if not already expanded
        if not self.is_expanded:
            self.expand()

    def clear_items(self):
        """Clear all item buttons"""
        while self.items_layout.count() > 1:  # Keep the stretch at the end
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def expand(self):
        """Expand the panel with animation"""
        if self.is_expanded:
            return

        self.is_expanded = True
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.target_width)
        self.animation.start()

    def collapse(self):
        """Collapse the panel with animation"""
        if not self.is_expanded:
            return

        self.is_expanded = False
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.collapsed_width)
        self.animation.start()

    def toggle(self):
        """Toggle panel expansion"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def on_item_clicked(self, item: Item):
        """Handle item click"""
        # Emit signal to parent
        self.item_clicked.emit(item)
