"""
Settings Window
Main settings dialog with tabbed interface
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from views.category_editor import CategoryEditor
from views.appearance_settings import AppearanceSettings
from views.hotkey_settings import HotkeySettings
from views.general_settings import GeneralSettings


class SettingsWindow(QDialog):
    """
    Settings window with tabbed interface
    Modal dialog for configuring all application settings
    """

    # Signal emitted when settings are saved
    settings_changed = pyqtSignal()

    def __init__(self, controller=None, parent=None):
        """
        Initialize settings window

        Args:
            controller: MainController instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.controller = controller
        self.config_manager = controller.config_manager if controller else None

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize the UI"""
        # Window properties
        self.setWindowTitle("Configuración")
        self.setFixedSize(600, 650)
        self.setModal(True)

        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #cccccc;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #252525;
                color: #cccccc;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #3d3d3d;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                color: #ffffff;
                border-bottom: 2px solid #007acc;
            }
            QTabBar::tab:hover:!selected {
                background-color: #2d2d2d;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
                min-width: 80px;
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
            QPushButton#apply_button {
                background-color: #0e6b0e;
                color: #ffffff;
                border: none;
            }
            QPushButton#apply_button:hover {
                background-color: #0a520a;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Create tabs
        self.category_editor = CategoryEditor(controller=self.controller)
        self.appearance_settings = AppearanceSettings(config_manager=self.config_manager)
        self.hotkey_settings = HotkeySettings(config_manager=self.config_manager)
        self.general_settings = GeneralSettings(config_manager=self.config_manager)

        # Add tabs
        self.tab_widget.addTab(self.category_editor, "Categorías")
        self.tab_widget.addTab(self.appearance_settings, "Apariencia")
        self.tab_widget.addTab(self.hotkey_settings, "Hotkeys")
        self.tab_widget.addTab(self.general_settings, "General")

        main_layout.addWidget(self.tab_widget)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Cancel button
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        buttons_layout.addStretch()

        # Apply button
        self.apply_button = QPushButton("Aplicar")
        self.apply_button.setObjectName("apply_button")
        self.apply_button.clicked.connect(self.apply_settings)
        buttons_layout.addWidget(self.apply_button)

        # Save button
        self.save_button = QPushButton("Guardar")
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_button)

        main_layout.addLayout(buttons_layout)

    def load_settings(self):
        """Load current settings into all tabs"""
        # Category editor loads its own data
        self.category_editor.load_categories()

        # Other tabs load through their __init__ methods
        # Already done in init_ui

    def apply_settings(self):
        """Apply settings without closing dialog"""
        try:
            # Save to config
            if self.save_to_config():
                QMessageBox.information(
                    self,
                    "Aplicar Configuración",
                    "Configuración aplicada correctamente.\n\n"
                    "Algunos cambios requieren reiniciar la aplicación."
                )
                self.settings_changed.emit()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al aplicar configuración:\n{str(e)}"
            )

    def save_settings(self):
        """Save all settings and close dialog"""
        try:
            if self.save_to_config():
                self.settings_changed.emit()
                self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar configuración:\n{str(e)}"
            )

    def save_to_config(self) -> bool:
        """
        Save all settings to config manager

        Returns:
            True if successful
        """
        if not self.config_manager:
            return False

        # Get settings from all tabs
        appearance_settings = self.appearance_settings.get_settings()
        hotkey_settings = self.hotkey_settings.get_settings()
        general_settings = self.general_settings.get_settings()

        # Update config
        self.config_manager.set_setting("theme", appearance_settings["theme"])
        self.config_manager.set_setting("opacity", appearance_settings["opacity"])
        self.config_manager.set_setting("sidebar_width", appearance_settings["sidebar_width"])
        self.config_manager.set_setting("panel_width", appearance_settings["panel_width"])
        self.config_manager.set_setting("animation_speed", appearance_settings["animation_speed"])

        self.config_manager.set_setting("hotkey", hotkey_settings["hotkey"])

        self.config_manager.set_setting("minimize_to_tray", general_settings["minimize_to_tray"])
        self.config_manager.set_setting("always_on_top", general_settings["always_on_top"])
        self.config_manager.set_setting("start_with_windows", general_settings["start_with_windows"])
        self.config_manager.set_setting("max_history", general_settings["max_history"])

        # Save categories
        categories = self.category_editor.get_categories()
        if self.controller:
            # Update controller's categories
            self.controller.categories = categories

            # Save to config
            self.config_manager.categories = categories
            self.config_manager.save_config()

        return True

    def closeEvent(self, event):
        """Override close event to check for unsaved changes"""
        # For now, just accept the close
        # TODO: Add unsaved changes detection
        event.accept()
