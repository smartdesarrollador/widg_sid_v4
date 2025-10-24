"""
Favorites Floating Panel - Panel flotante para mostrar favoritos
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from views.widgets.favorites_panel import FavoritesPanel
from views.dialogs.suggestions_dialog import FavoriteSuggestionsDialog
from core.favorites_manager import FavoritesManager

logger = logging.getLogger(__name__)


class FavoritesFloatingPanel(QWidget):
    """Panel flotante para favoritos"""

    # Señales
    item_clicked = pyqtSignal(object)
    window_closed = pyqtSignal()
    favorite_executed = pyqtSignal(int)  # item_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.favorites_manager = FavoritesManager()
        self.init_ui()

    def init_ui(self):
        """Inicializar UI"""
        # Window properties
        self.setWindowTitle("⭐ Favoritos")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        # Tamaño
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_height = screen.availableGeometry().height()
            window_height = int(screen_height * 0.8)
        else:
            window_height = 600

        self.setFixedWidth(350)
        self.setMinimumHeight(400)
        self.resize(350, window_height)
        self.setWindowOpacity(0.95)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #007acc;
                border-radius: 6px 6px 0 0;
            }
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(15, 15, 15, 10)

        # Título
        title = QLabel("⭐ MIS FAVORITOS")
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14pt;
                font-weight: bold;
                background: transparent;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        # Botones de acción
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        suggestions_btn = QPushButton("💡 Sugerencias")
        suggestions_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        suggestions_btn.clicked.connect(self.show_suggestions)
        btn_layout.addWidget(suggestions_btn)

        close_btn = QPushButton("✕ Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 0.5);
            }
        """)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        header_layout.addLayout(btn_layout)
        main_layout.addWidget(header)

        # Panel de favoritos
        self.favorites_panel = FavoritesPanel(self)
        self.favorites_panel.setStyleSheet("""
            QWidget#favorites_panel {
                background-color: #252525;
                border: none;
                border-radius: 0 0 6px 6px;
            }
        """)

        # Conectar señales
        self.favorites_panel.favorite_double_clicked.connect(self.on_favorite_executed)
        self.favorites_panel.favorite_removed.connect(self.on_favorite_removed)

        main_layout.addWidget(self.favorites_panel)

        # Borde del panel
        self.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border: 2px solid #007acc;
                border-radius: 8px;
            }
        """)

    def on_favorite_executed(self, item_id: int):
        """Handler cuando se ejecuta un favorito"""
        logger.info(f"Favorite executed: {item_id}")
        self.favorite_executed.emit(item_id)

    def on_favorite_removed(self, item_id: int):
        """Handler cuando se quita un favorito"""
        logger.info(f"Favorite removed: {item_id}")
        self.favorites_panel.refresh()

    def show_suggestions(self):
        """Mostrar diálogo de sugerencias"""
        dialog = FavoriteSuggestionsDialog(self)
        if dialog.exec():
            # Usuario agregó favoritos
            self.favorites_panel.refresh()

    def refresh(self):
        """Refrescar panel de favoritos"""
        self.favorites_panel.refresh()

    def position_near_sidebar(self, sidebar_window):
        """Posicionar cerca del sidebar"""
        sidebar_geo = sidebar_window.geometry()
        x = sidebar_geo.x() + sidebar_geo.width() + 5
        y = sidebar_geo.y()
        self.move(x, y)

    def closeEvent(self, event):
        """Handler al cerrar ventana"""
        self.window_closed.emit()
        super().closeEvent(event)

    def mousePressEvent(self, event):
        """Handler para poder mover la ventana"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handler para mover la ventana"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
