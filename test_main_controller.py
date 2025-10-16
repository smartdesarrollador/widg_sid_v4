"""
Test MainController con SQLite
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from controllers.main_controller import MainController

def test_main_controller():
    """Test que MainController funciona con SQLite"""
    print("=== TEST: MainController con SQLite ===\n")

    # 1. Crear instancia
    print("[1/5] Creando MainController...")
    controller = MainController()
    print("  [OK] MainController creado\n")

    # 2. Verificar categorias cargadas
    print("[2/5] Verificando categorias...")
    categories = controller.get_categories()
    print(f"  [OK] {len(categories)} categorias cargadas")
    for cat in categories[:3]:  # Mostrar solo las primeras 3
        print(f"    - {cat.name}: {len(cat.items)} items")
    print()

    # 3. Verificar get_category
    print("[3/5] Probando get_category()...")
    cat = controller.get_category("1")
    if cat:
        print(f"  [OK] Categoria obtenida: {cat.name}")
        print(f"       Items: {len(cat.items)}")
    else:
        print("  [ERROR] Error obteniendo categoria")
    print()

    # 4. Verificar settings
    print("[4/5] Probando settings...")
    theme = controller.get_setting("theme", "light")
    print(f"  [OK] Theme: {theme}")

    panel_width = controller.get_setting("panel_width", 250)
    print(f"  [OK] Panel width: {panel_width}")
    print()

    # 5. Verificar set_current_category
    print("[5/5] Probando set_current_category()...")
    if controller.set_current_category("1"):
        print(f"  [OK] Categoria activa: {controller.get_current_category().name}")
    else:
        print("  [ERROR] Error configurando categoria activa")
    print()

    # Cleanup
    del controller
    print("=== TEST COMPLETADO ===")

if __name__ == '__main__':
    test_main_controller()
