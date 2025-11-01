"""
Structure Dashboard
Main window for visualizing global structure of categories and items
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QWidget, QApplication, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QBrush, QColor, QShortcut, QKeySequence
import logging

from core.dashboard_manager import DashboardManager
from views.dashboard.search_bar_widget import SearchBarWidget
from views.dashboard.highlight_delegate import HighlightDelegate

logger = logging.getLogger(__name__)


class StructureDashboard(QDialog):
    """Dashboard window for viewing global structure"""

    # Signal emitted when user wants to navigate to a category
    navigate_to_category = pyqtSignal(int)  # category_id

    def __init__(self, db_manager, parent=None):
        """
        Initialize the structure dashboard

        Args:
            db_manager: DBManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager
        self.dashboard_manager = DashboardManager(db_manager)
        self.structure = None
        self.current_matches = []  # Store current search matches
        self.highlight_delegate = None  # Will be set in init_ui
        self.is_custom_maximized = False  # Track custom maximize state

        # For window dragging
        self.dragging = False
        self.drag_position = None
        self.normal_geometry = None  # Store normal size for restore

        self.init_ui()
        self.setup_shortcuts()
        self.load_data()

    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("Dashboard de Estructura - Widget Sidebar")
        self.setModal(False)  # Changed to non-modal so it doesn't block main window
        self.resize(1200, 800)

        # Set window flags to stay behind the main sidebar
        self.setWindowFlags(
            Qt.WindowType.Window |  # Normal window
            Qt.WindowType.CustomizeWindowHint  # Allow custom buttons
        )

        # Center window on screen
        self.center_on_screen()

        # Apply dark theme
        self.apply_dark_theme()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)

        # Search Bar
        self.search_bar = SearchBarWidget()
        self.search_bar.search_changed.connect(self.on_search_changed)
        self.search_bar.navigate_to_result.connect(self.navigate_to_result)
        main_layout.addWidget(self.search_bar)

        # TreeView
        self.tree_widget = self.create_tree_widget()
        main_layout.addWidget(self.tree_widget)

        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)

        logger.info("StructureDashboard UI initialized")

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+F to focus search
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.search_bar.focus_search)

        # F3 to navigate to next result
        next_shortcut = QShortcut(QKeySequence("F3"), self)
        next_shortcut.activated.connect(self.search_bar.navigate_next)

        # Shift+F3 to navigate to previous result
        prev_shortcut = QShortcut(QKeySequence("Shift+F3"), self)
        prev_shortcut.activated.connect(self.search_bar.navigate_previous)

        # Escape to clear search
        esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        esc_shortcut.activated.connect(self.search_bar.clear_search)

        logger.info("Keyboard shortcuts configured: Ctrl+F, F3, Shift+F3, Esc")

    def center_on_screen(self):
        """Center the window on the screen"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    def apply_dark_theme(self):
        """Apply dark theme stylesheet"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QTreeWidget {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                outline: none;
            }
            QTreeWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QTreeWidget::item:hover {
                background-color: #2d2d2d;
            }
            QTreeWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QTreeWidget::branch {
                background-color: #252525;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                image: url(none);
                border-image: none;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                image: url(none);
                border-image: none;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-right: 1px solid #3d3d3d;
                font-weight: bold;
            }
        """)

    def create_header(self) -> QWidget:
        """Create header widget with title and buttons"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-bottom: 1px solid #3d3d3d;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 10, 10)  # Reduced right margin
        layout.setSpacing(8)  # Add spacing between elements

        # Draggable title area
        self.title_label = QLabel("📊 Dashboard de Estructura")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setCursor(Qt.CursorShape.SizeAllCursor)  # Show move cursor
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                padding: 5px;
            }
        """)

        # Install event filter to capture mouse events on title
        self.title_label.mousePressEvent = self.header_mouse_press
        self.title_label.mouseMoveEvent = self.header_mouse_move
        self.title_label.mouseReleaseEvent = self.header_mouse_release

        layout.addWidget(self.title_label)

        layout.addStretch()

        # Filter buttons
        fav_btn = QPushButton("⭐ Favoritos")
        fav_btn.setToolTip("Mostrar solo items favoritos")
        fav_btn.clicked.connect(self.filter_favorites)
        layout.addWidget(fav_btn)

        sort_btn = QPushButton("🔢 +Items")
        sort_btn.setToolTip("Ordenar por cantidad de items (desc)")
        sort_btn.clicked.connect(self.sort_by_items)
        layout.addWidget(sort_btn)

        reset_btn = QPushButton("↺ Todo")
        reset_btn.setToolTip("Mostrar todo sin filtros")
        reset_btn.clicked.connect(self.reset_filters)
        layout.addWidget(reset_btn)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refrescar")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)

        # Add spacer before window controls
        layout.addSpacing(20)

        # Window control buttons - with better visibility
        window_controls_style = """
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 18pt;
                font-weight: bold;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-radius: 4px;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
        """

        # Minimize button
        minimize_btn = QPushButton("─")
        minimize_btn.setToolTip("Minimizar")
        minimize_btn.setFixedSize(40, 35)
        minimize_btn.setStyleSheet(window_controls_style)
        minimize_btn.clicked.connect(self.showMinimized)
        layout.addWidget(minimize_btn)

        # Maximize/Restore button
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setToolTip("Maximizar")
        self.maximize_btn.setFixedSize(40, 35)
        self.maximize_btn.setStyleSheet(window_controls_style)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.maximize_btn)

        # Close button - with red hover
        close_btn = QPushButton("✕")
        close_btn.setToolTip("Cerrar")
        close_btn.setFixedSize(40, 35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 18pt;
                font-weight: bold;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #e81123;
                border-radius: 4px;
            }
            QPushButton:pressed {
                background-color: #c50d1d;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return header

    def create_tree_widget(self) -> QTreeWidget:
        """Create the main tree widget"""
        tree = QTreeWidget()
        tree.setHeaderLabels(["Nombre", "Tipo", "Info"])
        tree.setColumnWidth(0, 400)
        tree.setColumnWidth(1, 100)
        tree.setColumnWidth(2, 600)

        # Enable alternating row colors
        tree.setAlternatingRowColors(True)

        # Enable animations
        tree.setAnimated(True)

        # Set custom delegate for highlighting
        self.highlight_delegate = HighlightDelegate(tree)
        tree.setItemDelegateForColumn(0, self.highlight_delegate)  # Highlight in column 0 (Name)
        tree.setItemDelegateForColumn(2, self.highlight_delegate)  # Highlight in column 2 (Info)

        # Double click to copy content
        tree.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Enable context menu
        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.show_context_menu)

        return tree

    def create_footer(self) -> QWidget:
        """Create footer widget with statistics"""
        footer = QWidget()
        footer.setFixedHeight(40)
        footer.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-top: 1px solid #3d3d3d;
            }
        """)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 10, 20, 10)

        # Statistics label
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self.stats_label)

        layout.addStretch()

        # Action buttons
        expand_btn = QPushButton("Expandir Todo")
        expand_btn.clicked.connect(self.tree_widget.expandAll)
        expand_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        layout.addWidget(expand_btn)

        collapse_btn = QPushButton("Colapsar Todo")
        collapse_btn.clicked.connect(self.tree_widget.collapseAll)
        collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        layout.addWidget(collapse_btn)

        return footer

    def load_data(self):
        """Load data from database and populate tree"""
        logger.info("Loading dashboard data...")

        try:
            # Get structure
            self.structure = self.dashboard_manager.get_full_structure()

            # Clear tree
            self.tree_widget.clear()

            # Populate tree
            self.populate_tree(self.structure)

            # Update statistics
            self.update_statistics()

            logger.info("Dashboard data loaded successfully")

        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}", exc_info=True)
            self.stats_label.setText("❌ Error al cargar datos")

    def populate_tree(self, structure: dict):
        """
        Populate tree widget with structure data

        Args:
            structure: Structure dict from DashboardManager
        """
        categories = structure.get('categories', [])

        logger.info(f"Populating tree with {len(categories)} categories...")

        for category in categories:
            # Create category item (Level 1)
            category_item = QTreeWidgetItem(self.tree_widget)

            # Column 0: Name with icon and item count
            category_name = f"{category['icon']} {category['name']} ({len(category['items'])} items)"
            category_item.setText(0, category_name)
            category_item.setFont(0, self.get_bold_font())

            # Column 1: Type
            category_item.setText(1, "Categoría")

            # Column 2: Tags
            if category['tags']:
                tags_str = ", ".join([f"#{tag}" for tag in category['tags']])
                category_item.setText(2, tags_str)

            # Build tooltip for category
            category_tooltip_parts = []
            category_tooltip_parts.append(f"<b>{category['name']}</b>")
            category_tooltip_parts.append(f"<b>Items:</b> {len(category['items'])}")

            if category['tags']:
                tags_str = ", ".join([f"#{tag}" for tag in category['tags']])
                category_tooltip_parts.append(f"<b>Tags:</b> {tags_str}")

            if category.get('is_predefined'):
                category_tooltip_parts.append("📌 <b>Categoría predefinida</b>")

            category_tooltip_parts.append("<br><i>Click para expandir/colapsar | Click derecho para opciones</i>")

            category_tooltip_html = "<br>".join(category_tooltip_parts)
            category_item.setToolTip(0, category_tooltip_html)
            category_item.setToolTip(1, category_tooltip_html)
            category_item.setToolTip(2, category_tooltip_html)

            # Store category ID in user data
            category_item.setData(0, Qt.ItemDataRole.UserRole, {
                'type': 'category',
                'id': category['id']
            })

            # Add items under this category (Level 2)
            for item in category['items']:
                item_widget = QTreeWidgetItem(category_item)

                # Column 0: Item name with indicators
                indicators = ""
                if item.get('is_list'):
                    indicators += "📝 "
                if item['is_favorite']:
                    indicators += "⭐ "
                if item['is_sensitive']:
                    indicators += "🔒 "

                item_name = f"{indicators}{item['label']}"
                item_widget.setText(0, item_name)

                # Column 1: Item type
                type_icons = {
                    'CODE': '💻',
                    'URL': '🔗',
                    'PATH': '📂',
                    'TEXT': '📝'
                }
                type_icon = type_icons.get(item['type'], '📄')
                item_widget.setText(1, f"{type_icon} {item['type']}")

                # Column 2: Tags + list_group + preview
                info_parts = []

                # List group (if is_list)
                if item.get('is_list') and item.get('list_group'):
                    info_parts.append(f"📝 Lista: {item['list_group']}")

                # Tags
                if item['tags']:
                    tags_str = ", ".join([f"#{tag}" for tag in item['tags']])
                    info_parts.append(tags_str)

                # Content preview (first 50 chars)
                if not item['is_sensitive'] and item['content']:
                    preview = item['content'][:50]
                    if len(item['content']) > 50:
                        preview += "..."
                    info_parts.append(f"Preview: {preview}")

                item_widget.setText(2, " | ".join(info_parts))

                # Build tooltip with detailed information
                tooltip_parts = []
                tooltip_parts.append(f"<b>{item['label']}</b>")
                tooltip_parts.append(f"<b>Tipo:</b> {item['type']}")

                if item['description']:
                    tooltip_parts.append(f"<b>Descripción:</b> {item['description']}")

                if item.get('is_list') and item.get('list_group'):
                    tooltip_parts.append(f"📝 <b>Pertenece a la lista:</b> {item['list_group']}")

                if item['tags']:
                    tags_str = ", ".join([f"#{tag}" for tag in item['tags']])
                    tooltip_parts.append(f"<b>Tags:</b> {tags_str}")

                if item['is_favorite']:
                    tooltip_parts.append("⭐ <b>Favorito</b>")

                if item['is_sensitive']:
                    tooltip_parts.append("🔒 <b>Contenido sensible (encriptado)</b>")
                else:
                    # Show content preview for non-sensitive items
                    if item['content']:
                        content_preview = item['content'][:100]
                        if len(item['content']) > 100:
                            content_preview += "..."
                        tooltip_parts.append(f"<b>Contenido:</b><br><code>{content_preview}</code>")

                tooltip_parts.append("<br><i>Doble click para copiar | Click derecho para más opciones</i>")

                tooltip_html = "<br>".join(tooltip_parts)
                item_widget.setToolTip(0, tooltip_html)
                item_widget.setToolTip(1, tooltip_html)
                item_widget.setToolTip(2, tooltip_html)

                # Store item data
                item_widget.setData(0, Qt.ItemDataRole.UserRole, {
                    'type': 'item',
                    'id': item['id'],
                    'content': item['content'],
                    'item_type': item['type']
                })

        logger.info("Tree populated successfully")

    def update_statistics(self):
        """Update statistics label"""
        if not self.structure:
            return

        stats = self.dashboard_manager.calculate_statistics(self.structure)

        # Build detailed statistics text
        stats_parts = [
            f"📊 {stats['total_categories']} cat.",
            f"📄 {stats['total_items']} items",
            f"⭐ {stats['total_favorites']} fav.",
            f"🔒 {stats['total_sensitive']} sens.",
            f"🏷️ {stats['total_unique_tags']} tags"
        ]

        # Add most used tag if available
        if stats.get('most_used_tag'):
            stats_parts.append(f"🔥 #{stats['most_used_tag']}")

        # Add average items per category
        if stats.get('avg_items_per_category', 0) > 0:
            stats_parts.append(f"📈 {stats['avg_items_per_category']} prom/cat")

        stats_text = " | ".join(stats_parts)
        self.stats_label.setText(stats_text)

    def get_bold_font(self) -> QFont:
        """Get bold font for categories"""
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        return font

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double click on tree item"""
        data = item.data(0, Qt.ItemDataRole.UserRole)

        if not data:
            return

        if data['type'] == 'item':
            # Copy item content to clipboard
            content = data.get('content', '')
            if content:
                clipboard = QApplication.clipboard()
                clipboard.setText(content)
                logger.info(f"Copied item content to clipboard")
                self.stats_label.setText("✅ Contenido copiado al portapapeles")
                # Reset message after 2 seconds
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(2000, lambda: self.update_statistics())

    def filter_favorites(self):
        """Show only favorite items"""
        logger.info("Filtering favorites...")
        state_filters = {'favorites': True, 'sensitive': False, 'normal': False}
        filtered_structure = self.dashboard_manager.filter_and_sort_structure(
            structure=self.structure,
            state_filters=state_filters
        )
        self.tree_widget.clear()
        self.populate_tree(filtered_structure)
        self.stats_label.setText("🔍 Mostrando solo favoritos")

    def sort_by_items(self):
        """Sort by item count descending"""
        logger.info("Sorting by items count...")
        sorted_structure = self.dashboard_manager.filter_and_sort_structure(
            structure=self.structure,
            sort_by='items_desc'
        )
        self.tree_widget.clear()
        self.populate_tree(sorted_structure)
        self.stats_label.setText("🔢 Ordenado por cantidad de items")

    def reset_filters(self):
        """Reset all filters and show all data"""
        logger.info("Resetting filters...")
        # Clear search
        self.search_bar.clear_search()
        # Reload full structure
        self.tree_widget.clear()
        self.populate_tree(self.structure)
        self.update_statistics()

    def refresh_data(self):
        """Refresh data from database"""
        logger.info("Refreshing dashboard data...")
        self.stats_label.setText("🔄 Refrescando datos...")
        self.load_data()

    def on_search_changed(self, query: str, scope_filters: dict):
        """Handle search query change"""
        logger.info(f"Search changed - Query: '{query}', Filters: {scope_filters}")

        # Update highlight delegate with search query
        if self.highlight_delegate:
            self.highlight_delegate.set_search_query(query)

        # Clear previous highlighting
        self.clear_highlighting()

        if not query:
            # If empty query, show all items
            self.show_all_items()
            self.search_bar.set_results_count(0)
            self.current_matches = []
            # Refresh tree to remove highlights
            self.tree_widget.viewport().update()
            return

        # Perform search
        matches = self.dashboard_manager.search(query, scope_filters, self.structure)
        self.current_matches = matches

        # Filter tree to show only matches
        self.filter_tree_by_matches(matches)

        # Update results counter
        self.search_bar.set_results_count(len(matches))

        # Refresh tree to apply highlights
        self.tree_widget.viewport().update()

        # Navigate to first result
        if matches:
            self.navigate_to_result(0)

        logger.info(f"Search found {len(matches)} matches")

    def clear_highlighting(self):
        """Clear all highlighting in tree"""
        root = self.tree_widget.invisibleRootItem()

        for cat_idx in range(root.childCount()):
            category_item = root.child(cat_idx)

            # Reset category background
            for col in range(3):
                category_item.setBackground(col, QBrush(QColor('#252525')))

            # Reset items background
            for item_idx in range(category_item.childCount()):
                item_widget = category_item.child(item_idx)
                for col in range(3):
                    item_widget.setBackground(col, QBrush(QColor('#252525')))

    def highlight_matches(self, matches: list):
        """
        Highlight matching items in tree

        Args:
            matches: List of (match_type, category_index, item_index) tuples
        """
        root = self.tree_widget.invisibleRootItem()
        highlight_color = QColor('#3d5a80')  # Dark blue for highlights

        for match_type, cat_idx, item_idx in matches:
            if cat_idx >= root.childCount():
                continue

            category_item = root.child(cat_idx)

            if item_idx == -1:
                # Highlight category
                for col in range(3):
                    category_item.setBackground(col, QBrush(highlight_color))
                # Expand category to show items
                category_item.setExpanded(True)
            else:
                # Highlight item
                if item_idx < category_item.childCount():
                    item_widget = category_item.child(item_idx)
                    for col in range(3):
                        item_widget.setBackground(col, QBrush(highlight_color))
                    # Expand category to show highlighted item
                    category_item.setExpanded(True)

    def show_all_items(self):
        """Show all items in tree"""
        root = self.tree_widget.invisibleRootItem()

        for cat_idx in range(root.childCount()):
            category_item = root.child(cat_idx)
            category_item.setHidden(False)

            # Show all items in category
            for item_idx in range(category_item.childCount()):
                item_widget = category_item.child(item_idx)
                item_widget.setHidden(False)

    def navigate_to_result(self, result_index: int):
        """
        Navigate to specific search result by scrolling and selecting it

        Args:
            result_index: Index of the result to navigate to (0-based)
        """
        if result_index < 0 or result_index >= len(self.current_matches):
            logger.warning(f"Invalid result index: {result_index}")
            return

        match_type, cat_idx, item_idx = self.current_matches[result_index]
        root = self.tree_widget.invisibleRootItem()

        if cat_idx >= root.childCount():
            logger.warning(f"Invalid category index: {cat_idx}")
            return

        category_item = root.child(cat_idx)

        # Clear previous selection
        self.tree_widget.clearSelection()

        if item_idx == -1:
            # Navigate to category
            category_item.setExpanded(True)
            category_item.setSelected(True)
            self.tree_widget.scrollToItem(category_item, QTreeWidget.ScrollHint.PositionAtCenter)
            logger.debug(f"Navigated to category at index {cat_idx}")
        else:
            # Navigate to item
            if item_idx < category_item.childCount():
                category_item.setExpanded(True)
                item_widget = category_item.child(item_idx)
                item_widget.setSelected(True)
                self.tree_widget.scrollToItem(item_widget, QTreeWidget.ScrollHint.PositionAtCenter)
                logger.debug(f"Navigated to item at cat:{cat_idx}, item:{item_idx}")
            else:
                logger.warning(f"Invalid item index: {item_idx}")

    def filter_tree_by_matches(self, matches: list):
        """
        Filter tree to show only matching items

        Args:
            matches: List of (match_type, category_index, item_index) tuples
        """
        root = self.tree_widget.invisibleRootItem()

        # Create set of matching category and item indices for quick lookup
        matching_categories = set()
        matching_items = {}  # {cat_idx: set(item_indices)}

        for match_type, cat_idx, item_idx in matches:
            matching_categories.add(cat_idx)
            if item_idx != -1:
                if cat_idx not in matching_items:
                    matching_items[cat_idx] = set()
                matching_items[cat_idx].add(item_idx)

        # Hide/show categories and items based on matches
        for cat_idx in range(root.childCount()):
            category_item = root.child(cat_idx)

            # Check if this category has any matches
            if cat_idx in matching_categories:
                # Category has matches - show it
                category_item.setHidden(False)
                category_item.setExpanded(True)

                # If category itself matched, show all its items
                category_matched = any(
                    m[1] == cat_idx and m[2] == -1
                    for m in matches
                )

                if category_matched:
                    # Show all items in this category
                    for item_idx in range(category_item.childCount()):
                        item_widget = category_item.child(item_idx)
                        item_widget.setHidden(False)
                else:
                    # Only show matching items
                    cat_matching_items = matching_items.get(cat_idx, set())
                    for item_idx in range(category_item.childCount()):
                        item_widget = category_item.child(item_idx)
                        item_widget.setHidden(item_idx not in cat_matching_items)
            else:
                # No matches in this category - hide it
                category_item.setHidden(True)

    def show_context_menu(self, position):
        """Show context menu on right-click"""
        item = self.tree_widget.itemAt(position)

        if not item:
            return

        data = item.data(0, Qt.ItemDataRole.UserRole)

        if not data:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #007acc;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3d3d3d;
                margin: 5px 10px;
            }
        """)

        if data['type'] == 'item':
            # Item context menu
            copy_action = menu.addAction("📋 Copiar contenido")
            copy_action.triggered.connect(lambda: self.copy_item_content(data))

            menu.addSeparator()

            details_action = menu.addAction("ℹ️ Ver detalles")
            details_action.triggered.connect(lambda: self.show_item_details(item, data))

        elif data['type'] == 'category':
            # Category context menu
            if item.isExpanded():
                collapse_action = menu.addAction("➖ Colapsar")
                collapse_action.triggered.connect(lambda: item.setExpanded(False))
            else:
                expand_action = menu.addAction("➕ Expandir")
                expand_action.triggered.connect(lambda: item.setExpanded(True))

            menu.addSeparator()

            expand_all_action = menu.addAction("⬇️ Expandir todo")
            expand_all_action.triggered.connect(self.tree_widget.expandAll)

            collapse_all_action = menu.addAction("⬆️ Colapsar todo")
            collapse_all_action.triggered.connect(self.tree_widget.collapseAll)

        # Show menu at cursor position
        menu.exec(self.tree_widget.viewport().mapToGlobal(position))
        logger.debug(f"Context menu shown for {data['type']}")

    def copy_item_content(self, data: dict):
        """Copy item content to clipboard"""
        content = data.get('content', '')
        if content:
            clipboard = QApplication.clipboard()
            clipboard.setText(content)
            self.stats_label.setText("✅ Contenido copiado al portapapeles")
            logger.info(f"Copied item content to clipboard")

            # Reset message after 2 seconds
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.update_statistics())

    def show_item_details(self, item: QTreeWidgetItem, data: dict):
        """Show detailed information about an item"""
        from PyQt6.QtWidgets import QMessageBox

        details = []
        details.append(f"<b>Tipo:</b> {data.get('item_type', 'N/A')}")
        details.append(f"<b>ID:</b> {data.get('id', 'N/A')}")

        # Get item text from tree
        item_name = item.text(0)
        details.append(f"<b>Nombre:</b> {item_name}")

        # Content preview
        content = data.get('content', '')
        if content:
            preview = content[:200]
            if len(content) > 200:
                preview += "..."
            details.append(f"<b>Contenido:</b><br><code>{preview}</code>")

        details_html = "<br><br>".join(details)

        msg = QMessageBox(self)
        msg.setWindowTitle("Detalles del Item")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(details_html)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #ffffff;
                min-width: 400px;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        msg.exec()
        logger.info(f"Showed details for item {data.get('id')}")

    def header_mouse_press(self, event):
        """Handle mouse press on header for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def header_mouse_move(self, event):
        """Handle mouse move on header for dragging"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            # If maximized, restore to normal size first
            if self.is_custom_maximized:
                self.is_custom_maximized = False
                self.showNormal()
                self.maximize_btn.setText("□")
                self.maximize_btn.setToolTip("Maximizar")

            # Move window
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def header_mouse_release(self, event):
        """Handle mouse release after dragging"""
        self.dragging = False
        event.accept()

    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.is_custom_maximized:
            # Restore to saved normal size
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
                logger.debug(f"Restored to saved geometry: {self.normal_geometry}")
            else:
                self.showNormal()
                logger.debug("Restored to normal size (no saved geometry)")

            self.is_custom_maximized = False
            self.maximize_btn.setText("□")
            self.maximize_btn.setToolTip("Maximizar")
        else:
            # Save current geometry before maximizing
            self.normal_geometry = self.geometry()
            logger.debug(f"Saved normal geometry: {self.normal_geometry}")

            # Maximize window, but leave space for the main sidebar
            screen = QApplication.primaryScreen()
            if screen:
                # Get screen geometry
                screen_rect = screen.availableGeometry()

                # Reserve space for sidebar (70px width + some margin)
                sidebar_width = 85  # 70px sidebar + 15px margin

                # Set geometry to cover screen except sidebar area (leave space on the right)
                maximized_rect = screen_rect.adjusted(0, 0, -sidebar_width, 0)
                self.setGeometry(maximized_rect)

                # Set flag
                self.is_custom_maximized = True

                # Update button
                self.maximize_btn.setText("❐")
                self.maximize_btn.setToolTip("Restaurar")
                logger.debug(f"Dashboard maximized with sidebar space: {maximized_rect}")
            else:
                # Fallback to normal maximize if screen not available
                self.showMaximized()
                self.maximize_btn.setText("❐")
                self.maximize_btn.setToolTip("Restaurar")
                logger.debug("Dashboard maximized (fallback)")

    def closeEvent(self, event):
        """Handle window close"""
        logger.info("Structure Dashboard closed")
        event.accept()
