"""
Item Button Widget
"""
from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.item import Item, ItemType


class ItemButton(QFrame):
    """Custom item button widget for content panel with tags support"""

    # Signal emitted when item is clicked with the item
    item_clicked = pyqtSignal(object)

    def __init__(self, item: Item, parent=None):
        super().__init__(parent)
        self.item = item
        self.is_copied = False

        self.init_ui()

    def init_ui(self):
        """Initialize button UI"""
        # Set frame properties
        self.setMinimumHeight(50)
        self.setMaximumHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 8, 15, 8)
        main_layout.setSpacing(10)

        # Left side: Item info (label + tags)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(5)

        # Item label
        self.label_widget = QLabel(self.item.label)
        label_font = QFont()
        label_font.setPointSize(10)
        self.label_widget.setFont(label_font)
        left_layout.addWidget(self.label_widget)

        # Tags container (only if item has tags)
        if self.item.tags and len(self.item.tags) > 0:
            tags_layout = QHBoxLayout()
            tags_layout.setContentsMargins(0, 0, 0, 0)
            tags_layout.setSpacing(5)

            for tag in self.item.tags:
                tag_label = QLabel(tag)
                tag_label.setStyleSheet("""
                    QLabel {
                        background-color: #007acc;
                        color: #ffffff;
                        border-radius: 3px;
                        padding: 2px 8px;
                        font-size: 8pt;
                    }
                """)
                tags_layout.addWidget(tag_label)

            tags_layout.addStretch()
            left_layout.addLayout(tags_layout)

        main_layout.addLayout(left_layout, 1)

        # Right side: Open URL button (only for URL items)
        if self.item.type == ItemType.URL:
            self.open_url_button = QPushButton("🌐")
            self.open_url_button.setFixedSize(35, 35)
            self.open_url_button.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    font-size: 16pt;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
                QPushButton:pressed {
                    background-color: #004578;
                }
            """)
            self.open_url_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.open_url_button.setToolTip("Abrir en navegador")
            self.open_url_button.clicked.connect(self.open_in_browser)
            main_layout.addWidget(self.open_url_button)

        # Set initial style
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: none;
                border-bottom: 1px solid #1e1e1e;
            }
            QFrame:hover {
                background-color: #3d3d3d;
            }
            QLabel {
                color: #cccccc;
                background-color: transparent;
                border: none;
            }
        """)

    def mousePressEvent(self, event):
        """Handle mouse press event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_clicked()
        super().mousePressEvent(event)

    def on_clicked(self):
        """Handle button click"""
        # Emit signal with item
        self.item_clicked.emit(self.item)

        # Show copied feedback
        self.show_copied_feedback()

    def open_in_browser(self):
        """Open URL in default browser"""
        if self.item.type == ItemType.URL:
            url = self.item.content
            # Ensure URL has proper protocol
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                else:
                    url = 'https://' + url

            # Open in browser
            webbrowser.open(url)

            # Update button style briefly to show it was clicked
            original_style = self.open_url_button.styleSheet()
            self.open_url_button.setStyleSheet("""
                QPushButton {
                    background-color: #00ff00;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    font-size: 16pt;
                }
            """)
            QTimer.singleShot(300, lambda: self.open_url_button.setStyleSheet(original_style))

    def show_copied_feedback(self):
        """Show visual feedback that item was copied"""
        self.is_copied = True

        # Change style temporarily
        self.setStyleSheet("""
            QFrame {
                background-color: #007acc;
                border: none;
                border-bottom: 1px solid #005a9e;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
                border: none;
                font-weight: bold;
            }
        """)

        # Reset after 500ms
        QTimer.singleShot(500, self.reset_style)

    def reset_style(self):
        """Reset button style to normal"""
        self.is_copied = False
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: none;
                border-bottom: 1px solid #1e1e1e;
            }
            QFrame:hover {
                background-color: #3d3d3d;
            }
            QLabel {
                color: #cccccc;
                background-color: transparent;
                border: none;
            }
        """)
