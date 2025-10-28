"""
Script de testing para verificar la funcionalidad de is_active e is_archived
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.db_manager import DBManager
from core.config_manager import ConfigManager
from models.item import Item, ItemType

def test_database_operations():
    """Test 1: Verificar operaciones de base de datos"""
    print("\n" + "="*80)
    print("TEST 1: Operaciones de Base de Datos")
    print("="*80)

    db = DBManager("widget_sidebar.db")

    # Crear categoría de prueba
    cat_id = db.add_category(
        name="TEST_ACTIVE_ARCHIVED",
        icon="🧪",
        is_predefined=False
    )
    print(f"[OK] Categoria de prueba creada (ID: {cat_id})")

    # Crear items de prueba con diferentes combinaciones de estados
    test_cases = [
        ("Item Normal", True, False),       # Activo, NO archivado
        ("Item Archivado", True, True),     # Activo, archivado
        ("Item Inactivo", False, False),    # Inactivo, NO archivado
        ("Item Inactivo Archivado", False, True),  # Inactivo, archivado
    ]

    item_ids = []
    for label, is_active, is_archived in test_cases:
        item_id = db.add_item(
            category_id=cat_id,
            label=label,
            content=f"Contenido de {label}",
            item_type="TEXT",
            is_active=is_active,
            is_archived=is_archived
        )
        item_ids.append(item_id)
        print(f"[OK] Item creado: {label} (ID: {item_id}, active={is_active}, archived={is_archived})")

    # Verificar que los items se guardaron correctamente
    items = db.get_items_by_category(cat_id)
    print(f"\n[OK] Items recuperados de DB: {len(items)}")

    for item in items:
        print(f"  - {item['label']}: active={item['is_active']}, archived={item['is_archived']}")

    # Verificar valores
    assert len(items) == 4, "Deberían existir 4 items"
    assert items[0]['is_active'] == True and items[0]['is_archived'] == False, "Item Normal"
    assert items[1]['is_active'] == True and items[1]['is_archived'] == True, "Item Archivado"
    assert items[2]['is_active'] == False and items[2]['is_archived'] == False, "Item Inactivo"
    assert items[3]['is_active'] == False and items[3]['is_archived'] == True, "Item Inactivo Archivado"

    print("\n[PASS] TEST 1 PASADO: Todos los items se guardaron y recuperaron correctamente")

    return db, cat_id, item_ids


def test_config_manager(db, cat_id):
    """Test 2: Verificar ConfigManager"""
    print("\n" + "="*80)
    print("TEST 2: ConfigManager - _dict_to_item")
    print("="*80)

    config = ConfigManager()

    # Obtener categoría con items
    category = config.get_category(cat_id)

    print(f"[OK] Categoria recuperada: {category.name} ({len(category.items)} items)")

    for item in category.items:
        is_active = getattr(item, 'is_active', None)
        is_archived = getattr(item, 'is_archived', None)
        print(f"  - {item.label}: active={is_active}, archived={is_archived}")

    # Verificar que los atributos están presentes
    assert len(category.items) == 4, "Deberían existir 4 items"

    for item in category.items:
        assert hasattr(item, 'is_active'), f"Item {item.label} no tiene atributo is_active"
        assert hasattr(item, 'is_archived'), f"Item {item.label} no tiene atributo is_archived"

    print("\n[PASS] TEST 2 PASADO: ConfigManager convierte correctamente los items")

    return config, category


def test_filtering_logic():
    """Test 3: Verificar lógica de filtrado"""
    print("\n" + "="*80)
    print("TEST 3: Lógica de Filtrado")
    print("="*80)

    # Crear items de prueba
    items = [
        Item("1", "Normal", "content", ItemType.TEXT, is_active=True, is_archived=False),
        Item("2", "Archivado", "content", ItemType.TEXT, is_active=True, is_archived=True),
        Item("3", "Inactivo", "content", ItemType.TEXT, is_active=False, is_archived=False),
        Item("4", "Inactivo Archivado", "content", ItemType.TEXT, is_active=False, is_archived=True),
    ]

    # Test filtro "normal" (activo y NO archivado)
    normal_items = [item for item in items if getattr(item, 'is_active', True) and not getattr(item, 'is_archived', False)]
    print(f"Filtro 'Normal': {len(normal_items)} items")
    for item in normal_items:
        print(f"  - {item.label}")
    assert len(normal_items) == 1, "Filtro Normal debería retornar 1 item"
    assert normal_items[0].label == "Normal", "Debería ser el item Normal"

    # Test filtro "archived" (archivado)
    archived_items = [item for item in items if getattr(item, 'is_archived', False)]
    print(f"\nFiltro 'Archivados': {len(archived_items)} items")
    for item in archived_items:
        print(f"  - {item.label}")
    assert len(archived_items) == 2, "Filtro Archivados debería retornar 2 items"

    # Test filtro "inactive" (inactivo)
    inactive_items = [item for item in items if not getattr(item, 'is_active', True)]
    print(f"\nFiltro 'Inactivos': {len(inactive_items)} items")
    for item in inactive_items:
        print(f"  - {item.label}")
    assert len(inactive_items) == 2, "Filtro Inactivos debería retornar 2 items"

    # Test filtro "all" (todos)
    all_items = items
    print(f"\nFiltro 'Todos': {len(all_items)} items")
    assert len(all_items) == 4, "Filtro Todos debería retornar 4 items"

    print("\n[PASS] TEST 3 PASADO: Logica de filtrado funciona correctamente")


def test_update_item(db, cat_id, item_ids):
    """Test 4: Verificar actualización de items"""
    print("\n" + "="*80)
    print("TEST 4: Actualización de Items")
    print("="*80)

    # Tomar el primer item y cambiar su estado
    item_id = item_ids[0]

    # Cambiar de activo a inactivo
    db.update_item(
        item_id=item_id,
        is_active=False,
        is_archived=True
    )
    print(f"[OK] Item {item_id} actualizado: active=False, archived=True")

    # Verificar que se actualizó
    items = db.get_items_by_category(cat_id)
    updated_item = [item for item in items if item['id'] == item_id][0]

    print(f"[OK] Item recuperado: active={updated_item['is_active']}, archived={updated_item['is_archived']}")

    assert updated_item['is_active'] == False, "is_active deberia ser False"
    assert updated_item['is_archived'] == True, "is_archived deberia ser True"

    print("\n[PASS] TEST 4 PASADO: Actualizacion de items funciona correctamente")


def cleanup(db, cat_id):
    """Limpiar datos de prueba"""
    print("\n" + "="*80)
    print("CLEANUP: Eliminando datos de prueba")
    print("="*80)

    db.delete_category(cat_id)
    print(f"[OK] Categoria de prueba eliminada (ID: {cat_id})")

    db.close()
    print("[OK] Conexion a DB cerrada")


def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*80)
    print("INICIANDO TESTING DE is_active / is_archived")
    print("="*80)

    try:
        # Test 1: Operaciones de base de datos
        db, cat_id, item_ids = test_database_operations()

        # Test 2: ConfigManager
        config, category = test_config_manager(db, cat_id)

        # Test 3: Lógica de filtrado
        test_filtering_logic()

        # Test 4: Actualización de items
        test_update_item(db, cat_id, item_ids)

        # Cleanup
        cleanup(db, cat_id)

        # Resumen final
        print("\n" + "="*80)
        print("[SUCCESS] TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*80)
        print("\nResumen de tests:")
        print("  [PASS] Test 1: Operaciones de Base de Datos")
        print("  [PASS] Test 2: ConfigManager - _dict_to_item")
        print("  [PASS] Test 3: Logica de Filtrado")
        print("  [PASS] Test 4: Actualizacion de Items")
        print("\nFuncionalidad is_active/is_archived verificada correctamente!")
        print("="*80 + "\n")

        return True

    except Exception as e:
        print("\n" + "="*80)
        print("[ERROR] ERROR EN TESTING")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

        # Intentar cleanup aunque haya fallado
        try:
            cleanup(db, cat_id)
        except:
            pass

        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
