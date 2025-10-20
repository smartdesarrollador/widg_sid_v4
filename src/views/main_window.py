"""
Main Window View
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QScreen
import sys
import logging
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from views.sidebar import Sidebar
from views.floating_panel import FloatingPanel
from views.settings_window import SettingsWindow
from models.item import Item
from core.hotkey_manager import HotkeyManager
from core.tray_manager import TrayManager
from core.session_manager import SessionManager

# Get logger
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window - frameless, always-on-top sidebar"""

    # Signals
    category_selected = pyqtSignal(str)  # category_id
    item_selected = pyqtSignal(object)  # Item

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.config_manager = controller.config_manager if controller else None
        self.sidebar = None
        self.floating_panel = None  # Ventana flotante para items
        self.current_category_id = None  # Para el toggle
        self.hotkey_manager = None
        self.tray_manager = None
        self.is_visible = True

        self.init_ui()
        self.position_window()
        self.setup_hotkeys()
        self.setup_tray()

    def init_ui(self):
        """Initialize the user interface"""
        # Window properties
        self.setWindowTitle("Widget Sidebar")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Calculate window height: 80% of screen height (10% margin top + 10% margin bottom)
        screen = self.screen()
        if screen:
            screen_height = screen.availableGeometry().height()
            window_height = int(screen_height * 0.8)  # 80% de la altura de la pantalla
        else:
            window_height = 600  # Fallback

        # Set window size (starts with sidebar only)
        self.setFixedWidth(70)  # Just sidebar initially
        self.setMinimumHeight(400)
        self.resize(70, window_height)

        # Set window opacity
        self.setWindowOpacity(0.95)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout (vertical: title bar + sidebar)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar with minimize and close buttons
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-bottom: 1px solid #007acc;
            }
        """)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(5, 0, 5, 0)
        title_bar_layout.setSpacing(5)

        # Spacer
        title_bar_layout.addStretch()

        # Minimize button
        self.minimize_button = QPushButton("─")
        self.minimize_button.setFixedSize(25, 25)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #007acc;
            }
        """)
        self.minimize_button.clicked.connect(self.minimize_window)
        title_bar_layout.addWidget(self.minimize_button)

        # Close button
        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(25, 25)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c42b1c;
                border: 1px solid #e81123;
                color: #ffffff;
            }
        """)
        self.close_button.clicked.connect(self.close_window)
        title_bar_layout.addWidget(self.close_button)

        main_layout.addWidget(title_bar)

        # Create sidebar only (no embedded panel)
        self.sidebar = Sidebar()
        self.sidebar.category_clicked.connect(self.on_category_clicked)
        self.sidebar.settings_clicked.connect(self.open_settings)
        main_layout.addWidget(self.sidebar)

    def load_categories(self, categories):
        """Load categories into sidebar"""
        if self.sidebar:
            self.sidebar.load_categories(categories)

    def on_category_clicked(self, category_id: str):
        """Handle category button click - toggle floating panel"""
        try:
            logger.info(f"Category clicked: {category_id}")

            # Toggle: Si se hace clic en la misma categoría, ocultar el panel
            if self.current_category_id == category_id and self.floating_panel and self.floating_panel.isVisible():
                logger.info(f"Toggling off - hiding floating panel for category: {category_id}")
                self.floating_panel.hide()
                self.current_category_id = None
                return

            # Get category from controller
            if self.controller:
                logger.debug(f"Getting category {category_id} from controller...")
                category = self.controller.get_category(category_id)

                if category:
                    logger.info(f"Category found: {category.name} with {len(category.items)} items")

                    # Create floating panel if it doesn't exist
                    if not self.floating_panel:
                        self.floating_panel = FloatingPanel(config_manager=self.config_manager)
                        self.floating_panel.item_clicked.connect(self.on_item_clicked)
                        self.floating_panel.window_closed.connect(self.on_floating_panel_closed)
                        logger.debug("Floating panel created")

                    # Load category into floating panel
                    self.floating_panel.load_category(category)

                    # Position near sidebar
                    self.floating_panel.position_near_sidebar(self)

                    # Update current category
                    self.current_category_id = category_id

                    logger.debug("Category loaded into floating panel")
                else:
                    logger.warning(f"Category {category_id} not found")

            # Emit signal
            self.category_selected.emit(category_id)
            logger.debug("Category selected signal emitted")

        except Exception as e:
            logger.error(f"Error in on_category_clicked: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar categoría:\n{str(e)}\n\nRevisa widget_sidebar_error.log"
            )

    def on_floating_panel_closed(self):
        """Handle floating panel closed"""
        logger.info("Floating panel closed")
        self.current_category_id = None  # Reset para el toggle
        if self.floating_panel:
            self.floating_panel.deleteLater()
            self.floating_panel = None

    def on_item_clicked(self, item: Item):
        """Handle item button click"""
        try:
            logger.info(f"Item clicked: {item.label}")

            # Copy to clipboard via controller
            if self.controller:
                logger.debug(f"Copying item to clipboard: {item.content[:50]}...")
                self.controller.copy_item_to_clipboard(item)
                logger.info("Item copied to clipboard successfully")

            # Emit signal
            self.item_selected.emit(item)

        except Exception as e:
            logger.error(f"Error in on_item_clicked: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al copiar item:\n{str(e)}\n\nRevisa widget_sidebar_error.log"
            )

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

    def setup_hotkeys(self):
        """Setup global hotkeys"""
        self.hotkey_manager = HotkeyManager()

        # Register Ctrl+Shift+V to toggle window visibility
        self.hotkey_manager.register_hotkey("ctrl+shift+v", self.toggle_visibility)

        # Start listening for hotkeys
        self.hotkey_manager.start()

        print("Hotkeys registered: Ctrl+Shift+V (toggle window)")

    def setup_tray(self):
        """Setup system tray icon"""
        self.tray_manager = TrayManager()

        # Connect tray signals
        self.tray_manager.show_window_requested.connect(self.show_window)
        self.tray_manager.hide_window_requested.connect(self.hide_window)
        self.tray_manager.settings_requested.connect(self.show_settings)
        self.tray_manager.logout_requested.connect(self.logout_session)
        self.tray_manager.quit_requested.connect(self.quit_application)

        # Setup tray icon
        self.tray_manager.setup_tray(self)

        print("System tray icon created")

    def toggle_visibility(self):
        """Toggle window visibility"""
        if self.is_visible:
            self.hide_window()
        else:
            self.show_window()

    def show_window(self):
        """Show the window"""
        self.show()
        self.activateWindow()
        self.raise_()

    def minimize_window(self):
        """Minimize the window"""
        logger.info("Minimizing window")
        self.showMinimized()

    def close_window(self):
        """Close the application"""
        logger.info("Closing application from close button")
        self.quit_application()

    def hide_window(self):
        """Hide the window"""
        self.hide()
        self.is_visible = False
        if self.tray_manager:
            self.tray_manager.update_window_state(False)
        print("Window hidden")

    def open_settings(self):
        """Open settings window"""
        print("Opening settings window...")
        settings_window = SettingsWindow(controller=self.controller, parent=self)
        settings_window.settings_changed.connect(self.on_settings_changed)

        if settings_window.exec() == QMessageBox.DialogCode.Accepted:
            print("Settings saved")

    def show_settings(self):
        """Show settings dialog (called from tray)"""
        self.open_settings()

    def on_settings_changed(self):
        """Handle settings changes"""
        print("Settings changed - reloading...")

        # Reload categories in sidebar
        if self.controller:
            categories = self.controller.get_categories()
            self.sidebar.load_categories(categories)

        # Apply appearance settings (opacity, etc.)
        if self.config_manager:
            opacity = self.config_manager.get_setting("opacity", 0.95)
            self.setWindowOpacity(opacity)

        print("Settings applied")

    def logout_session(self):
        """Logout current session"""
        logger.info("Logging out...")

        # Confirm logout
        reply = QMessageBox.question(
            self,
            "Cerrar Sesión",
            "¿Estás seguro que deseas cerrar sesión?\n\nDeberás ingresar tu contraseña nuevamente al abrir la aplicación.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Invalidate session
            session_manager = SessionManager()
            session_manager.invalidate_session()
            logger.info("Session invalidated")

            # Show notification
            if self.tray_manager:
                self.tray_manager.show_message(
                    "Sesión Cerrada",
                    "Has cerrado sesión exitosamente. La aplicación se cerrará."
                )

            # Quit application
            self.quit_application()

    def quit_application(self):
        """Quit the application"""
        print("Quitting application...")

        # Stop hotkey manager
        if self.hotkey_manager:
            self.hotkey_manager.stop()

        # Cleanup tray
        if self.tray_manager:
            self.tray_manager.cleanup()

        # Close window
        self.close()

        # Exit application
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing"""
        # Minimize to tray instead of closing
        event.ignore()
        self.hide_window()

        # Show notification on first minimize
        if self.tray_manager and self.is_visible:
            self.tray_manager.show_message(
                "Widget Sidebar",
                "La aplicación sigue ejecutándose en la bandeja del sistema"
            )
