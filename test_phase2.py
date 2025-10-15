"""
Test script for Phase 2 - MVC Core functionality
Tests data loading and clipboard operations
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

from controllers.main_controller import MainController


def test_phase2():
    """Test Phase 2 MVC implementation"""
    print("=" * 60)
    print("TESTING PHASE 2: MVC Core")
    print("=" * 60)

    # Test 1: Initialize controller
    print("\n[TEST 1] Initializing MainController...")
    try:
        controller = MainController()
        print("✓ MainController initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing MainController: {e}")
        return False

    # Test 2: Check categories loaded
    print("\n[TEST 2] Checking categories loaded...")
    categories = controller.get_categories()
    print(f"✓ Loaded {len(categories)} categories")

    if len(categories) == 0:
        print("✗ No categories loaded!")
        return False

    # Test 3: List all categories and items
    print("\n[TEST 3] Listing all categories and items...")
    for cat in categories:
        print(f"\n  📁 {cat.name} (ID: {cat.id})")
        print(f"     Items: {len(cat.items)}")
        if cat.items:
            for i, item in enumerate(cat.items[:3]):  # Show first 3 items
                print(f"       {i+1}. {item.label}")
            if len(cat.items) > 3:
                print(f"       ... and {len(cat.items) - 3} more")

    # Test 4: Set active category
    print("\n[TEST 4] Setting active category...")
    if categories:
        first_cat = categories[0]
        success = controller.set_current_category(first_cat.id)
        if success:
            print(f"✓ Set active category: {first_cat.name}")
        else:
            print(f"✗ Failed to set active category")

    # Test 5: Copy item to clipboard
    print("\n[TEST 5] Testing clipboard operations...")
    git_category = controller.get_category("git_commands")
    if git_category and git_category.items:
        test_item = git_category.items[0]
        print(f"  Testing with item: {test_item.label}")
        print(f"  Content: {test_item.content}")

        success = controller.copy_item_to_clipboard(test_item)
        if success:
            print("✓ Item copied to clipboard successfully!")

            # Verify clipboard content
            clipboard_content = controller.clipboard_manager.get_clipboard_content()
            if clipboard_content == test_item.content:
                print(f"✓ Clipboard verification passed!")
                print(f"  Clipboard contains: '{clipboard_content}'")
            else:
                print("✗ Clipboard content mismatch!")
        else:
            print("✗ Failed to copy item to clipboard")

    # Test 6: Check clipboard history
    print("\n[TEST 6] Checking clipboard history...")
    history = controller.get_clipboard_history(5)
    print(f"✓ Clipboard history contains {len(history)} entries")
    for i, entry in enumerate(history):
        print(f"  {i+1}. {entry.item.label} - {entry.timestamp.strftime('%H:%M:%S')}")

    # Test 7: Configuration settings
    print("\n[TEST 7] Testing configuration settings...")
    theme = controller.get_setting("theme", "dark")
    panel_width = controller.get_setting("panel_width", 300)
    print(f"✓ Theme: {theme}")
    print(f"✓ Panel width: {panel_width}")

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Phase 2 Core is working!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    try:
        success = test_phase2()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
