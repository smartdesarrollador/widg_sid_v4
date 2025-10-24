"""
Stats Floating Panel - Panel flotante para mostrar estadísticas
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from views.widgets.stats_widget import StatsWidget

logger = logging.getLogger(__name__)


class StatsFloatingPanel(QWidget):
    """Panel flotante para estadísticas"""

    # Señales
    window_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Inicializar UI"""
        # Window properties
        self.setWindowTitle("📊 Estadísticas")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        # Tamaño
        self.setFixedSize(280, 350)
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
        title = QLabel("📊 ESTADÍSTICAS")
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12pt;
                font-weight: bold;
                background: transparent;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        # Botón cerrar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

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
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()

        header_layout.addLayout(btn_layout)
        main_layout.addWidget(header)

        # Stats widget
        self.stats_widget = StatsWidget(self)
        self.stats_widget.setStyleSheet("""
            QWidget#stats_widget {
                background-color: #252525;
                border: none;
                border-radius: 0 0 6px 6px;
            }
        """)
        main_layout.addWidget(self.stats_widget)

        # Borde del panel
        self.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border: 2px solid #007acc;
                border-radius: 8px;
            }
        """)

    def refresh(self):
        """Refrescar estadísticas"""
        self.stats_widget.refresh()

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
