"""
Test script for pinned panels CRUD operations
Run this to verify all database methods are working correctly

Usage:
    python test_pinned_panels_crud.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.db_manager import DBManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_pinned_panels_crud():
    """Test all CRUD operations for pinned panels"""
    print("="*60)
    print("Testing Pinned Panels CRUD Operations")
    print("="*60)

    # Create in-memory database for testing
    print("\n[1/12] Creating test database...")
    db = DBManager(":memory:")
    print("[OK] Database created")

    # Add a test category first (needed for foreign key)
    print("\n[2/12] Adding test category...")
    category_id = db.add_category(name="Test Category", icon="+")
    print(f"[OK] Category added with ID: {category_id}")

    # Test 1: Save pinned panel
    print("\n[3/12] Testing save_pinned_panel()...")
    panel_id_1 = db.save_pinned_panel(
        category_id=category_id,
        x_pos=100,
        y_pos=200,
        width=350,
        height=500,
        is_minimized=False,
        custom_name="My Custom Panel",
        custom_color="#0d7377"
    )
    print(f"[OK] Panel saved with ID: {panel_id_1}")

    # Test 2: Save another panel
    print("\n[4/12] Testing save_pinned_panel() again...")
    panel_id_2 = db.save_pinned_panel(
        category_id=category_id,
        x_pos=500,
        y_pos=300,
        width=400,
        height=600,
        is_minimized=True
    )
    print(f"[OK] Second panel saved with ID: {panel_id_2}")

    # Test 3: Get all active panels
    print("\n[5/12] Testing get_pinned_panels(active_only=True)...")
    active_panels = db.get_pinned_panels(active_only=True)
    print(f"[OK] Retrieved {len(active_panels)} active panels")
    assert len(active_panels) == 2, "Should have 2 active panels"

    # Test 4: Get panel by ID
    print("\n[6/12] Testing get_panel_by_id()...")
    panel = db.get_panel_by_id(panel_id_1)
    print(f"[OK] Retrieved panel: {panel['custom_name']}")
    assert panel is not None, "Panel should exist"
    assert panel['custom_name'] == "My Custom Panel", "Name should match"
    assert panel['custom_color'] == "#0d7377", "Color should match"
    assert panel['category_name'] == "Test Category", "Category name should match"

    # Test 5: Update panel
    print("\n[7/12] Testing update_pinned_panel()...")
    success = db.update_pinned_panel(
        panel_id_1,
        x_position=150,
        y_position=250,
        custom_name="Updated Panel Name",
        custom_color="#ff5733"
    )
    print(f"[OK] Panel updated: {success}")
    assert success, "Update should succeed"

    # Verify update
    updated_panel = db.get_panel_by_id(panel_id_1)
    assert updated_panel['x_position'] == 150, "X position should be updated"
    assert updated_panel['custom_name'] == "Updated Panel Name", "Name should be updated"
    assert updated_panel['custom_color'] == "#ff5733", "Color should be updated"
    print("[OK] Update verified")

    # Test 6: Update last opened
    print("\n[8/12] Testing update_panel_last_opened()...")
    db.update_panel_last_opened(panel_id_1)
    panel_after_open = db.get_panel_by_id(panel_id_1)
    assert panel_after_open['open_count'] == 1, "Open count should be 1"
    print(f"[OK] Last opened updated, open_count: {panel_after_open['open_count']}")

    # Test 7: Get recent panels
    print("\n[9/12] Testing get_recent_panels()...")
    recent_panels = db.get_recent_panels(limit=5)
    print(f"[OK] Retrieved {len(recent_panels)} recent panels")
    assert len(recent_panels) == 2, "Should have 2 panels"
    # Most recently opened should be first
    assert recent_panels[0]['id'] == panel_id_1, "Most recent should be panel 1"

    # Test 8: Get panel by category
    print("\n[10/12] Testing get_panel_by_category()...")
    category_panel = db.get_panel_by_category(category_id)
    print(f"[OK] Found panel for category: {category_panel['category_name']}")
    assert category_panel is not None, "Should find panel for category"

    # Test 9: Deactivate all panels
    print("\n[11/12] Testing deactivate_all_panels()...")
    db.deactivate_all_panels()
    active_after_deactivate = db.get_pinned_panels(active_only=True)
    print(f"[OK] Active panels after deactivation: {len(active_after_deactivate)}")
    assert len(active_after_deactivate) == 0, "Should have no active panels"

    # Verify we can still get all panels (including inactive)
    all_panels = db.get_pinned_panels(active_only=False)
    assert len(all_panels) == 2, "Should still have 2 panels total"
    print("[OK] All panels still exist (marked as inactive)")

    # Test 10: Delete panel
    print("\n[12/12] Testing delete_pinned_panel()...")
    success = db.delete_pinned_panel(panel_id_2)
    print(f"[OK] Panel deleted: {success}")
    assert success, "Deletion should succeed"

    # Verify deletion
    deleted_panel = db.get_panel_by_id(panel_id_2)
    assert deleted_panel is None, "Panel should not exist after deletion"
    print("[OK] Deletion verified")

    # Final count
    final_panels = db.get_pinned_panels(active_only=False)
    assert len(final_panels) == 1, "Should have 1 panel remaining"
    print(f"[OK] Final panel count: {len(final_panels)}")

    # Close database
    db.close()

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
    print("\nTest Summary:")
    print("   [OK] save_pinned_panel() - Working")
    print("   [OK] get_pinned_panels() - Working")
    print("   [OK] get_panel_by_id() - Working")
    print("   [OK] update_pinned_panel() - Working")
    print("   [OK] update_panel_last_opened() - Working")
    print("   [OK] get_recent_panels() - Working")
    print("   [OK] get_panel_by_category() - Working")
    print("   [OK] deactivate_all_panels() - Working")
    print("   [OK] delete_pinned_panel() - Working")
    print("\nAll CRUD operations for pinned panels are functional!")
    print("="*60)


if __name__ == "__main__":
    try:
        test_pinned_panels_crud()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
