"""
Main Window View
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QScreen


class MainWindow(QMainWindow):
    """Main application window - frameless, always-on-top sidebar"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.position_window()

    def init_ui(self):
        """Initialize the user interface"""
        # Window properties
        self.setWindowTitle("Widget Sidebar")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Set window size
        self.setFixedWidth(370)  # 70px sidebar + 300px content panel
        self.setMinimumHeight(400)
        self.resize(370, 600)

        # Set window opacity
        self.setWindowOpacity(0.95)

        # Central widget - temporary placeholder
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Temporary label to show window is working
        temp_label = QLabel("Widget Sidebar\n\nCore MVC Loaded\n\nPhase 2 in Progress")
        temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temp_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 14px;
                padding: 20px;
            }
        """)
        main_layout.addWidget(temp_label)

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
