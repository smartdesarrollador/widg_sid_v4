"""
Panel Configuration Dialog
Dialog to customize pinned panel name and color
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QWidget, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import logging

logger = logging.getLogger(__name__)


class PanelConfigDialog(QDialog):
    """Dialog for customizing pinned panel appearance"""

    # Signal emitted when configuration is saved (custom_name, custom_color)
    config_saved = pyqtSignal(str, str)

    def __init__(self, current_name: str = "", current_color: str = "#007acc", category_name: str = "", parent=None):
        """
        Initialize the panel configuration dialog

        Args:
            current_name: Current custom name (empty if not set)
            current_color: Current custom color in hex format (default: #007acc)
            category_name: Original category name (for reference)
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_name = current_name
        self.current_color = current_color
        self.category_name = category_name
        self.selected_color = current_color  # Track selected color
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Configurar Panel Anclado")
        self.setFixedSize(450, 280)
        self.setModal(True)

        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #252525;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
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
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        # Title
        title = QLabel("Personalizar Panel Anclado")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Category info (if custom name not set)
        if self.category_name:
            info = QLabel(f"Categoria: {self.category_name}")
            info.setStyleSheet("color: #999999; font-size: 9pt;")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(info)

        # Custom name section
        name_label = QLabel("Nombre personalizado:")
        name_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Dejar vacio para usar nombre de categoria")
        self.name_input.setText(self.current_name)
        main_layout.addWidget(self.name_input)

        # Color section
        color_label = QLabel("Color del encabezado:")
        color_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(color_label)

        # Color picker row
        color_row = QHBoxLayout()

        # Color preview widget
        self.color_preview = QWidget()
        self.color_preview.setFixedSize(40, 40)
        self.color_preview.setStyleSheet(f"""
            QWidget {{
                background-color: {self.selected_color};
                border: 2px solid #3d3d3d;
                border-radius: 4px;
            }}
        """)
        color_row.addWidget(self.color_preview)

        # Color hex label
        self.color_label = QLabel(self.selected_color)
        self.color_label.setStyleSheet("font-family: monospace; color: #cccccc;")
        color_row.addWidget(self.color_label)

        color_row.addStretch()

        # Color picker button
        self.color_button = QPushButton("Elegir Color")
        self.color_button.clicked.connect(self.choose_color)
        color_row.addWidget(self.color_button)

        main_layout.addLayout(color_row)

        main_layout.addStretch()

        # Button row
        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        # Reset button
        reset_button = QPushButton("Restablecer")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        reset_button.clicked.connect(self.reset_defaults)
        button_row.addWidget(reset_button)

        button_row.addStretch()

        # Cancel button
        cancel_button = QPushButton("Cancelar")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)

        # Save button
        save_button = QPushButton("Guardar")
        save_button.clicked.connect(self.save_config)
        button_row.addWidget(save_button)

        main_layout.addLayout(button_row)

    def choose_color(self):
        """Open color picker dialog"""
        # Convert hex to QColor
        current_qcolor = QColor(self.selected_color)

        # Open color dialog
        color = QColorDialog.getColor(
            current_qcolor,
            self,
            "Elegir Color del Encabezado"
        )

        if color.isValid():
            # Update selected color
            self.selected_color = color.name()

            # Update preview
            self.color_preview.setStyleSheet(f"""
                QWidget {{
                    background-color: {self.selected_color};
                    border: 2px solid #3d3d3d;
                    border-radius: 4px;
                }}
            """)

            # Update label
            self.color_label.setText(self.selected_color)

            logger.info(f"Color selected: {self.selected_color}")

    def reset_defaults(self):
        """Reset to default values (empty name, default color)"""
        self.name_input.clear()
        self.selected_color = "#007acc"

        # Update preview
        self.color_preview.setStyleSheet(f"""
            QWidget {{
                background-color: {self.selected_color};
                border: 2px solid #3d3d3d;
                border-radius: 4px;
            }}
        """)

        # Update label
        self.color_label.setText(self.selected_color)

        logger.info("Reset to default values")

    def save_config(self):
        """Save configuration and emit signal"""
        custom_name = self.name_input.text().strip()
        custom_color = self.selected_color

        logger.info(f"Saving panel config - Name: '{custom_name}', Color: {custom_color}")

        # Emit signal with values (empty string if no custom name)
        self.config_saved.emit(custom_name, custom_color)

        # Close dialog
        self.accept()
