"""
Test de Fase 5: Clipboard Seguro (Auto-limpieza)
Tests del sistema de auto-limpieza de clipboard para items sensibles
"""
import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.item import Item, ItemType


def test_clipboard_timer_starts_for_sensitive():
    """Test: Timer de clipboard inicia para items sensibles"""
    print("=" * 60)
    print("TEST 1: Timer de clipboard inicia para items sensibles")
    print("=" * 60)

    try:
        from views.widgets.item_widget import ItemButton
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create sensitive item
        sensitive_item = Item(
            item_id="test1",
            label="API Key",
            content="sk_live_1234567890",
            item_type=ItemType.TEXT,
            is_sensitive=True
        )

        # Create button widget
        button = ItemButton(sensitive_item)

        # Simulate click (should start timer)
        button.on_clicked()

        # Check if timer was created
        if button.clipboard_clear_timer is not None:
            print("\n[PASS] clipboard_clear_timer fue creado")

            if isinstance(button.clipboard_clear_timer, QTimer):
                print("[PASS] clipboard_clear_timer es un QTimer")

                if button.clipboard_clear_timer.isActive():
                    print("[PASS] Timer esta activo")

                    # Check interval is 30 seconds
                    if button.clipboard_clear_timer.interval() == 30000:
                        print("[PASS] Intervalo es 30 segundos (30000ms)")
                        return True
                    else:
                        print(f"[FAIL] Intervalo incorrecto: {button.clipboard_clear_timer.interval()}ms")
                        return False
                else:
                    print("[FAIL] Timer NO esta activo")
                    return False
            else:
                print("[FAIL] clipboard_clear_timer NO es QTimer")
                return False
        else:
            print("\n[FAIL] clipboard_clear_timer NO fue creado")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_clipboard_timer_not_starts_for_normal():
    """Test: Timer de clipboard NO inicia para items normales"""
    print("\n" + "=" * 60)
    print("TEST 2: Timer NO inicia para items normales")
    print("=" * 60)

    try:
        from views.widgets.item_widget import ItemButton
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create normal item
        normal_item = Item(
            item_id="test2",
            label="GitHub URL",
            content="https://github.com",
            item_type=ItemType.URL,
            is_sensitive=False
        )

        # Create button widget
        button = ItemButton(normal_item)

        # Simulate click
        button.on_clicked()

        # Check if timer was NOT created (or not started)
        if button.clipboard_clear_timer is None:
            print("\n[PASS] Timer NO fue creado para item normal (correcto)")
            return True
        elif not button.clipboard_clear_timer.isActive():
            print("\n[PASS] Timer existe pero NO esta activo (correcto)")
            return True
        else:
            print("\n[FAIL] Timer esta activo para item normal (incorrecto)")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_clear_clipboard_method():
    """Test: Metodo clear_clipboard() limpia el clipboard"""
    print("\n" + "=" * 60)
    print("TEST 3: clear_clipboard() limpia el clipboard")
    print("=" * 60)

    try:
        from views.widgets.item_widget import ItemButton
        from PyQt6.QtWidgets import QApplication
        import pyperclip

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create sensitive item
        sensitive_item = Item(
            item_id="test3",
            label="Password",
            content="MySecretPassword123",
            item_type=ItemType.TEXT,
            is_sensitive=True
        )

        # Create button widget
        button = ItemButton(sensitive_item)

        # Set clipboard content
        test_content = "TestClipboardContent123"
        pyperclip.copy(test_content)
        print(f"\n[INFO] Contenido copiado: {test_content}")

        # Verify clipboard has content
        clipboard_before = pyperclip.paste()
        if clipboard_before == test_content:
            print("[PASS] Clipboard contiene el contenido de prueba")
        else:
            print(f"[FAIL] Clipboard no tiene el contenido esperado: {clipboard_before}")
            return False

        # Call clear_clipboard
        button.clear_clipboard()
        print("[INFO] Ejecutado clear_clipboard()")

        # Verify clipboard is empty
        clipboard_after = pyperclip.paste()
        if clipboard_after == "":
            print("[PASS] Clipboard fue limpiado correctamente")
            return True
        else:
            print(f"[FAIL] Clipboard NO fue limpiado: {clipboard_after}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sensitive_feedback_visual():
    """Test: Items sensibles muestran feedback visual diferente"""
    print("\n" + "=" * 60)
    print("TEST 4: Feedback visual diferente para items sensibles")
    print("=" * 60)

    try:
        from views.widgets.item_widget import ItemButton
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create sensitive item
        sensitive_item = Item(
            item_id="test4",
            label="Credit Card",
            content="4111-1111-1111-1111",
            item_type=ItemType.TEXT,
            is_sensitive=True
        )

        # Create button widget
        button = ItemButton(sensitive_item)

        # Trigger copied feedback
        button.show_copied_feedback()

        # Check stylesheet (should have orange color for sensitive items)
        stylesheet = button.styleSheet()
        print("\n[INFO] Verificando stylesheet del feedback...")

        # Should have orange background (#cc7a00) for sensitive items
        if "#cc7a00" in stylesheet:
            print("[PASS] Tiene color naranja (#cc7a00) para item sensible")
            return True
        else:
            print("[FAIL] NO tiene el color naranja esperado")
            print(f"[DEBUG] Stylesheet: {stylesheet[:200]}...")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_normal_item_feedback_visual():
    """Test: Items normales muestran feedback azul"""
    print("\n" + "=" * 60)
    print("TEST 5: Items normales muestran feedback azul")
    print("=" * 60)

    try:
        from views.widgets.item_widget import ItemButton
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create normal item
        normal_item = Item(
            item_id="test5",
            label="Normal Text",
            content="Public information",
            item_type=ItemType.TEXT,
            is_sensitive=False
        )

        # Create button widget
        button = ItemButton(normal_item)

        # Trigger copied feedback
        button.show_copied_feedback()

        # Check stylesheet (should have blue color for normal items)
        stylesheet = button.styleSheet()
        print("\n[INFO] Verificando stylesheet del feedback...")

        # Should have blue background (#007acc) for normal items
        if "#007acc" in stylesheet:
            print("[PASS] Tiene color azul (#007acc) para item normal")
            return True
        else:
            print("[FAIL] NO tiene el color azul esperado")
            print(f"[DEBUG] Stylesheet: {stylesheet[:200]}...")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_clicks_reset_timer():
    """Test: Multiples clicks reinician el timer (solo el ultimo cuenta)"""
    print("\n" + "=" * 60)
    print("TEST 6: Multiples clicks reinician el timer")
    print("=" * 60)

    try:
        from views.widgets.item_widget import ItemButton
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Create sensitive item
        sensitive_item = Item(
            item_id="test6",
            label="Secret Key",
            content="secret_xyz_789",
            item_type=ItemType.TEXT,
            is_sensitive=True
        )

        # Create button widget
        button = ItemButton(sensitive_item)

        # First click
        button.on_clicked()
        first_timer = button.clipboard_clear_timer
        print("\n[INFO] Primer click realizado")

        if first_timer is None or not first_timer.isActive():
            print("[FAIL] Primer timer no se inicio")
            return False

        # Second click (should restart timer)
        button.on_clicked()
        second_timer = button.clipboard_clear_timer
        print("[INFO] Segundo click realizado")

        if second_timer is None or not second_timer.isActive():
            print("[FAIL] Segundo timer no se inicio")
            return False

        # Verify timer is still active and interval is correct
        if second_timer.isActive() and second_timer.interval() == 30000:
            print("[PASS] Timer fue reiniciado correctamente")
            print("[PASS] Intervalo sigue siendo 30 segundos")
            return True
        else:
            print("[FAIL] Timer no se reinicio correctamente")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todos los tests de Fase 5"""
    print("\n" + "=" * 60)
    print("FASE 5: TEST DE CLIPBOARD SEGURO (AUTO-LIMPIEZA)")
    print("=" * 60 + "\n")

    tests = [
        test_clipboard_timer_starts_for_sensitive,
        test_clipboard_timer_not_starts_for_normal,
        test_clear_clipboard_method,
        test_sensitive_feedback_visual,
        test_normal_item_feedback_visual,
        test_multiple_clicks_reset_timer
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
    print("RESUMEN DE TESTS - FASE 5")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nTests pasados: {passed}/{total}")

    if passed == total:
        print("\n*** FASE 5 COMPLETADA EXITOSAMENTE! ***")
        print("\nClipboard Seguro funcionando:")
        print("  [OK] Timer de 30s inicia para items sensibles")
        print("  [OK] Timer NO inicia para items normales")
        print("  [OK] clear_clipboard() limpia el clipboard")
        print("  [OK] Feedback visual diferenciado (naranja)")
        print("  [OK] Items normales con feedback azul")
        print("  [OK] Multiples clicks reinician timer")
        print("  [OK] Todos los tests pasaron")
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
