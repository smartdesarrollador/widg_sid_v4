"""
Test Completo del Sistema - Widget Sidebar v2.0
Verifica todos los componentes de la aplicación
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def run_all_tests():
    """Ejecutar todos los tests del sistema"""
    print("=" * 70)
    print(" WIDGET SIDEBAR v2.0 - TEST SUITE COMPLETO")
    print("=" * 70)
    print()

    tests_passed = 0
    tests_failed = 0

    # TEST 1: Base de datos
    print("[TEST 1/5] Base de Datos SQLite")
    print("-" * 70)
    try:
        from database.db_manager import DBManager
        db = DBManager("widget_sidebar.db")

        # Verificar tablas
        settings = db.get_all_settings()
        categories = db.get_categories()
        items_count = sum(len(db.get_items_by_category(cat['id'])) for cat in categories)

        print(f"  [OK] Tablas verificadas")
        print(f"       - Settings: {len(settings)}")
        print(f"       - Categorias: {len(categories)}")
        print(f"       - Items: {items_count}")
        db.close()
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] {e}")
        tests_failed += 1
    print()

    # TEST 2: ConfigManager
    print("[TEST 2/5] ConfigManager con SQLite")
    print("-" * 70)
    try:
        from core.config_manager import ConfigManager
        config = ConfigManager(db_path="widget_sidebar.db")

        categories = config.get_categories()
        total_items = sum(len(cat.items) for cat in categories)

        print(f"  [OK] ConfigManager operacional")
        print(f"       - Categorias cargadas: {len(categories)}")
        print(f"       - Items totales: {total_items}")

        # Test get_category
        cat = config.get_category("1")
        if cat:
            print(f"       - get_category(1): {cat.name} ({len(cat.items)} items)")

        # Test settings
        theme = config.get_setting("theme", "light")
        print(f"       - Setting theme: {theme}")

        config.close()
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] {e}")
        tests_failed += 1
    print()

    # TEST 3: MainController
    print("[TEST 3/5] MainController")
    print("-" * 70)
    try:
        from controllers.main_controller import MainController
        controller = MainController()

        categories = controller.get_categories()
        print(f"  [OK] MainController inicializado")
        print(f"       - Categorias: {len(categories)}")

        # Test set_current_category
        if controller.set_current_category("1"):
            current = controller.get_current_category()
            print(f"       - Categoria activa: {current.name}")

        # Test settings
        theme = controller.get_setting("theme", "light")
        print(f"       - Theme setting: {theme}")

        del controller
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] {e}")
        tests_failed += 1
    print()

    # TEST 4: Modelos (Category & Item)
    print("[TEST 4/5] Modelos de Datos")
    print("-" * 70)
    try:
        from models.category import Category
        from models.item import Item, ItemType

        # Test Category
        cat = Category("test", "Test Category", "📁")
        print(f"  [OK] Category model: {cat.name}")

        # Test Item
        item = Item("1", "Test Item", "test content", ItemType.TEXT)
        print(f"  [OK] Item model: {item.label}")

        cat.add_item(item)
        print(f"       - Item agregado a categoria: {len(cat.items)} items")

        # Test validation
        if cat.validate():
            print(f"       - Validacion: OK")

        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] {e}")
        tests_failed += 1
    print()

    # TEST 5: Migración y Compatibilidad
    print("[TEST 5/5] Migración y Compatibilidad")
    print("-" * 70)
    try:
        # Verificar archivos de backup
        backup_files = []
        if Path("config.json.backup").exists():
            backup_files.append("config.json.backup")
        if Path("default_categories.json.backup").exists():
            backup_files.append("default_categories.json.backup")

        print(f"  [OK] Backups creados: {len(backup_files)}")
        for backup in backup_files:
            size = Path(backup).stat().st_size
            print(f"       - {backup} ({size} bytes)")

        # Verificar base de datos
        db_path = Path("widget_sidebar.db")
        if db_path.exists():
            db_size = db_path.stat().st_size
            print(f"  [OK] Base de datos: widget_sidebar.db ({db_size} bytes)")

        # Verificar export/import (si existe)
        from core.config_manager import ConfigManager
        config = ConfigManager(db_path="widget_sidebar.db")

        # Test export
        export_path = Path("test_export.json")
        if config.export_config(export_path):
            print(f"  [OK] Export a JSON funcional")
            export_path.unlink()  # Limpiar

        config.close()
        tests_passed += 1
    except Exception as e:
        print(f"  [ERROR] {e}")
        tests_failed += 1
    print()

    # RESUMEN
    print("=" * 70)
    print(" RESUMEN DE TESTS")
    print("=" * 70)
    print(f"  Tests pasados: {tests_passed}/5")
    print(f"  Tests fallidos: {tests_failed}/5")
    print()

    if tests_failed == 0:
        print("  [OK] TODOS LOS TESTS PASARON")
        print()
        print("  El sistema esta listo para:")
        print("    1. Ejecutar en modo desarrollo")
        print("    2. Compilar con PyInstaller")
        print("    3. Distribuir como ejecutable")
        print()
        return True
    else:
        print("  [ERROR] ALGUNOS TESTS FALLARON")
        print()
        print("  Revisa los errores antes de continuar")
        print()
        return False

if __name__ == '__main__':
    print()
    success = run_all_tests()
    print("=" * 70)
    print()
    sys.exit(0 if success else 1)
