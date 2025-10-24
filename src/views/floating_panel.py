"""
Floating Panel Window - Independent window for displaying category items
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QEvent
from PyQt6.QtGui import QFont, QCursor
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.category import Category
from models.item import Item
from views.widgets.item_widget import ItemButton
from views.widgets.search_bar import SearchBar
from core.search_engine import SearchEngine

# Get logger
logger = logging.getLogger(__name__)


class FloatingPanel(QWidget):
    """Floating window for displaying category items"""

    # Signal emitted when an item is clicked
    item_clicked = pyqtSignal(object)

    # Signal emitted when window is closed
    window_closed = pyqtSignal()

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.current_category = None
        self.config_manager = config_manager
        self.search_engine = SearchEngine()
        self.all_items = []  # Store all items before filtering

        # Get panel width from config
        if config_manager:
            self.panel_width = config_manager.get_setting('panel_width', 500)
        else:
            self.panel_width = 500

        # Resize handling
        self.resizing = False
        self.resize_start_x = 0
        self.resize_start_width = 0
        self.resize_edge_width = 15  # Width of the resize edge in pixels (increased)

        self.init_ui()

    def init_ui(self):
        """Initialize the floating panel UI"""
        # Window properties
        self.setWindowTitle("Widget Sidebar - Items")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        # Calculate window height: 80% of screen height (same as sidebar)
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_height = screen.availableGeometry().height()
            window_height = int(screen_height * 0.8)
        else:
            window_height = 600  # Fallback

        # Set window size (allow width to be resized)
        self.setMinimumWidth(300)  # Minimum width
        self.setMaximumWidth(1000)  # Maximum width
        self.setMinimumHeight(400)
        self.resize(self.panel_width, window_height)

        # Enable mouse tracking for resize cursor
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        # Set window opacity
        self.setWindowOpacity(0.95)

        # Set background
        self.setStyleSheet("""
            FloatingPanel {
                background-color: #252525;
                border: 2px solid #007acc;
                border-left: 5px solid #007acc;
                border-radius: 8px;
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
                background-color: #007acc;
                color: #ffffff;
                padding: 15px;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 6px 6px 0 0;
            }
        """)
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.header_label)

        # Search bar
        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self.on_search_changed)
        main_layout.addWidget(self.search_bar)

        # Scroll area for items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #252525;
                border-radius: 0 0 6px 6px;
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

    def load_category(self, category: Category):
        """Load and display items from a category"""
        logger.info(f"Loading category: {category.name} with {len(category.items)} items")

        self.current_category = category
        self.all_items = category.items.copy()

        # Update header
        self.header_label.setText(category.name)
        logger.debug(f"Header updated to: {category.name}")

        # Clear search bar
        self.search_bar.clear_search()

        # Clear existing items
        self.clear_items()
        logger.debug("Previous items cleared")

        # Add new items
        self.display_items(self.all_items)

        # Show the window
        self.show()
        self.raise_()
        self.activateWindow()

    def display_items(self, items):
        """Display a list of items"""
        logger.info(f"Displaying {len(items)} items")

        # Clear existing items
        self.clear_items()

        # Add items
        for idx, item in enumerate(items):
            logger.debug(f"Creating button {idx+1}/{len(items)}: {item.label}")
            item_button = ItemButton(item)
            item_button.item_clicked.connect(self.on_item_clicked)
            self.items_layout.insertWidget(self.items_layout.count() - 1, item_button)

        logger.info(f"Successfully added {len(items)} item buttons to layout")

    def clear_items(self):
        """Clear all item buttons"""
        while self.items_layout.count() > 1:  # Keep the stretch at the end
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def on_item_clicked(self, item: Item):
        """Handle item click"""
        # Emit signal to parent
        self.item_clicked.emit(item)

    def on_search_changed(self, query: str):
        """Handle search query change with filtering"""
        if not self.current_category:
            return

        if not query or not query.strip():
            # Show all items if query is empty
            self.display_items(self.all_items)
        else:
            # Filter items using search engine
            filtered_items = self.search_engine.search_in_category(query, self.current_category)
            self.display_items(filtered_items)

    def position_near_sidebar(self, sidebar_window):
        """Position the floating panel near the sidebar window"""
        # Get sidebar window geometry
        sidebar_x = sidebar_window.x()
        sidebar_y = sidebar_window.y()
        sidebar_width = sidebar_window.width()

        # Position to the left of the sidebar
        panel_x = sidebar_x - self.width() - 10  # 10px gap
        panel_y = sidebar_y

        self.move(panel_x, panel_y)
        logger.debug(f"Positioned floating panel at ({panel_x}, {panel_y})")

    def is_on_left_edge(self, pos):
        """Check if mouse position is on the left edge for resizing"""
        return pos.x() <= self.resize_edge_width

    def event(self, event):
        """Override event to handle hover for cursor changes"""
        if event.type() == QEvent.Type.HoverMove:
            pos = event.position().toPoint()
            if self.is_on_left_edge(pos):
                self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        return super().event(event)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging or resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_on_left_edge(event.pos()):
                # Start resizing
                self.resizing = True
                self.resize_start_x = event.globalPosition().toPoint().x()
                self.resize_start_width = self.width()
                event.accept()
            else:
                # Start dragging
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging or resizing"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing:
                # Calculate new width
                current_x = event.globalPosition().toPoint().x()
                delta_x = current_x - self.resize_start_x
                new_width = self.resize_start_width - delta_x  # Subtract because we're dragging from left edge

                # Apply constraints
                new_width = max(self.minimumWidth(), min(new_width, self.maximumWidth()))

                # Resize and reposition
                old_width = self.width()
                old_x = self.x()
                self.resize(new_width, self.height())

                # Adjust position to keep right edge fixed
                width_diff = self.width() - old_width
                self.move(old_x - width_diff, self.y())

                event.accept()
            else:
                # Dragging
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to end resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.resizing:
                self.resizing = False
                # Save new width to config
                if self.config_manager:
                    self.config_manager.set_setting('panel_width', self.width())
                event.accept()

    def closeEvent(self, event):
        """Handle window close event"""
        self.window_closed.emit()
        event.accept()
