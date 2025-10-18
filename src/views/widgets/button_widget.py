"""
Category Button Widget
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont


class CategoryButton(QPushButton):
    """Custom category button widget for sidebar"""

    def __init__(self, category_id: str, category_name: str, parent=None):
        super().__init__(parent)
        self.category_id = category_id
        self.category_name = category_name
        self.is_active = False

        self.init_ui()

    def init_ui(self):
        """Initialize button UI"""
        # Set button text
        self.setText(self.category_name)

        # Set fixed size - Altura reducida para visualizar más categorías
        self.setFixedSize(70, 45)

        # Set font
        font = QFont()
        font.setPointSize(9)
        font.setBold(False)
        self.setFont(font)

        # Enable cursor change on hover
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Apply default style
        self.update_style()

    def update_style(self):
        """Update button style based on state"""
        if self.is_active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: none;
                    border-left: 3px solid #007acc;
                    padding: 5px;
                    text-align: center;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #454545;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2b2b2b;
                    color: #cccccc;
                    border: none;
                    border-left: 3px solid transparent;
                    padding: 5px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background-color: #454545;
                }
            """)

    def set_active(self, active: bool):
        """Set button active state"""
        self.is_active = active
        self.update_style()

    def sizeHint(self) -> QSize:
        """Recommended size"""
        return QSize(70, 45)
