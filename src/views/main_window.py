"""
Main Window View
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QScreen
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from views.sidebar import Sidebar
from views.content_panel import ContentPanel
from models.item import Item


class MainWindow(QMainWindow):
    """Main application window - frameless, always-on-top sidebar"""

    # Signals
    category_selected = pyqtSignal(str)  # category_id
    item_selected = pyqtSignal(object)  # Item

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.sidebar = None
        self.content_panel = None

        self.init_ui()
        self.position_window()

    def init_ui(self):
        """Initialize the user interface"""
        # Window properties
        self.setWindowTitle("Widget Sidebar")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Set window size (starts with sidebar only)
        self.setFixedWidth(70)  # Just sidebar initially
        self.setMinimumHeight(400)
        self.resize(70, 600)

        # Set window opacity
        self.setWindowOpacity(0.95)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        self.sidebar = Sidebar()
        self.sidebar.category_clicked.connect(self.on_category_clicked)
        main_layout.addWidget(self.sidebar)

        # Create content panel (initially collapsed)
        self.content_panel = ContentPanel()
        self.content_panel.item_clicked.connect(self.on_item_clicked)
        main_layout.addWidget(self.content_panel)

    def load_categories(self, categories):
        """Load categories into sidebar"""
        if self.sidebar:
            self.sidebar.load_categories(categories)

    def on_category_clicked(self, category_id: str):
        """Handle category button click"""
        print(f"Category clicked: {category_id}")

        # Get category from controller
        if self.controller:
            category = self.controller.get_category(category_id)
            if category:
                # Load category into content panel
                self.content_panel.load_category(category)

                # Adjust window width for expanded panel
                self.setFixedWidth(370)  # 70px sidebar + 300px panel

        # Emit signal
        self.category_selected.emit(category_id)

    def on_item_clicked(self, item: Item):
        """Handle item button click"""
        print(f"Item clicked: {item.label}")

        # Copy to clipboard via controller
        if self.controller:
            self.controller.copy_item_to_clipboard(item)

        # Emit signal
        self.item_selected.emit(item)

    def position_window(self):
        """Position window on the right edge of the screen"""
        # Get primary screen
        screen = self.screen()
        if screen is None:
            return

        screen_geometry = screen.availableGeometry()

        # Position on right edge
        x = screen_geometry.width() - self.width()
        y = (screen_geometry.height() - self.height()) // 2

        self.move(x, y)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
