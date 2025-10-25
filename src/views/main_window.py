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
from views.favorites_floating_panel import FavoritesFloatingPanel
from views.stats_floating_panel import StatsFloatingPanel
from views.settings_window import SettingsWindow
from views.dialogs.popular_items_dialog import PopularItemsDialog
from views.dialogs.forgotten_items_dialog import ForgottenItemsDialog
from views.dialogs.suggestions_dialog import FavoriteSuggestionsDialog
from views.dialogs.stats_dashboard import StatsDashboard
from views.category_filter_window import CategoryFilterWindow
from models.item import Item
from core.hotkey_manager import HotkeyManager
from core.tray_manager import TrayManager
from core.session_manager import SessionManager
from core.notification_manager import NotificationManager

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
        self.favorites_panel = None  # Ventana flotante para favoritos
        self.stats_panel = None  # Ventana flotante para estadísticas
        self.category_filter_window = None  # Ventana de filtros de categorías
        self.current_category_id = None  # Para el toggle
        self.hotkey_manager = None
        self.tray_manager = None
        self.notification_manager = NotificationManager()
        self.is_visible = True

        self.init_ui()
        self.position_window()
        self.setup_hotkeys()
        self.setup_tray()
        self.check_notifications_delayed()

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
        self.sidebar.favorites_clicked.connect(self.on_favorites_clicked)
        self.sidebar.stats_clicked.connect(self.on_stats_clicked)
        self.sidebar.settings_clicked.connect(self.open_settings)
        self.sidebar.category_filter_clicked.connect(self.on_category_filter_clicked)
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

    def on_favorites_clicked(self):
        """Handle favorites button click - show favorites panel"""
        try:
            logger.info("Favorites button clicked")

            # Toggle: Si ya está visible, ocultarlo
            if self.favorites_panel and self.favorites_panel.isVisible():
                logger.info("Hiding favorites panel")
                self.favorites_panel.hide()
                return

            # Crear panel si no existe
            if not self.favorites_panel:
                self.favorites_panel = FavoritesFloatingPanel()
                self.favorites_panel.favorite_executed.connect(self.on_favorite_executed)
                self.favorites_panel.window_closed.connect(self.on_favorites_panel_closed)
                logger.debug("Favorites panel created")

            # Posicionar cerca del sidebar
            self.favorites_panel.position_near_sidebar(self)

            # Mostrar panel
            self.favorites_panel.show()
            self.favorites_panel.refresh()

            logger.info("Favorites panel shown")

        except Exception as e:
            logger.error(f"Error in on_favorites_clicked: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al mostrar favoritos:\n{str(e)}"
            )

    def on_favorites_panel_closed(self):
        """Handle favorites panel closed"""
        logger.info("Favorites panel closed")
        if self.favorites_panel:
            self.favorites_panel.deleteLater()
            self.favorites_panel = None

    def on_favorite_executed(self, item_id: int):
        """Handle favorite item executed"""
        try:
            logger.info(f"Favorite item executed: {item_id}")

            # Buscar el item y ejecutarlo
            if self.controller:
                # Aquí deberías tener una forma de obtener el item por ID
                # Por ahora solo hacemos log
                logger.info(f"Executing favorite item {item_id}")

        except Exception as e:
            logger.error(f"Error executing favorite: {e}", exc_info=True)

    def on_stats_clicked(self):
        """Handle stats button click - show stats panel"""
        try:
            logger.info("Stats button clicked")

            # Toggle: Si ya está visible, ocultarlo
            if self.stats_panel and self.stats_panel.isVisible():
                logger.info("Hiding stats panel")
                self.stats_panel.hide()
                return

            # Crear panel si no existe
            if not self.stats_panel:
                self.stats_panel = StatsFloatingPanel()
                self.stats_panel.window_closed.connect(self.on_stats_panel_closed)
                logger.debug("Stats panel created")

            # Posicionar cerca del sidebar
            self.stats_panel.position_near_sidebar(self)

            # Mostrar panel
            self.stats_panel.show()
            self.stats_panel.refresh()

            logger.info("Stats panel shown")

        except Exception as e:
            logger.error(f"Error in on_stats_clicked: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al mostrar estadísticas:\n{str(e)}"
            )

    def on_stats_panel_closed(self):
        """Handle stats panel closed"""
        logger.info("Stats panel closed")
        if self.stats_panel:
            self.stats_panel.deleteLater()
            self.stats_panel = None

    def on_category_filter_clicked(self):
        """Handle category filter button click - show filter window"""
        try:
            logger.info("Category filter button clicked")

            # Toggle: Si ya está visible, ocultarlo
            if self.category_filter_window and self.category_filter_window.isVisible():
                logger.info("Hiding category filter window")
                self.category_filter_window.hide()
                return

            # Crear ventana si no existe
            if not self.category_filter_window:
                self.category_filter_window = CategoryFilterWindow(self)
                self.category_filter_window.filters_changed.connect(self.on_category_filters_changed)
                self.category_filter_window.filters_cleared.connect(self.on_category_filters_cleared)
                self.category_filter_window.window_closed.connect(self.on_category_filter_window_closed)
                logger.debug("Category filter window created")

            # Posicionar a la IZQUIERDA del sidebar
            sidebar_rect = self.geometry()
            filter_window_width = self.category_filter_window.width()
            window_x = sidebar_rect.left() - filter_window_width - 10
            window_y = sidebar_rect.top()
            self.category_filter_window.move(window_x, window_y)

            # Mostrar ventana
            self.category_filter_window.show()

            logger.info("Category filter window shown")

        except Exception as e:
            logger.error(f"Error in on_category_filter_clicked: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al mostrar filtros de categorías:\n{str(e)}"
            )

    def on_category_filters_changed(self, filters: dict):
        """Handle category filters changed"""
        try:
            logger.info(f"Category filters changed: {filters}")

            # Aplicar filtros a través del controller
            if self.controller:
                self.controller.apply_category_filters(filters)

        except Exception as e:
            logger.error(f"Error applying category filters: {e}", exc_info=True)

    def on_category_filters_cleared(self):
        """Handle category filters cleared"""
        try:
            logger.info("Category filters cleared")

            # Recargar todas las categorías
            if self.controller:
                self.controller.load_all_categories()

        except Exception as e:
            logger.error(f"Error clearing category filters: {e}", exc_info=True)

    def on_category_filter_window_closed(self):
        """Handle category filter window closed"""
        logger.info("Category filter window closed")
        # No eliminamos la ventana, solo la ocultamos para reutilizarla

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
        self.tray_manager.stats_dashboard_requested.connect(self.show_stats_dashboard)
        self.tray_manager.popular_items_requested.connect(self.show_popular_items)
        self.tray_manager.forgotten_items_requested.connect(self.show_forgotten_items)
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

    def check_notifications_delayed(self):
        """Verificar notificaciones 10 segundos después de abrir"""
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(10000, self.check_notifications)  # 10 segundos

    def check_notifications(self):
        """Verificar y mostrar notificaciones pendientes"""
        try:
            notifications = self.notification_manager.get_pending_notifications()

            if not notifications:
                logger.info("No pending notifications")
                return

            # Mostrar solo las 2 primeras notificaciones (no saturar)
            priority_notifications = notifications[:2]

            logger.info(f"Found {len(notifications)} notifications, showing {len(priority_notifications)}")

            # Por ahora, solo mostramos un diálogo simple con la primera notificación de alta prioridad
            for notification in priority_notifications:
                if notification.get('priority') == 'high':
                    self.show_notification_message(notification)
                    break

        except Exception as e:
            logger.error(f"Error checking notifications: {e}")

    def show_notification_message(self, notification: dict):
        """Mostrar mensaje de notificación"""
        title = notification.get('title', 'Notificación')
        message = notification.get('message', '')
        action = notification.get('action', '')

        reply = QMessageBox.question(
            self,
            title,
            f"{message}\n\n¿Deseas verlo ahora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.handle_notification_action(action)

    def handle_notification_action(self, action: str):
        """Manejar acción de notificación"""
        try:
            if action == 'show_favorite_suggestions':
                self.show_favorite_suggestions()

            elif action == 'show_cleanup_suggestions':
                self.show_forgotten_items()

            elif action == 'show_abandoned_items':
                self.show_forgotten_items()

            elif action == 'show_failing_items':
                # TODO: Crear diálogo específico para items con errores
                QMessageBox.information(
                    self,
                    "Items con Errores",
                    "Funcionalidad en desarrollo"
                )

            elif action == 'show_slow_items':
                # TODO: Crear diálogo específico para items lentos
                QMessageBox.information(
                    self,
                    "Items Lentos",
                    "Funcionalidad en desarrollo"
                )

            elif action == 'show_shortcut_suggestions':
                # TODO: Crear diálogo para asignar atajos
                QMessageBox.information(
                    self,
                    "Sugerencias de Atajos",
                    "Funcionalidad en desarrollo"
                )

        except Exception as e:
            logger.error(f"Error handling notification action '{action}': {e}")

    def show_popular_items(self):
        """Mostrar diálogo de items populares"""
        try:
            dialog = PopularItemsDialog(self)
            dialog.item_selected.connect(self.on_popular_item_selected)
            dialog.exec()
        except Exception as e:
            logger.error(f"Error showing popular items: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar items populares:\n{str(e)}")

    def show_forgotten_items(self):
        """Mostrar diálogo de items olvidados"""
        try:
            dialog = ForgottenItemsDialog(self)
            if dialog.exec():
                # Recargar categorías si se eliminaron items
                if self.controller:
                    categories = self.controller.get_categories()
                    self.sidebar.load_categories(categories)
        except Exception as e:
            logger.error(f"Error showing forgotten items: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar items olvidados:\n{str(e)}")

    def show_stats_dashboard(self):
        """Mostrar dashboard completo de estadísticas"""
        try:
            dialog = StatsDashboard(self)
            dialog.exec()
        except Exception as e:
            logger.error(f"Error showing stats dashboard: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar dashboard de estadísticas:\n{str(e)}")

    def show_favorite_suggestions(self):
        """Mostrar diálogo de sugerencias de favoritos"""
        try:
            dialog = FavoriteSuggestionsDialog(self)
            if dialog.exec():
                # Refrescar panel de favoritos si existe
                if self.favorites_panel:
                    self.favorites_panel.refresh()
        except Exception as e:
            logger.error(f"Error showing favorite suggestions: {e}")
            QMessageBox.critical(self, "Error", f"Error al mostrar sugerencias:\n{str(e)}")

    def on_popular_item_selected(self, item_id: int):
        """Handler cuando se selecciona un item popular"""
        logger.info(f"Popular item selected: {item_id}")
        # TODO: Abrir el item o mostrarlo en la lista principal

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
