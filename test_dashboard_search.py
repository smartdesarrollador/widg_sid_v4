"""
Test dashboard search functionality
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.db_manager import DBManager
from core.dashboard_manager import DashboardManager

def main():
    print("=" * 60)
    print("TEST: Dashboard Search Functionality")
    print("=" * 60)

    # Initialize
    db_path = Path(__file__).parent / 'widget_sidebar.db'
    db = DBManager(str(db_path))
    dashboard_mgr = DashboardManager(db)

    # Get structure
    structure = dashboard_mgr.get_full_structure()
    print(f"\nTotal categories: {len(structure['categories'])}")
    print(f"Total items: {sum(len(cat['items']) for cat in structure['categories'])}")

    # Test 1: Search for "test" in content
    print("\n" + "=" * 60)
    print("TEST 1: Search for 'test' in content")
    print("=" * 60)

    scope_filters = {
        'categories': False,
        'items': False,
        'tags': False,
        'content': True
    }

    matches = dashboard_mgr.search('test', scope_filters, structure)
    print(f"Found {len(matches)} matches:")

    for match_type, cat_idx, item_idx in matches[:10]:  # Show first 10
        category = structure['categories'][cat_idx]
        if item_idx == -1:
            print(f"  - Category: {category['name']}")
        else:
            item = category['items'][item_idx]
            print(f"  - Item: {item['label']} in {category['name']}")
            print(f"    Content preview: {item['content'][:50]}...")

    # Test 2: Search in all scopes
    print("\n" + "=" * 60)
    print("TEST 2: Search for 'docker' in all scopes")
    print("=" * 60)

    scope_filters = {
        'categories': True,
        'items': True,
        'tags': True,
        'content': True
    }

    matches = dashboard_mgr.search('docker', scope_filters, structure)
    print(f"Found {len(matches)} matches:")

    for match_type, cat_idx, item_idx in matches[:10]:
        category = structure['categories'][cat_idx]
        if item_idx == -1:
            print(f"  - Category match: {category['name']}")
        else:
            item = category['items'][item_idx]
            print(f"  - Item match: {item['label']} ({match_type})")

    # Test 3: Filter favorites
    print("\n" + "=" * 60)
    print("TEST 3: Filter favorites")
    print("=" * 60)

    state_filters = {'favorites': True, 'sensitive': False, 'normal': False}
    filtered_structure = dashboard_mgr.filter_and_sort_structure(
        structure=structure,
        state_filters=state_filters
    )

    total_favorites = sum(len(cat['items']) for cat in filtered_structure['categories'])
    print(f"Total favorite items: {total_favorites}")

    for category in filtered_structure['categories']:
        if category['items']:
            print(f"\n  Category: {category['name']}")
            for item in category['items']:
                print(f"    ⭐ {item['label']}")

    print("\n" + "=" * 60)
    print("TEST: Complete")
    print("=" * 60)

    db.close()

if __name__ == '__main__':
    main()
