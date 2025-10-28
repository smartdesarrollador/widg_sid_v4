"""
Floating Panel Window - Independent window for displaying category items
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QComboBox
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
from views.advanced_filters_window import AdvancedFiltersWindow
from core.search_engine import SearchEngine
from core.advanced_filter_engine import AdvancedFilterEngine

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
        self.filter_engine = AdvancedFilterEngine()  # Motor de filtrado avanzado
        self.all_items = []  # Store all items before filtering
        self.current_filters = {}  # Filtros activos actuales
        self.current_state_filter = "normal"  # Filtro de estado actual: normal, archived, inactive, all

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

        # Header with category name and close button
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #007acc;
                border-radius: 6px 6px 0 0;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 10, 10)
        header_layout.setSpacing(5)

        # Category title
        self.header_label = QLabel("Select a category")
        self.header_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #ffffff;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.header_label)

        # Close button
        close_button = QPushButton("✕")
        close_button.setFixedSize(24, 24)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                font-size: 12pt;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        close_button.clicked.connect(self.hide)
        header_layout.addWidget(close_button)

        main_layout.addWidget(header_widget)

        # Botón para abrir ventana de filtros avanzados
        filters_button_widget = QWidget()
        filters_button_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-bottom: 1px solid #3d3d3d;
            }
        """)
        filters_button_layout = QHBoxLayout(filters_button_widget)
        filters_button_layout.setContentsMargins(8, 5, 8, 5)
        filters_button_layout.setSpacing(0)

        self.open_filters_button = QPushButton("🔍 Filtros Avanzados")
        self.open_filters_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.open_filters_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        self.open_filters_button.clicked.connect(self.toggle_filters_window)
        filters_button_layout.addWidget(self.open_filters_button)

        # Agregar espaciador
        filters_button_layout.addSpacing(10)

        # Label para el filtro de estado
        state_label = QLabel("Estado:")
        state_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 10pt;
                background: transparent;
            }
        """)
        filters_button_layout.addWidget(state_label)

        # ComboBox para filtrar por estado
        self.state_filter_combo = QComboBox()
        self.state_filter_combo.addItem("📄 Normal", "normal")
        self.state_filter_combo.addItem("📦 Archivados", "archived")
        self.state_filter_combo.addItem("⏸️ Inactivos", "inactive")
        self.state_filter_combo.addItem("📋 Todos", "all")
        self.state_filter_combo.setCurrentIndex(0)  # Default: Normal
        self.state_filter_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.state_filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 10pt;
                min-width: 140px;
            }
            QComboBox:hover {
                border: 1px solid #007acc;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #cccccc;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #cccccc;
                selection-background-color: #007acc;
                selection-color: #ffffff;
                border: 1px solid #3d3d3d;
            }
        """)
        self.state_filter_combo.currentIndexChanged.connect(self.on_state_filter_changed)
        filters_button_layout.addWidget(self.state_filter_combo)

        main_layout.addWidget(filters_button_widget)

        # Crear ventana flotante de filtros (oculta inicialmente)
        self.filters_window = AdvancedFiltersWindow(self)
        self.filters_window.filters_changed.connect(self.on_filters_changed)
        self.filters_window.filters_cleared.connect(self.on_filters_cleared)
        self.filters_window.hide()

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

        # Update available tags in filters window (Fase 4)
        self.filters_window.update_available_tags(self.all_items)
        logger.debug(f"Updated available tags from {len(self.all_items)} items")

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

        # Aplicar filtros avanzados primero
        filtered_items = self.filter_engine.apply_filters(self.all_items, self.current_filters)

        # Aplicar filtro de estado (is_active, is_archived)
        filtered_items = self.filter_items_by_state(filtered_items)

        # Luego aplicar búsqueda si hay query
        if query and query.strip():
            # Crear categoría temporal con items filtrados para búsqueda
            from models.category import Category
            temp_category = Category(
                category_id="temp",
                name="temp",
                icon=""
            )
            # Asignar items después de crear la categoría
            temp_category.items = filtered_items
            filtered_items = self.search_engine.search_in_category(query, temp_category)

        self.display_items(filtered_items)

    def on_filters_changed(self, filters: dict):
        """Handle cuando cambian los filtros avanzados"""
        logger.info(f"Filters changed: {filters}")
        self.current_filters = filters

        # Re-aplicar búsqueda y filtros
        current_query = self.search_bar.search_input.text()
        self.on_search_changed(current_query)

    def on_filters_cleared(self):
        """Handle cuando se limpian todos los filtros"""
        logger.info("All filters cleared")
        self.current_filters = {}

        # Re-aplicar búsqueda sin filtros
        current_query = self.search_bar.search_input.text()
        self.on_search_changed(current_query)

    def on_state_filter_changed(self, index):
        """Handle cuando cambia el filtro de estado"""
        state_filter = self.state_filter_combo.itemData(index)
        self.current_state_filter = state_filter
        logger.info(f"State filter changed to: {state_filter}")

        # Re-aplicar búsqueda con nuevo filtro de estado
        current_query = self.search_bar.search_input.text()
        self.on_search_changed(current_query)

    def filter_items_by_state(self, items):
        """Filtrar items por estado (activo/archivado)

        Args:
            items: Lista de items a filtrar

        Returns:
            Lista de items filtrados según el estado actual
        """
        if self.current_state_filter == "all":
            # Mostrar todos los items
            return items
        elif self.current_state_filter == "normal":
            # Mostrar solo items activos y NO archivados
            return [item for item in items if getattr(item, 'is_active', True) and not getattr(item, 'is_archived', False)]
        elif self.current_state_filter == "archived":
            # Mostrar solo items archivados (independiente de si están activos)
            return [item for item in items if getattr(item, 'is_archived', False)]
        elif self.current_state_filter == "inactive":
            # Mostrar solo items inactivos
            return [item for item in items if not getattr(item, 'is_active', True)]
        else:
            return items

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

    def toggle_filters_window(self):
        """Abrir/cerrar la ventana de filtros avanzados"""
        if self.filters_window.isVisible():
            self.filters_window.hide()
        else:
            # Posicionar cerca del panel flotante
            self.filters_window.position_near_panel(self)
            self.filters_window.show()
            self.filters_window.raise_()
            self.filters_window.activateWindow()

    def closeEvent(self, event):
        """Handle window close event"""
        # Cerrar también la ventana de filtros si está abierta
        if self.filters_window.isVisible():
            self.filters_window.close()

        self.window_closed.emit()
        event.accept()
