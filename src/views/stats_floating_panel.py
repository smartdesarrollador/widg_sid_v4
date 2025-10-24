"""
Stats Floating Panel - Panel flotante para mostrar estadísticas
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QFont, QCursor
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

        # Resize handling
        self.resizing = False
        self.resize_start_x = 0
        self.resize_start_width = 0
        self.resize_edge_width = 15

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
        self.setMinimumWidth(250)
        self.setMaximumWidth(500)
        self.setFixedHeight(350)
        self.resize(280, 350)
        self.setWindowOpacity(0.95)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

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

    def is_on_left_edge(self, pos):
        """Check if mouse position is on the left edge for resizing"""
        return pos.x() <= self.resize_edge_width

    def event(self, event):
        """Override event to handle hover for cursor changes"""
        if event.type() == QEvent.Type.HoverMove:
            pos = event.position().toPoint()
            if self.is_on_left_edge(pos):
                self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        return super().event(event)

    def mousePressEvent(self, event):
        """Handler para poder mover la ventana o redimensionarla"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_on_left_edge(event.pos()):
                # Start resizing
                self.resizing = True
                self.resize_start_x = event.globalPosition().toPoint().x()
                self.resize_start_width = self.width()
                event.accept()
            else:
                # Start dragging
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """Handler para mover o redimensionar la ventana"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing:
                # Calculate new width
                current_x = event.globalPosition().toPoint().x()
                delta_x = current_x - self.resize_start_x
                new_width = self.resize_start_width - delta_x

                # Apply constraints
                new_width = max(self.minimumWidth(), min(new_width, self.maximumWidth()))

                # Resize and reposition
                old_width = self.width()
                old_x = self.x()
                self.resize(new_width, self.height())

                # Adjust position to keep right edge fixed
                width_diff = self.width() - old_width
                self.move(old_x - width_diff, self.y())

                event.accept()
            else:
                # Dragging
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to end resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.resizing:
                self.resizing = False
                event.accept()
