"""
Floating Panel Window - Independent window for displaying category items
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QEvent, QTimer
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

    # Signal emitted when pin state changes
    pin_state_changed = pyqtSignal(bool)  # True = pinned, False = unpinned

    # Signal emitted when customization is requested
    customization_requested = pyqtSignal()

    def __init__(self, config_manager=None, panel_id=None, custom_name=None, custom_color=None, parent=None):
        super().__init__(parent)
        self.current_category = None
        self.config_manager = config_manager
        self.search_engine = SearchEngine()
        self.filter_engine = AdvancedFilterEngine()  # Motor de filtrado avanzado
        self.all_items = []  # Store all items before filtering
        self.current_filters = {}  # Filtros activos actuales
        self.current_state_filter = "normal"  # Filtro de estado actual: normal, archived, inactive, all
        self.is_pinned = False  # Estado de anclaje del panel
        self.is_minimized = False  # Estado de minimizado (solo para paneles anclados)
        self.normal_height = None  # Altura normal antes de minimizar
        self.normal_width = None  # Ancho normal antes de minimizar
        self.normal_position = None  # Posición normal antes de minimizar

        # Panel persistence attributes
        self.panel_id = panel_id  # ID del panel en la base de datos (None si no está guardado)
        self.custom_name = custom_name  # Nombre personalizado del panel
        self.custom_color = custom_color  # Color personalizado del header (hex format)

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

        # AUTO-UPDATE: Timer for debounced panel state updates
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._save_panel_state_to_db)
        self.update_delay_ms = 1000  # 1 second delay after move/resize

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
        self.header_widget = QWidget()
        self.header_widget.setStyleSheet("""
            QWidget {
                background-color: #007acc;
                border-radius: 6px 6px 0 0;
            }
        """)
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(15, 10, 10, 10)
        self.header_layout.setSpacing(5)

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
        self.header_layout.addWidget(self.header_label)

        # Pin button
        self.pin_button = QPushButton("📌")
        self.pin_button.setFixedSize(24, 24)
        self.pin_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pin_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                font-size: 10pt;
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
        self.pin_button.setToolTip("Anclar panel (permite abrir múltiples paneles)")
        self.pin_button.clicked.connect(self.toggle_pin)
        self.header_layout.addWidget(self.pin_button)

        # Minimize button (only visible when pinned)
        self.minimize_button = QPushButton("−")
        self.minimize_button.setFixedSize(24, 24)
        self.minimize_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                font-size: 16pt;
                font-weight: bold;
                padding: 0px;
                padding-bottom: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.minimize_button.setToolTip("Minimizar panel")
        self.minimize_button.clicked.connect(self.toggle_minimize)
        self.minimize_button.setVisible(False)  # Hidden by default (only show when pinned)
        self.header_layout.addWidget(self.minimize_button)

        # Config button (only visible when pinned)
        self.config_button = QPushButton("⚙")
        self.config_button.setFixedSize(24, 24)
        self.config_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.config_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                font-size: 10pt;
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
        self.config_button.setToolTip("Configurar panel (nombre y color)")
        self.config_button.clicked.connect(self.on_config_clicked)
        self.config_button.setVisible(False)  # Hidden by default (only show when pinned)
        self.header_layout.addWidget(self.config_button)

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
        self.header_layout.addWidget(close_button)

        main_layout.addWidget(self.header_widget)

        # Botón para abrir ventana de filtros avanzados
        self.filters_button_widget = QWidget()
        self.filters_button_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-bottom: 1px solid #3d3d3d;
            }
        """)
        filters_button_layout = QHBoxLayout(self.filters_button_widget)
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

        main_layout.addWidget(self.filters_button_widget)

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
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
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

        self.scroll_area.setWidget(self.items_container)
        main_layout.addWidget(self.scroll_area)

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

        # AUTO-UPDATE: Trigger panel state save with new filters
        if self.is_pinned and self.panel_id and self.config_manager:
            self.update_timer.start(self.update_delay_ms)
            logger.debug("Filter change triggered auto-save")

    def on_filters_cleared(self):
        """Handle cuando se limpian todos los filtros"""
        logger.info("All filters cleared")
        self.current_filters = {}

        # Re-aplicar búsqueda sin filtros
        current_query = self.search_bar.search_input.text()
        self.on_search_changed(current_query)

        # AUTO-UPDATE: Trigger panel state save with cleared filters
        if self.is_pinned and self.panel_id and self.config_manager:
            self.update_timer.start(self.update_delay_ms)
            logger.debug("Filter clear triggered auto-save")

    def on_state_filter_changed(self, index):
        """Handle cuando cambia el filtro de estado"""
        state_filter = self.state_filter_combo.itemData(index)
        self.current_state_filter = state_filter
        logger.info(f"State filter changed to: {state_filter}")

        # Re-aplicar búsqueda con nuevo filtro de estado
        current_query = self.search_bar.search_input.text()
        self.on_search_changed(current_query)

        # AUTO-UPDATE: Trigger panel state save with new state filter
        if self.is_pinned and self.panel_id and self.config_manager:
            self.update_timer.start(self.update_delay_ms)
            logger.debug("State filter change triggered auto-save")

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

    def apply_filter_config(self, filter_config: dict):
        """Apply saved filter configuration to panel

        Args:
            filter_config: Dict with 'advanced_filters', 'state_filter', and 'search_text'
        """
        if not filter_config:
            logger.debug("No filter config to apply")
            return

        try:
            logger.info(f"Applying filter configuration: {filter_config}")

            # Apply advanced filters
            if 'advanced_filters' in filter_config:
                self.current_filters = filter_config['advanced_filters']
                logger.debug(f"Applied advanced filters: {self.current_filters}")

            # Apply state filter and update combo box
            if 'state_filter' in filter_config:
                state_filter = filter_config['state_filter']
                self.current_state_filter = state_filter

                # Update combo box to match (without triggering signal)
                state_index_map = {
                    'normal': 0,
                    'archived': 1,
                    'inactive': 2,
                    'all': 3
                }
                if state_filter in state_index_map:
                    self.state_filter_combo.blockSignals(True)
                    self.state_filter_combo.setCurrentIndex(state_index_map[state_filter])
                    self.state_filter_combo.blockSignals(False)
                    logger.debug(f"Applied state filter: {state_filter}")

            # Apply search text and update search bar
            if 'search_text' in filter_config:
                search_text = filter_config['search_text']
                if search_text:
                    self.search_bar.search_input.blockSignals(True)
                    self.search_bar.search_input.setText(search_text)
                    self.search_bar.search_input.blockSignals(False)
                    logger.debug(f"Applied search text: {search_text}")

            # Trigger filter application
            current_query = self.search_bar.search_input.text()
            self.on_search_changed(current_query)

            logger.info("Filter configuration applied successfully")
        except Exception as e:
            logger.error(f"Error applying filter config: {e}", exc_info=True)

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

    def toggle_pin(self):
        """Toggle panel pin state"""
        self.is_pinned = not self.is_pinned

        # Update pin button appearance
        if self.is_pinned:
            self.pin_button.setText("📍")  # Pinned icon
            self.pin_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 200, 0, 0.3);
                    color: #ffffff;
                    border: 1px solid rgba(0, 200, 0, 0.6);
                    border-radius: 12px;
                    font-size: 10pt;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 200, 0, 0.4);
                    border: 1px solid rgba(0, 200, 0, 0.8);
                }
                QPushButton:pressed {
                    background-color: rgba(0, 200, 0, 0.5);
                }
            """)
            self.pin_button.setToolTip("Desanclar panel")

            # Show minimize and config buttons when pinned
            self.minimize_button.setVisible(True)
            self.config_button.setVisible(True)
            logger.info(f"Panel '{self.header_label.text()}' ANCLADO - puede abrir otros paneles")
        else:
            self.pin_button.setText("📌")  # Unpinned icon
            self.pin_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 12px;
                    font-size: 10pt;
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
            self.pin_button.setToolTip("Anclar panel (permite abrir múltiples paneles)")

            # Hide minimize and config buttons when unpinned
            self.minimize_button.setVisible(False)
            self.config_button.setVisible(False)

            # If panel was minimized, restore it before unpinning
            if self.is_minimized:
                self.toggle_minimize()  # Restore to normal state

            logger.info(f"Panel '{self.header_label.text()}' DESANCLADO")

        # Emit signal
        self.pin_state_changed.emit(self.is_pinned)

    def toggle_minimize(self):
        """Toggle panel minimize state (only for pinned panels)"""
        if not self.is_pinned:
            logger.warning("Cannot minimize unpinned panel")
            return  # Only allow minimize for pinned panels

        self.is_minimized = not self.is_minimized

        if self.is_minimized:
            # Save current size and position
            self.normal_height = self.height()
            self.normal_width = self.width()
            self.normal_position = self.pos()
            logger.info(f"Minimizing panel - saving size: {self.normal_width}x{self.normal_height}, position: {self.normal_position}")

            # Hide content widgets
            self.filters_button_widget.setVisible(False)
            self.search_bar.setVisible(False)
            self.scroll_area.setVisible(False)

            # Reduce header margins for compact look
            self.header_layout.setContentsMargins(8, 3, 5, 3)

            # CRITICAL: Remove size constraints temporarily to allow small size
            self.setMinimumWidth(0)
            self.setMinimumHeight(0)

            # Resize to compact size (height: 32px, width: ~180px)
            minimized_height = 32
            minimized_width = 180
            self.resize(minimized_width, minimized_height)

            # Move to bottom of screen (al ras de la barra de tareas)
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                # Position al ras de la barra de tareas (5px margin)
                new_x = self.x()  # Keep same X position
                new_y = screen_geometry.bottom() - minimized_height - 5  # 5px margin - al ras de taskbar
                self.move(new_x, new_y)
                logger.info(f"Moved minimized panel to bottom: ({new_x}, {new_y})")

            # Update button
            self.minimize_button.setText("□")
            self.minimize_button.setToolTip("Maximizar panel")
            logger.info(f"Panel '{self.header_label.text()}' MINIMIZADO")
        else:
            # Restore content widgets
            self.filters_button_widget.setVisible(True)
            self.search_bar.setVisible(True)
            self.scroll_area.setVisible(True)

            # Restore header margins
            self.header_layout.setContentsMargins(15, 10, 10, 10)

            # CRITICAL: Restore size constraints
            self.setMinimumWidth(300)
            self.setMinimumHeight(400)

            # Restore original size
            if self.normal_height and self.normal_width:
                self.resize(self.normal_width, self.normal_height)
                logger.info(f"Restored panel size to: {self.normal_width}x{self.normal_height}")
            else:
                # Fallback: use default size
                from PyQt6.QtWidgets import QApplication
                screen = QApplication.primaryScreen()
                if screen:
                    screen_height = screen.availableGeometry().height()
                    window_height = int(screen_height * 0.8)
                    self.resize(self.panel_width, window_height)
                    logger.info(f"Restored panel size to default: {self.panel_width}x{window_height}")

            # Restore original position
            if self.normal_position:
                self.move(self.normal_position)
                logger.info(f"Restored panel position to: {self.normal_position}")

            # Update button
            self.minimize_button.setText("−")
            self.minimize_button.setToolTip("Minimizar panel")
            logger.info(f"Panel '{self.header_label.text()}' MAXIMIZADO")

    def apply_custom_styling(self):
        """Apply custom color to panel header if custom_color is set"""
        if self.custom_color:
            self.header_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {self.custom_color};
                    border-radius: 6px 6px 0 0;
                }}
            """)
            logger.info(f"Applied custom color to panel: {self.custom_color}")
        else:
            # Restore default styling
            self.header_widget.setStyleSheet("""
                QWidget {
                    background-color: #007acc;
                    border-radius: 6px 6px 0 0;
                }
            """)
            logger.debug("Restored default header color")

    def get_display_name(self) -> str:
        """Get name to display in header (custom name takes priority over category name)"""
        if self.custom_name:
            return self.custom_name
        elif self.current_category:
            return self.current_category.name
        else:
            return "Select a category"

    def update_header_title(self):
        """Update the header label with current display name"""
        display_name = self.get_display_name()
        self.header_label.setText(display_name)
        logger.debug(f"Updated header title to: {display_name}")

    def update_customization(self, custom_name: str = None, custom_color: str = None):
        """Update panel customization (name and/or color)

        Args:
            custom_name: New custom name (None to keep unchanged)
            custom_color: New custom color in hex format (None to keep unchanged)
        """
        if custom_name is not None:
            self.custom_name = custom_name
            self.update_header_title()
            logger.info(f"Updated panel custom name to: {custom_name}")

        if custom_color is not None:
            self.custom_color = custom_color
            self.apply_custom_styling()
            logger.info(f"Updated panel custom color to: {custom_color}")

    def on_config_clicked(self):
        """Handle config button click - emit signal for parent to handle"""
        logger.info(f"Config button clicked for panel: {self.get_display_name()}")
        self.customization_requested.emit()

    def closeEvent(self, event):
        """Handle window close event"""
        # Cerrar también la ventana de filtros si está abierta
        if self.filters_window.isVisible():
            self.filters_window.close()

        self.window_closed.emit()
        event.accept()

    def moveEvent(self, event):
        """AUTO-UPDATE: Handle window move event - save position to database (debounced)"""
        super().moveEvent(event)

        # Only save if this is a pinned panel with a panel_id
        if self.is_pinned and self.panel_id and self.config_manager:
            # Restart the debounce timer
            self.update_timer.start(self.update_delay_ms)

    def resizeEvent(self, event):
        """AUTO-UPDATE: Handle window resize event - save size to database (debounced)"""
        super().resizeEvent(event)

        # Only save if this is a pinned panel with a panel_id
        if self.is_pinned and self.panel_id and self.config_manager:
            # Restart the debounce timer
            self.update_timer.start(self.update_delay_ms)

    def _save_panel_state_to_db(self):
        """AUTO-UPDATE: Save current panel state (position/size) to database"""
        # Only save if this is a pinned panel with a valid panel_id
        if not self.is_pinned or not self.panel_id or not self.config_manager:
            return

        try:
            # Get PinnedPanelsManager from main_window via parent chain
            from views.main_window import MainWindow

            # Find MainWindow in parent chain
            main_window = None
            parent = self.parent()
            while parent:
                if isinstance(parent, MainWindow):
                    main_window = parent
                    break
                parent = parent.parent()

            if not main_window or not main_window.controller:
                logger.warning("Could not find MainWindow or controller - skipping panel state save")
                return

            # Get the PinnedPanelsManager
            panels_manager = main_window.controller.pinned_panels_manager

            # Update panel state in database
            panels_manager.update_panel_state(
                panel_id=self.panel_id,
                panel_widget=self
            )

            logger.debug(f"Panel {self.panel_id} state auto-saved to database (Position: {self.pos()}, Size: {self.size()})")

        except Exception as e:
            logger.error(f"Error auto-saving panel state: {e}", exc_info=True)
