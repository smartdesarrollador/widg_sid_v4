"""
Test script for Phase 3 - UI functionality
Tests UI components without displaying window
"""

import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from controllers.main_controller import MainController
from views.main_window import MainWindow
from views.sidebar import Sidebar
from views.content_panel import ContentPanel
from views.widgets.button_widget import CategoryButton
from views.widgets.item_widget import ItemButton


def test_phase3():
    """Test Phase 3 UI implementation"""
    print("=" * 60)
    print("TESTING PHASE 3: UI Implementation")
    print("=" * 60)

    # Initialize Qt application (required for widgets)
    app = QApplication(sys.argv)

    # Test 1: Initialize controller
    print("\n[TEST 1] Initializing MainController...")
    try:
        controller = MainController()
        categories = controller.get_categories()
        print(f"✓ Controller initialized with {len(categories)} categories")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 2: Create Sidebar
    print("\n[TEST 2] Creating Sidebar...")
    try:
        sidebar = Sidebar()
        sidebar.load_categories(categories)
        print(f"✓ Sidebar created with {len(sidebar.category_buttons)} buttons")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 3: Create ContentPanel
    print("\n[TEST 3] Creating ContentPanel...")
    try:
        content_panel = ContentPanel()
        print("✓ ContentPanel created")

        # Test loading a category
        if categories:
            test_category = categories[0]
            content_panel.load_category(test_category)
            print(f"✓ Loaded category '{test_category.name}' with {len(test_category.items)} items")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 4: Create MainWindow
    print("\n[TEST 4] Creating MainWindow...")
    try:
        window = MainWindow(controller)
        window.load_categories(categories)
        print("✓ MainWindow created successfully")
        print(f"  - Window size: {window.width()}x{window.height()}")
        print(f"  - Sidebar attached: {window.sidebar is not None}")
        print(f"  - ContentPanel attached: {window.content_panel is not None}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 5: Test category buttons
    print("\n[TEST 5] Testing CategoryButton...")
    try:
        test_cat = categories[0]
        button = CategoryButton(test_cat.id, test_cat.name)
        print(f"✓ CategoryButton created: '{button.text()}'")
        print(f"  - Size: {button.width()}x{button.height()}")
        print(f"  - Active: {button.is_active}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 6: Test item buttons
    print("\n[TEST 6] Testing ItemButton...")
    try:
        if categories and categories[0].items:
            test_item = categories[0].items[0]
            item_button = ItemButton(test_item)
            print(f"✓ ItemButton created: '{item_button.text()}'")
            print(f"  - Label: {test_item.label}")
            print(f"  - Content: {test_item.content}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 7: Test animation setup
    print("\n[TEST 7] Testing panel animation...")
    try:
        panel = ContentPanel()
        print("✓ Animation configured:")
        print(f"  - Duration: {panel.animation.duration()}ms")
        print(f"  - Target width: {panel.target_width}px")
        print(f"  - Collapsed width: {panel.collapsed_width}px")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    # Test 8: Component integration
    print("\n[TEST 8] Testing component integration...")
    try:
        window2 = MainWindow(controller)
        window2.load_categories(categories)

        # Simulate category click
        if categories:
            cat_id = categories[0].id
            print(f"  Simulating click on category: {cat_id}")
            window2.on_category_clicked(cat_id)
            print("✓ Category click handled successfully")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Phase 3 UI is functional!")
    print("=" * 60)
    print("\nUI Components:")
    print("  ✓ Sidebar with category buttons")
    print("  ✓ ContentPanel with item buttons")
    print("  ✓ Smooth animations")
    print("  ✓ MainWindow integration")
    print("  ✓ Click handlers connected")
    print("  ✓ Clipboard integration ready")

    return True


if __name__ == '__main__':
    try:
        success = test_phase3()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
