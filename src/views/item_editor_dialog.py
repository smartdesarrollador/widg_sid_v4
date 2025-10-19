"""
Item Editor Dialog
Dialog for creating and editing items
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.item import Item, ItemType


class ItemEditorDialog(QDialog):
    """
    Dialog for creating or editing items
    Modal dialog with form fields for item properties
    """

    def __init__(self, item=None, parent=None):
        """
        Initialize item editor dialog

        Args:
            item: Item to edit (None for new item)
            parent: Parent widget
        """
        super().__init__(parent)
        self.item = item
        self.is_edit_mode = item is not None

        self.init_ui()
        self.load_item_data()

    def init_ui(self):
        """Initialize the dialog UI"""
        # Window properties
        title = "Editar Item" if self.is_edit_mode else "Nuevo Item"
        self.setWindowTitle(title)
        self.setFixedSize(450, 400)
        self.setModal(True)

        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
                font-size: 10pt;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #007acc;
            }
            QPushButton#save_button {
                background-color: #007acc;
                color: #ffffff;
                border: none;
            }
            QPushButton#save_button:hover {
                background-color: #005a9e;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Label field (required)
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Nombre del item")
        form_layout.addRow("Label *:", self.label_input)

        # Type combobox
        self.type_combo = QComboBox()
        for item_type in ItemType:
            self.type_combo.addItem(item_type.value.upper(), item_type)
        form_layout.addRow("Tipo:", self.type_combo)

        # Content field (required, multiline)
        content_label = QLabel("Content *:")
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Contenido a copiar al portapapeles")
        self.content_input.setMinimumHeight(120)
        form_layout.addRow(content_label, self.content_input)

        # Tags field (optional)
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2, tag3 (opcional)")
        form_layout.addRow("Tags:", self.tags_input)

        main_layout.addLayout(form_layout)

        # Required fields note
        note_label = QLabel("* Campos requeridos")
        note_label.setStyleSheet("color: #666666; font-size: 9pt;")
        main_layout.addWidget(note_label)

        # Spacer
        main_layout.addStretch()

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Cancel button
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        buttons_layout.addStretch()

        # Save button
        self.save_button = QPushButton("Guardar")
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.on_save)
        buttons_layout.addWidget(self.save_button)

        main_layout.addLayout(buttons_layout)

    def load_item_data(self):
        """Load existing item data if in edit mode"""
        if not self.is_edit_mode or not self.item:
            return

        # Load item data
        self.label_input.setText(self.item.label)
        self.content_input.setPlainText(self.item.content)

        # Set type combobox
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == self.item.type:
                self.type_combo.setCurrentIndex(i)
                break

        # Load tags
        if self.item.tags:
            self.tags_input.setText(", ".join(self.item.tags))

    def validate(self) -> bool:
        """
        Validate form fields

        Returns:
            True if all fields are valid
        """
        # Check required fields
        label = self.label_input.text().strip()
        content = self.content_input.toPlainText().strip()

        if not label:
            QMessageBox.warning(
                self,
                "Campo requerido",
                "El campo 'Label' es requerido."
            )
            self.label_input.setFocus()
            return False

        if not content:
            QMessageBox.warning(
                self,
                "Campo requerido",
                "El campo 'Content' es requerido."
            )
            self.content_input.setFocus()
            return False

        # Validate URL if type is URL
        selected_type = self.type_combo.currentData()
        if selected_type == ItemType.URL:
            if not self.validate_url(content):
                QMessageBox.warning(
                    self,
                    "URL inválida",
                    "El contenido debe ser una URL válida (http:// o https://)."
                )
                self.content_input.setFocus()
                return False

        # Validate PATH if type is PATH
        if selected_type == ItemType.PATH:
            if not self.validate_path(content):
                # Show warning but allow to save anyway
                reply = QMessageBox.question(
                    self,
                    "Ruta no encontrada",
                    f"La ruta '{content}' no existe en el sistema.\n\n¿Deseas guardarla de todas formas?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    self.content_input.setFocus()
                    return False

        return True

    def validate_url(self, url: str) -> bool:
        """
        Validate URL format

        Args:
            url: URL string to validate

        Returns:
            True if valid URL
        """
        # Simple URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

    def validate_path(self, path_str: str) -> bool:
        """
        Validate if path exists

        Args:
            path_str: Path string to validate

        Returns:
            True if path exists
        """
        try:
            from pathlib import Path
            path = Path(path_str)
            return path.exists()
        except Exception:
            return False

    def get_item_data(self) -> dict:
        """
        Get item data from form fields

        Returns:
            Dictionary with item data
        """
        # Get tags list
        tags_text = self.tags_input.text().strip()
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()] if tags_text else []

        return {
            "label": self.label_input.text().strip(),
            "content": self.content_input.toPlainText().strip(),
            "type": self.type_combo.currentData(),
            "tags": tags
        }

    def on_save(self):
        """Handle save button click"""
        if not self.validate():
            return

        # Accept dialog
        self.accept()
