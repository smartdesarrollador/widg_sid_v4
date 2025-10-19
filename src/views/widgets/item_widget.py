"""
Item Button Widget
"""
from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont
import sys
import webbrowser
import os
import subprocess
import platform
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.item import Item, ItemType


class ItemButton(QFrame):
    """Custom item button widget for content panel with tags support"""

    # Signal emitted when item is clicked with the item
    item_clicked = pyqtSignal(object)

    def __init__(self, item: Item, parent=None):
        super().__init__(parent)
        self.item = item
        self.is_copied = False
        self.is_revealed = False  # Track if sensitive content is revealed
        self.reveal_timer = None  # Timer for auto-hide
        self.clipboard_clear_timer = None  # Timer for clipboard clearing

        self.init_ui()

    def init_ui(self):
        """Initialize button UI"""
        # Set frame properties
        self.setMinimumHeight(50)
        self.setMaximumHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 8, 15, 8)
        main_layout.setSpacing(10)

        # Left side: Item info (label + tags)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(5)

        # Item label (ofuscar si es sensible y no revelado)
        label_text = self.get_display_label()
        self.label_widget = QLabel(label_text)
        label_font = QFont()
        label_font.setPointSize(10)
        self.label_widget.setFont(label_font)
        left_layout.addWidget(self.label_widget)

        # Tags container (only if item has tags)
        if self.item.tags and len(self.item.tags) > 0:
            tags_layout = QHBoxLayout()
            tags_layout.setContentsMargins(0, 0, 0, 0)
            tags_layout.setSpacing(5)

            for tag in self.item.tags:
                tag_label = QLabel(tag)
                tag_label.setStyleSheet("""
                    QLabel {
                        background-color: #007acc;
                        color: #ffffff;
                        border-radius: 3px;
                        padding: 2px 8px;
                        font-size: 8pt;
                    }
                """)
                tags_layout.addWidget(tag_label)

            tags_layout.addStretch()
            left_layout.addLayout(tags_layout)

        main_layout.addLayout(left_layout, 1)

        # Reveal button for sensitive items
        if hasattr(self.item, 'is_sensitive') and self.item.is_sensitive:
            self.reveal_button = QPushButton("👁")
            self.reveal_button.setFixedSize(35, 35)
            self.reveal_button.setStyleSheet("""
                QPushButton {
                    background-color: #cc0000;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    font-size: 16pt;
                }
                QPushButton:hover {
                    background-color: #9e0000;
                }
                QPushButton:pressed {
                    background-color: #780000;
                }
            """)
            self.reveal_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.reveal_button.setToolTip("Revelar/Ocultar contenido sensible")
            self.reveal_button.clicked.connect(self.toggle_reveal)
            main_layout.addWidget(self.reveal_button)

        # Right side: Action buttons based on item type
        if self.item.type == ItemType.URL:
            # Open URL button (only for URL items)
            self.open_url_button = QPushButton("🌐")
            self.open_url_button.setFixedSize(35, 35)
            self.open_url_button.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    font-size: 16pt;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
                QPushButton:pressed {
                    background-color: #004578;
                }
            """)
            self.open_url_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.open_url_button.setToolTip("Abrir en navegador")
            self.open_url_button.clicked.connect(self.open_in_browser)
            main_layout.addWidget(self.open_url_button)

        elif self.item.type == ItemType.PATH:
            # PATH action buttons
            path_buttons_layout = QHBoxLayout()
            path_buttons_layout.setSpacing(5)

            # Open in explorer button
            self.open_explorer_button = QPushButton("📁")
            self.open_explorer_button.setFixedSize(35, 35)
            self.open_explorer_button.setStyleSheet("""
                QPushButton {
                    background-color: #2d7d2d;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    font-size: 16pt;
                }
                QPushButton:hover {
                    background-color: #236123;
                }
                QPushButton:pressed {
                    background-color: #1a4a1a;
                }
            """)
            self.open_explorer_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.open_explorer_button.setToolTip("Abrir en explorador")
            self.open_explorer_button.clicked.connect(self.open_in_explorer)
            path_buttons_layout.addWidget(self.open_explorer_button)

            # Open file button (only if it's a file, not a directory)
            path = Path(self.item.content)
            if path.exists() and path.is_file():
                self.open_file_button = QPushButton("📝")
                self.open_file_button.setFixedSize(35, 35)
                self.open_file_button.setStyleSheet("""
                    QPushButton {
                        background-color: #cc7a00;
                        color: #ffffff;
                        border: none;
                        border-radius: 4px;
                        font-size: 16pt;
                    }
                    QPushButton:hover {
                        background-color: #9e5e00;
                    }
                    QPushButton:pressed {
                        background-color: #784500;
                    }
                """)
                self.open_file_button.setCursor(Qt.CursorShape.PointingHandCursor)
                self.open_file_button.setToolTip("Abrir archivo")
                self.open_file_button.clicked.connect(self.open_file)
                path_buttons_layout.addWidget(self.open_file_button)

            main_layout.addLayout(path_buttons_layout)

        # Set initial style (different for sensitive items)
        if hasattr(self.item, 'is_sensitive') and self.item.is_sensitive:
            self.setStyleSheet("""
                QFrame {
                    background-color: #3d2020;
                    border: none;
                    border-left: 3px solid #cc0000;
                    border-bottom: 1px solid #1e1e1e;
                }
                QFrame:hover {
                    background-color: #4d2525;
                }
                QLabel {
                    color: #cccccc;
                    background-color: transparent;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border: none;
                    border-bottom: 1px solid #1e1e1e;
                }
                QFrame:hover {
                    background-color: #3d3d3d;
                }
                QLabel {
                    color: #cccccc;
                    background-color: transparent;
                    border: none;
                }
            """)

    def mousePressEvent(self, event):
        """Handle mouse press event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_clicked()
        super().mousePressEvent(event)

    def on_clicked(self):
        """Handle button click"""
        # Emit signal with item
        self.item_clicked.emit(self.item)

        # Show copied feedback
        self.show_copied_feedback()

        # If sensitive item, start clipboard auto-clear timer
        if hasattr(self.item, 'is_sensitive') and self.item.is_sensitive:
            self.start_clipboard_clear_timer()

    def open_in_browser(self):
        """Open URL in default browser"""
        if self.item.type == ItemType.URL:
            url = self.item.content
            # Ensure URL has proper protocol
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                else:
                    url = 'https://' + url

            # Open in browser
            webbrowser.open(url)

            # Update button style briefly to show it was clicked
            original_style = self.open_url_button.styleSheet()
            self.open_url_button.setStyleSheet("""
                QPushButton {
                    background-color: #00ff00;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    font-size: 16pt;
                }
            """)
            QTimer.singleShot(300, lambda: self.open_url_button.setStyleSheet(original_style))

    def open_in_explorer(self):
        """Open file/folder in system file explorer"""
        if self.item.type == ItemType.PATH:
            path = Path(self.item.content)

            try:
                system = platform.system()

                if system == 'Windows':
                    # Windows: Use explorer with /select to highlight the file/folder
                    if path.exists():
                        subprocess.run(['explorer', '/select,', str(path.absolute())])
                    else:
                        # If path doesn't exist, try to open parent directory
                        parent = path.parent
                        if parent.exists():
                            subprocess.run(['explorer', str(parent.absolute())])

                elif system == 'Darwin':  # macOS
                    if path.exists():
                        subprocess.run(['open', '-R', str(path.absolute())])
                    else:
                        parent = path.parent
                        if parent.exists():
                            subprocess.run(['open', str(parent.absolute())])

                else:  # Linux
                    if path.exists():
                        if path.is_file():
                            subprocess.run(['xdg-open', str(path.parent.absolute())])
                        else:
                            subprocess.run(['xdg-open', str(path.absolute())])
                    else:
                        parent = path.parent
                        if parent.exists():
                            subprocess.run(['xdg-open', str(parent.absolute())])

                # Visual feedback
                original_style = self.open_explorer_button.styleSheet()
                self.open_explorer_button.setStyleSheet("""
                    QPushButton {
                        background-color: #00ff00;
                        color: #ffffff;
                        border: none;
                        border-radius: 4px;
                        font-size: 16pt;
                    }
                """)
                QTimer.singleShot(300, lambda: self.open_explorer_button.setStyleSheet(original_style))

            except Exception as e:
                print(f"Error opening explorer: {e}")

    def open_file(self):
        """Open file with default application"""
        if self.item.type == ItemType.PATH:
            path = Path(self.item.content)

            if not path.exists() or not path.is_file():
                print(f"File not found: {path}")
                return

            try:
                system = platform.system()

                if system == 'Windows':
                    # Windows: Use os.startfile
                    os.startfile(str(path.absolute()))

                elif system == 'Darwin':  # macOS
                    subprocess.run(['open', str(path.absolute())])

                else:  # Linux
                    subprocess.run(['xdg-open', str(path.absolute())])

                # Visual feedback
                original_style = self.open_file_button.styleSheet()
                self.open_file_button.setStyleSheet("""
                    QPushButton {
                        background-color: #00ff00;
                        color: #ffffff;
                        border: none;
                        border-radius: 4px;
                        font-size: 16pt;
                    }
                """)
                QTimer.singleShot(300, lambda: self.open_file_button.setStyleSheet(original_style))

            except Exception as e:
                print(f"Error opening file: {e}")

    def show_copied_feedback(self):
        """Show visual feedback that item was copied"""
        self.is_copied = True

        # Different style for sensitive items (orange/warning color)
        if hasattr(self.item, 'is_sensitive') and self.item.is_sensitive:
            self.setStyleSheet("""
                QFrame {
                    background-color: #cc7a00;
                    border: none;
                    border-bottom: 1px solid #9e5e00;
                }
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
                    border: none;
                    font-weight: bold;
                }
            """)
        else:
            # Normal items: blue feedback
            self.setStyleSheet("""
                QFrame {
                    background-color: #007acc;
                    border: none;
                    border-bottom: 1px solid #005a9e;
                }
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
                    border: none;
                    font-weight: bold;
                }
            """)

        # Reset after 500ms
        QTimer.singleShot(500, self.reset_style)

    def reset_style(self):
        """Reset button style to normal"""
        self.is_copied = False
        # Apply special style for sensitive items
        if hasattr(self.item, 'is_sensitive') and self.item.is_sensitive:
            self.setStyleSheet("""
                QFrame {
                    background-color: #3d2020;
                    border: none;
                    border-left: 3px solid #cc0000;
                    border-bottom: 1px solid #1e1e1e;
                }
                QFrame:hover {
                    background-color: #4d2525;
                }
                QLabel {
                    color: #cccccc;
                    background-color: transparent;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border: none;
                    border-bottom: 1px solid #1e1e1e;
                }
                QFrame:hover {
                    background-color: #3d3d3d;
                }
                QLabel {
                    color: #cccccc;
                    background-color: transparent;
                    border: none;
                }
            """)

    def get_display_label(self):
        """Get display label (ofuscado si es sensible y no revelado)"""
        if hasattr(self.item, 'is_sensitive') and self.item.is_sensitive and not self.is_revealed:
            # Ofuscar: mostrar label + (********)
            content_preview = "********"
            return f"{self.item.label} ({content_preview})"
        elif hasattr(self.item, 'is_sensitive') and self.item.is_sensitive and self.is_revealed:
            # Revelado: mostrar label + preview del contenido
            content = self.item.content[:30] if len(self.item.content) > 30 else self.item.content
            return f"{self.item.label} ({content}...)" if len(self.item.content) > 30 else f"{self.item.label} ({content})"
        else:
            # Item normal: solo el label
            return self.item.label

    def toggle_reveal(self):
        """Toggle reveal/hide sensitive content"""
        self.is_revealed = not self.is_revealed

        # Update label
        self.label_widget.setText(self.get_display_label())

        if self.is_revealed:
            # Cambiar icono del boton
            self.reveal_button.setText("🙈")
            self.reveal_button.setToolTip("Ocultar contenido sensible")

            # Cancelar timer anterior si existe
            if self.reveal_timer:
                self.reveal_timer.stop()

            # Auto-ocultar despues de 10 segundos
            self.reveal_timer = QTimer()
            self.reveal_timer.setSingleShot(True)
            self.reveal_timer.timeout.connect(self.auto_hide)
            self.reveal_timer.start(10000)  # 10 segundos
        else:
            # Cambiar icono del boton
            self.reveal_button.setText("👁")
            self.reveal_button.setToolTip("Revelar/Ocultar contenido sensible")

            # Cancelar timer si existe
            if self.reveal_timer:
                self.reveal_timer.stop()

    def auto_hide(self):
        """Auto-hide sensitive content after timeout"""
        if self.is_revealed:
            self.toggle_reveal()

    def start_clipboard_clear_timer(self):
        """Start timer to clear clipboard after 30 seconds for sensitive items"""
        # Cancel previous timer if exists
        if self.clipboard_clear_timer:
            self.clipboard_clear_timer.stop()

        # Start 30-second timer
        self.clipboard_clear_timer = QTimer()
        self.clipboard_clear_timer.setSingleShot(True)
        self.clipboard_clear_timer.timeout.connect(self.clear_clipboard)
        self.clipboard_clear_timer.start(30000)  # 30 seconds

    def clear_clipboard(self):
        """Clear clipboard content"""
        try:
            import pyperclip
            pyperclip.copy("")  # Clear clipboard
        except Exception as e:
            print(f"Error clearing clipboard: {e}")
