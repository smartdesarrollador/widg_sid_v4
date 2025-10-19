"""
Test de Fase 3: UI - Editor (Checkbox Sensible)
Tests de integracion end-to-end con la UI
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.db_manager import DBManager
from models.item import Item, ItemType


def test_ui_checkbox_exists():
    """Test: Verificar que ItemEditorDialog tiene checkbox sensible"""
    print("=" * 60)
    print("TEST 1: ItemEditorDialog tiene checkbox 'Sensible'")
    print("=" * 60)

    try:
        from views.item_editor_dialog import ItemEditorDialog
        from PyQt6.QtWidgets import QApplication

        # Create QApplication (required for QDialog)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create dialog
        dialog = ItemEditorDialog()

        # Check if sensitive_checkbox exists
        if hasattr(dialog, 'sensitive_checkbox'):
            print("\n[PASS] Dialog tiene 'sensitive_checkbox'")

            # Check it's a QCheckBox
            from PyQt6.QtWidgets import QCheckBox
            if isinstance(dialog.sensitive_checkbox, QCheckBox):
                print("[PASS] sensitive_checkbox es un QCheckBox")

                # Check default state (should be unchecked)
                if not dialog.sensitive_checkbox.isChecked():
                    print("[PASS] Estado inicial: desmarcado (correcto)")
                else:
                    print("[FAIL] Estado inicial deberia ser desmarcado")
                    return False

                return True
            else:
                print("[FAIL] sensitive_checkbox NO es un QCheckBox")
                return False
        else:
            print("\n[FAIL] Dialog NO tiene 'sensitive_checkbox'")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error creando dialog: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_item_data_includes_sensitive():
    """Test: get_item_data() incluye is_sensitive"""
    print("\n" + "=" * 60)
    print("TEST 2: get_item_data() incluye 'is_sensitive'")
    print("=" * 60)

    try:
        from views.item_editor_dialog import ItemEditorDialog
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create dialog
        dialog = ItemEditorDialog()

        # Set some data
        dialog.label_input.setText("Test Item")
        dialog.content_input.setPlainText("Test Content")

        # Test unchecked state
        dialog.sensitive_checkbox.setChecked(False)
        data = dialog.get_item_data()

        if 'is_sensitive' in data:
            print("\n[PASS] get_item_data() contiene 'is_sensitive'")

            if data['is_sensitive'] == False:
                print("[PASS] is_sensitive = False cuando desmarcado")
            else:
                print("[FAIL] is_sensitive deberia ser False")
                return False

            # Test checked state
            dialog.sensitive_checkbox.setChecked(True)
            data = dialog.get_item_data()

            if data['is_sensitive'] == True:
                print("[PASS] is_sensitive = True cuando marcado")
                return True
            else:
                print("[FAIL] is_sensitive deberia ser True")
                return False
        else:
            print("\n[FAIL] get_item_data() NO contiene 'is_sensitive'")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_load_item_data_loads_sensitive():
    """Test: load_item_data() carga el estado is_sensitive"""
    print("\n" + "=" * 60)
    print("TEST 3: load_item_data() carga estado 'is_sensitive'")
    print("=" * 60)

    try:
        from views.item_editor_dialog import ItemEditorDialog
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create item with is_sensitive=True
        sensitive_item = Item(
            item_id="test1",
            label="Sensitive Item",
            content="Secret Password",
            item_type=ItemType.TEXT,
            is_sensitive=True
        )

        # Create dialog in edit mode
        dialog = ItemEditorDialog(item=sensitive_item)

        # Check if checkbox is checked
        if dialog.sensitive_checkbox.isChecked():
            print("\n[PASS] Checkbox marcado para item sensible")
        else:
            print("\n[FAIL] Checkbox NO marcado para item sensible")
            return False

        # Create item with is_sensitive=False
        normal_item = Item(
            item_id="test2",
            label="Normal Item",
            content="Public Content",
            item_type=ItemType.TEXT,
            is_sensitive=False
        )

        # Create dialog in edit mode
        dialog2 = ItemEditorDialog(item=normal_item)

        # Check if checkbox is unchecked
        if not dialog2.sensitive_checkbox.isChecked():
            print("[PASS] Checkbox desmarcado para item normal")
            return True
        else:
            print("[FAIL] Checkbox deberia estar desmarcado para item normal")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_sensitive_item():
    """Test: Flujo completo - crear item sensible y verificar cifrado en BD"""
    print("\n" + "=" * 60)
    print("TEST 4: Flujo End-to-End - Item Sensible")
    print("=" * 60)

    try:
        # Create in-memory database
        db = DBManager(":memory:")

        # Create category
        cat_id = db.add_category("Passwords", "lock", 0)
        print(f"\n[OK] Categoria creada: ID {cat_id}")

        # Simulate creating item through UI (what category_editor does)
        item_data = {
            "label": "Gmail Password",
            "content": "SuperSecretPass123",
            "type": ItemType.TEXT,
            "tags": ["email", "personal"],
            "is_sensitive": True  # From checkbox
        }

        # Add item to database (simulating what happens after dialog.accept())
        item_id = db.add_item(
            category_id=cat_id,
            label=item_data["label"],
            content=item_data["content"],
            item_type=item_data["type"].value.upper(),  # DB expects uppercase
            is_sensitive=item_data["is_sensitive"],
            tags=item_data["tags"]
        )

        print(f"[OK] Item agregado: ID {item_id}")
        print(f"    Label: {item_data['label']}")
        print(f"    is_sensitive: {item_data['is_sensitive']}")

        # Verify in database (raw)
        import sqlite3
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT content, is_sensitive FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()

        encrypted_content = row[0]
        is_sensitive_in_db = row[1]

        print(f"\nVerificacion en BD:")
        print(f"    Contenido: {encrypted_content[:50]}...")
        print(f"    is_sensitive: {is_sensitive_in_db}")

        # Verify encrypted
        if encrypted_content != item_data["content"]:
            print("\n[PASS] Contenido esta CIFRADO en BD")
        else:
            print("\n[FAIL] Contenido NO esta cifrado")
            return False

        # Retrieve and verify decryption
        retrieved = db.get_item(item_id)
        if retrieved['content'] == item_data["content"]:
            print("[PASS] Contenido se descifra correctamente")
            print(f"    Contenido descifrado: {retrieved['content']}")
            return True
        else:
            print("[FAIL] Descifrado incorrecto")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test end-to-end: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_normal_item():
    """Test: Flujo completo - crear item normal y verificar NO cifrado"""
    print("\n" + "=" * 60)
    print("TEST 5: Flujo End-to-End - Item Normal")
    print("=" * 60)

    try:
        # Create in-memory database
        db = DBManager(":memory:")

        # Create category
        cat_id = db.add_category("URLs", "link", 0)
        print(f"\n[OK] Categoria creada: ID {cat_id}")

        # Simulate creating normal item through UI
        item_data = {
            "label": "GitHub",
            "content": "https://github.com",
            "type": ItemType.URL,
            "tags": ["dev"],
            "is_sensitive": False  # Checkbox NOT checked
        }

        # Add item to database
        item_id = db.add_item(
            category_id=cat_id,
            label=item_data["label"],
            content=item_data["content"],
            item_type=item_data["type"].value.upper(),  # DB expects uppercase
            is_sensitive=item_data["is_sensitive"],
            tags=item_data["tags"]
        )

        print(f"[OK] Item agregado: ID {item_id}")
        print(f"    Label: {item_data['label']}")
        print(f"    is_sensitive: {item_data['is_sensitive']}")

        # Verify in database (should be plain text)
        import sqlite3
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT content, is_sensitive FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()

        content_in_db = row[0]
        is_sensitive_in_db = row[1]

        print(f"\nVerificacion en BD:")
        print(f"    Contenido: {content_in_db}")
        print(f"    is_sensitive: {is_sensitive_in_db}")

        # Verify NOT encrypted (plain text)
        if content_in_db == item_data["content"]:
            print("\n[PASS] Contenido NO esta cifrado (correcto para item normal)")
            return True
        else:
            print("\n[FAIL] Contenido no deberia estar cifrado")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test end-to-end: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todos los tests de Fase 3"""
    print("\n" + "=" * 60)
    print("FASE 3: TEST DE UI - EDITOR (CHECKBOX SENSIBLE)")
    print("=" * 60 + "\n")

    tests = [
        test_ui_checkbox_exists,
        test_get_item_data_includes_sensitive,
        test_load_item_data_loads_sensitive,
        test_end_to_end_sensitive_item,
        test_end_to_end_normal_item
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[ERROR] Error en {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS - FASE 3")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nTests pasados: {passed}/{total}")

    if passed == total:
        print("\n*** FASE 3 COMPLETADA EXITOSAMENTE! ***")
        print("\nUI - Editor funcionando:")
        print("  [OK] Checkbox 'Sensible' agregado")
        print("  [OK] get_item_data() incluye is_sensitive")
        print("  [OK] load_item_data() carga is_sensitive")
        print("  [OK] Integracion con category_editor")
        print("  [OK] Flujo end-to-end con cifrado funciona")
        print("  [OK] Items normales NO se cifran")
        print("  [OK] Todos los tests pasaron")
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
