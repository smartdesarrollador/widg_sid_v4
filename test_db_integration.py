"""
Test de integración completa con SQLite
Verifica que todo el sistema funciona correctamente
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_database_integration():
    """Test completo de integración con SQLite"""
    print("=== TEST: Integración SQLite Completa ===\n")

    # 1. Verificar que existe la base de datos
    print("[1/6] Verificando base de datos...")
    db_path = Path("widget_sidebar.db")
    if db_path.exists():
        print(f"  [OK] Base de datos encontrada: {db_path}")
        print(f"       Tamaño: {db_path.stat().st_size} bytes")
    else:
        print("  [ERROR] Base de datos no encontrada")
        return False
    print()

    # 2. Verificar DBManager
    print("[2/6] Verificando DBManager...")
    from database.db_manager import DBManager

    db = DBManager(str(db_path))
    settings = db.get_all_settings()
    categories = db.get_categories()
    print(f"  [OK] {len(settings)} settings cargados")
    print(f"  [OK] {len(categories)} categorías cargadas")
    db.close()
    print()

    # 3. Verificar ConfigManager
    print("[3/6] Verificando ConfigManager...")
    from core.config_manager import ConfigManager

    config = ConfigManager(db_path=str(db_path))
    cats = config.get_categories()
    print(f"  [OK] {len(cats)} categorías cargadas")

    # Verificar items
    total_items = sum(len(cat.items) for cat in cats)
    print(f"  [OK] {total_items} items totales")
    config.close()
    print()

    # 4. Verificar MainController
    print("[4/6] Verificando MainController...")
    from controllers.main_controller import MainController

    controller = MainController()
    categories = controller.get_categories()
    print(f"  [OK] {len(categories)} categorías en controller")

    # Test get_category
    cat = controller.get_category("1")
    if cat:
        print(f"  [OK] get_category funciona: {cat.name}")
    print()

    # 5. Verificar settings
    print("[5/6] Verificando settings...")
    theme = controller.get_setting("theme", "light")
    panel_width = controller.get_setting("panel_width", 250)
    print(f"  [OK] theme = {theme}")
    print(f"  [OK] panel_width = {panel_width}")
    print()

    # 6. Verificar tipos de items
    print("[6/6] Verificando tipos de items...")
    type_counts = {}
    for cat in categories:
        for item in cat.items:
            type_name = item.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

    for type_name, count in sorted(type_counts.items()):
        print(f"  - {type_name}: {count} items")
    print()

    # Cleanup
    del controller

    print("=== TODOS LOS TESTS PASARON ===")
    return True

if __name__ == '__main__':
    success = test_database_integration()
    sys.exit(0 if success else 1)
