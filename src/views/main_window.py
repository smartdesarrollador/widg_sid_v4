"""
Main Window View
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QScreen
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from views.sidebar import Sidebar
from views.content_panel import ContentPanel
from views.settings_window import SettingsWindow
from models.item import Item
from core.hotkey_manager import HotkeyManager
from core.tray_manager import TrayManager


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
        self.content_panel = None
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
        self.sidebar.settings_clicked.connect(self.open_settings)
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
        self.is_visible = True
        if self.tray_manager:
            self.tray_manager.update_window_state(True)
        print("Window shown")

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
