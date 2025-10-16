"""
Category Editor
Widget for editing categories and their items
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.category import Category
from models.item import Item, ItemType
from views.item_editor_dialog import ItemEditorDialog


class CategoryEditor(QWidget):
    """
    Category and item editor widget
    Two-column layout with categories list and items list
    """

    # Signal emitted when data changes
    data_changed = pyqtSignal()

    def __init__(self, controller=None, parent=None):
        """
        Initialize category editor

        Args:
            controller: MainController instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.controller = controller
        self.categories = []
        self.current_category = None

        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Left column - Categories
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        # Categories label
        categories_label = QLabel("Categorías")
        categories_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        left_layout.addWidget(categories_label)

        # Categories list
        self.categories_list = QListWidget()
        self.categories_list.setFixedWidth(200)
        self.categories_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.categories_list.itemSelectionChanged.connect(self.on_category_selected)
        self.categories_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
        """)
        left_layout.addWidget(self.categories_list)

        # Category buttons
        cat_buttons_layout = QHBoxLayout()
        cat_buttons_layout.setSpacing(5)

        self.add_cat_button = QPushButton("+")
        self.add_cat_button.setFixedSize(40, 30)
        self.add_cat_button.setToolTip("Agregar categoría")
        self.add_cat_button.clicked.connect(self.add_category)

        self.delete_cat_button = QPushButton("-")
        self.delete_cat_button.setFixedSize(40, 30)
        self.delete_cat_button.setToolTip("Eliminar categoría")
        self.delete_cat_button.clicked.connect(self.delete_category)
        self.delete_cat_button.setEnabled(False)

        cat_buttons_layout.addWidget(self.add_cat_button)
        cat_buttons_layout.addWidget(self.delete_cat_button)
        cat_buttons_layout.addStretch()

        left_layout.addLayout(cat_buttons_layout)

        main_layout.addLayout(left_layout)

        # Right column - Items
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        # Items label
        self.items_label = QLabel("Items")
        self.items_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        right_layout.addWidget(self.items_label)

        # Items list
        self.items_list = QListWidget()
        self.items_list.setMinimumWidth(280)
        self.items_list.itemSelectionChanged.connect(self.on_item_selected)
        self.items_list.itemDoubleClicked.connect(lambda: self.edit_item())
        self.items_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
        """)
        right_layout.addWidget(self.items_list)

        # Item buttons
        item_buttons_layout = QHBoxLayout()
        item_buttons_layout.setSpacing(5)

        self.add_item_button = QPushButton("+")
        self.add_item_button.setFixedSize(40, 30)
        self.add_item_button.setToolTip("Agregar item")
        self.add_item_button.clicked.connect(self.add_item)
        self.add_item_button.setEnabled(False)

        self.edit_item_button = QPushButton("✎")
        self.edit_item_button.setFixedSize(40, 30)
        self.edit_item_button.setToolTip("Editar item")
        self.edit_item_button.clicked.connect(self.edit_item)
        self.edit_item_button.setEnabled(False)

        self.delete_item_button = QPushButton("-")
        self.delete_item_button.setFixedSize(40, 30)
        self.delete_item_button.setToolTip("Eliminar item")
        self.delete_item_button.clicked.connect(self.delete_item)
        self.delete_item_button.setEnabled(False)

        item_buttons_layout.addWidget(self.add_item_button)
        item_buttons_layout.addWidget(self.edit_item_button)
        item_buttons_layout.addWidget(self.delete_item_button)
        item_buttons_layout.addStretch()

        right_layout.addLayout(item_buttons_layout)

        main_layout.addLayout(right_layout)

        # Apply button styles
        button_style = """
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #007acc;
            }
            QPushButton:disabled {
                background-color: #252525;
                color: #555555;
                border: 1px solid #2d2d2d;
            }
        """
        self.add_cat_button.setStyleSheet(button_style)
        self.delete_cat_button.setStyleSheet(button_style)
        self.add_item_button.setStyleSheet(button_style)
        self.edit_item_button.setStyleSheet(button_style)
        self.delete_item_button.setStyleSheet(button_style)

    def load_categories(self):
        """Load categories from controller"""
        if not self.controller:
            return

        self.categories = self.controller.get_categories()
        self.refresh_categories_list()

    def refresh_categories_list(self):
        """Refresh the categories list widget"""
        self.categories_list.clear()

        for category in self.categories:
            item = QListWidgetItem(f"{category.name} ({len(category.items)})")
            item.setData(Qt.ItemDataRole.UserRole, category)
            self.categories_list.addItem(item)

    def on_category_selected(self):
        """Handle category selection"""
        selected_items = self.categories_list.selectedItems()

        if not selected_items:
            self.current_category = None
            self.items_list.clear()
            self.items_label.setText("Items")
            self.delete_cat_button.setEnabled(False)
            self.add_item_button.setEnabled(False)
            return

        # Get selected category
        item = selected_items[0]
        self.current_category = item.data(Qt.ItemDataRole.UserRole)

        # Update items list
        self.refresh_items_list()

        # Update label
        self.items_label.setText(f"Items - {self.current_category.name}")

        # Enable buttons
        self.delete_cat_button.setEnabled(True)
        self.add_item_button.setEnabled(True)

    def refresh_items_list(self):
        """Refresh the items list for current category"""
        self.items_list.clear()

        if not self.current_category:
            return

        for item in self.current_category.items:
            list_item = QListWidgetItem(f"{item.label}")
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.items_list.addItem(list_item)

    def on_item_selected(self):
        """Handle item selection"""
        selected = len(self.items_list.selectedItems()) > 0
        self.edit_item_button.setEnabled(selected)
        self.delete_item_button.setEnabled(selected)

    def add_category(self):
        """Add new category"""
        name, ok = QInputDialog.getText(
            self,
            "Nueva Categoría",
            "Nombre de la categoría:"
        )

        if not ok or not name.strip():
            return

        # Create new category
        category_id = f"custom_{uuid.uuid4().hex[:8]}"
        new_category = Category(
            category_id=category_id,
            name=name.strip(),
            icon="",
            order=len(self.categories),
            is_active=True
        )

        self.categories.append(new_category)
        self.refresh_categories_list()
        self.data_changed.emit()

    def delete_category(self):
        """Delete selected category"""
        if not self.current_category:
            return

        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Eliminar Categoría",
            f"¿Eliminar la categoría '{self.current_category.name}' y todos sus items?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.categories.remove(self.current_category)
            self.current_category = None
            self.refresh_categories_list()
            self.items_list.clear()
            self.data_changed.emit()

    def add_item(self):
        """Add new item to current category"""
        if not self.current_category:
            return

        dialog = ItemEditorDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item_data = dialog.get_item_data()

            # Create new item
            item_id = f"item_{uuid.uuid4().hex[:8]}"
            new_item = Item(
                item_id=item_id,
                label=item_data["label"],
                content=item_data["content"],
                item_type=item_data["type"],
                tags=item_data["tags"]
            )

            self.current_category.add_item(new_item)
            self.refresh_items_list()
            self.refresh_categories_list()  # Update count
            self.data_changed.emit()

    def edit_item(self):
        """Edit selected item"""
        selected_items = self.items_list.selectedItems()
        if not selected_items or not self.current_category:
            return

        # Get selected item
        list_item = selected_items[0]
        item = list_item.data(Qt.ItemDataRole.UserRole)

        dialog = ItemEditorDialog(item=item, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item_data = dialog.get_item_data()

            # Update item
            item.label = item_data["label"]
            item.content = item_data["content"]
            item.type = item_data["type"]
            item.tags = item_data["tags"]

            self.refresh_items_list()
            self.data_changed.emit()

    def delete_item(self):
        """Delete selected item"""
        selected_items = self.items_list.selectedItems()
        if not selected_items or not self.current_category:
            return

        # Get selected item
        list_item = selected_items[0]
        item = list_item.data(Qt.ItemDataRole.UserRole)

        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Eliminar Item",
            f"¿Eliminar el item '{item.label}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.current_category.remove_item(item.id)
            self.refresh_items_list()
            self.refresh_categories_list()  # Update count
            self.data_changed.emit()

    def get_categories(self):
        """
        Get current categories list

        Returns:
            List of categories
        """
        return self.categories
