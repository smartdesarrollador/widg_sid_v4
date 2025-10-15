"""
Widget Sidebar - Windows Clipboard Manager
Main entry point for the application

Version: 1.0.0
Author: Widget Sidebar Team
License: MIT
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from controllers.main_controller import MainController
from views.main_window import MainWindow


def main():
    """Main entry point for Widget Sidebar application"""
    print("=" * 50)
    print("Widget Sidebar v1.0.0 - Phase 2")
    print("=" * 50)

    # Initialize PyQt6 application
    app = QApplication(sys.argv)
    app.setApplicationName("Widget Sidebar")

    # Initialize main controller (loads config and categories)
    print("\nInitializing MVC architecture...")
    controller = MainController()

    # Create and show main window
    print("\nCreating main window...")
    window = MainWindow()
    window.show()

    print("\nApplication ready!")
    print("=" * 50)

    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
