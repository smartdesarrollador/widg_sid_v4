"""
Debug script to check dashboard data loading
"""
import sys
import io
from pathlib import Path

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.db_manager import DBManager
from core.dashboard_manager import DashboardManager

def main():
    print("=" * 60)
    print("DEBUG: Dashboard Data Loading")
    print("=" * 60)

    # Get database path
    db_path = Path(__file__).parent / 'widget_sidebar.db'
    print(f"\n1. Database path: {db_path}")
    print(f"   Database exists: {db_path.exists()}")

    if not db_path.exists():
        print("   ERROR: Database file does not exist!")
        return

    # Initialize DBManager
    print("\n2. Initializing DBManager...")
    db = DBManager(str(db_path))

    # Get categories directly from DB
    print("\n3. Getting categories from database...")
    categories = db.get_categories()
    print(f"   Total categories: {len(categories)}")

    if not categories:
        print("   ERROR: No categories found in database!")
        return

    # Show first 5 categories
    print("\n4. First 5 categories:")
    for i, cat in enumerate(categories[:5], 1):
        print(f"   {i}. {cat.get('icon', '?')} {cat.get('name', 'N/A')} (ID: {cat.get('id', 'N/A')})")

        # Get items for this category
        items = db.get_items_by_category(cat['id'])
        print(f"      Items: {len(items)}")

        if items:
            # Show first item
            first_item = items[0]
            print(f"      - {first_item.get('label', 'N/A')} ({first_item.get('type', 'N/A')})")

    # Initialize DashboardManager
    print("\n5. Initializing DashboardManager...")
    dashboard_mgr = DashboardManager(db)

    # Get full structure
    print("\n6. Getting full structure...")
    structure = dashboard_mgr.get_full_structure()

    print(f"   Structure keys: {structure.keys()}")
    print(f"   Categories in structure: {len(structure.get('categories', []))}")

    # Show structure details
    if structure.get('categories'):
        print("\n7. Structure details:")
        for i, cat in enumerate(structure['categories'][:5], 1):
            print(f"   {i}. {cat.get('name', 'N/A')}")
            print(f"      Icon: {cat.get('icon', 'N/A')}")
            print(f"      Items: {len(cat.get('items', []))}")
            print(f"      Tags: {cat.get('tags', [])}")
    else:
        print("\n7. ERROR: No categories in structure!")
        print(f"   Full structure: {structure}")

    # Calculate statistics
    print("\n8. Calculating statistics...")
    stats = dashboard_mgr.calculate_statistics(structure)
    print(f"   Total categories: {stats.get('total_categories', 0)}")
    print(f"   Total items: {stats.get('total_items', 0)}")
    print(f"   Total favorites: {stats.get('total_favorites', 0)}")
    print(f"   Total sensitive: {stats.get('total_sensitive', 0)}")

    print("\n" + "=" * 60)
    print("DEBUG: Complete")
    print("=" * 60)

    # Close database
    db.close()

if __name__ == '__main__':
    main()
