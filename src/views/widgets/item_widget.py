"""
Item Button Widget
"""
from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.item import Item


class ItemButton(QPushButton):
    """Custom item button widget for content panel"""

    # Signal emitted when item is clicked with the item
    item_clicked = pyqtSignal(object)

    def __init__(self, item: Item, parent=None):
        super().__init__(parent)
        self.item = item
        self.is_copied = False

        self.init_ui()

    def init_ui(self):
        """Initialize button UI"""
        # Set button text
        self.setText(self.item.label)

        # Set minimum height
        self.setMinimumHeight(40)
        self.setMaximumHeight(50)

        # Set font
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        # Enable cursor change on hover
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set alignment
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: none;
                border-bottom: 1px solid #1e1e1e;
                padding: 10px 15px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #454545;
            }
        """)

        # Connect click event
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        """Handle button click"""
        # Emit signal with item
        self.item_clicked.emit(self.item)

        # Show copied feedback
        self.show_copied_feedback()

    def show_copied_feedback(self):
        """Show visual feedback that item was copied"""
        self.is_copied = True

        # Change style temporarily
        self.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-bottom: 1px solid #005a9e;
                padding: 10px 15px;
                text-align: left;
                font-weight: bold;
            }
        """)

        # Reset after 500ms
        QTimer.singleShot(500, self.reset_style)

    def reset_style(self):
        """Reset button style to normal"""
        self.is_copied = False
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: none;
                border-bottom: 1px solid #1e1e1e;
                padding: 10px 15px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #454545;
            }
        """)
