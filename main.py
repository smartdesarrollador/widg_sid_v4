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

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from controllers.main_controller import MainController
from views.main_window import MainWindow


def main():
    """Main entry point for Widget Sidebar application"""
    print("=" * 60)
    print("Widget Sidebar v1.0.0 - Phase 3: UI Complete")
    print("=" * 60)

    # Initialize PyQt6 application
    app = QApplication(sys.argv)
    app.setApplicationName("Widget Sidebar")

    # Initialize main controller (loads config and categories)
    print("\nInitializing MVC architecture...")
    controller = MainController()

    # Create main window with controller
    print("\nCreating main window...")
    window = MainWindow(controller)

    # Load categories into sidebar
    print("\nLoading categories into UI...")
    categories = controller.get_categories()
    window.load_categories(categories)

    # Show window
    window.show()

    print(f"\n✓ Loaded {len(categories)} categories")
    print("✓ UI fully functional")
    print("\nHow to use:")
    print("  1. Click a category button in the sidebar")
    print("  2. Panel will expand showing items")
    print("  3. Click an item to copy to clipboard")
    print("  4. Item will flash blue when copied")
    print("\nApplication ready!")
    print("=" * 60)

    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
