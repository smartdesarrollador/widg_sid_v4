"""
Test de Fase 2: FirstTimeWizard
Tests del wizard de configuración inicial
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from views.first_time_wizard import FirstTimeWizard
from core.auth_manager import AuthManager
from PyQt6.QtWidgets import QApplication


def test_wizard_has_required_widgets():
    """Test: Wizard tiene todos los widgets necesarios"""
    print("=" * 60)
    print("TEST 1: Wizard tiene todos los widgets necesarios")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        wizard = FirstTimeWizard()

        # Check widgets exist
        widgets_exist = [
            hasattr(wizard, 'password_input'),
            hasattr(wizard, 'confirm_input'),
            hasattr(wizard, 'create_btn'),
            hasattr(wizard, 'show_password_btn'),
            hasattr(wizard, 'strength_label'),
            hasattr(wizard, 'match_label')
        ]

        if all(widgets_exist):
            print("\n[PASS] Todos los widgets existen")
            print("  - password_input")
            print("  - confirm_input")
            print("  - create_btn")
            print("  - show_password_btn")
            print("  - strength_label")
            print("  - match_label")
            return True
        else:
            print("\n[FAIL] Faltan widgets")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validate_weak_password():
    """Test: Validación rechaza contraseñas débiles"""
    print("\n" + "=" * 60)
    print("TEST 2: Validación rechaza contraseñas débiles")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        wizard = FirstTimeWizard()

        # Test weak passwords
        weak_passwords = [
            "abc",  # Too short
            "abcdefgh",  # No uppercase, no number, no special
            "ABCDEFGH",  # No lowercase, no number, no special
            "Abcdefgh",  # No number, no special
            "Abcdef12",  # No special
        ]

        all_rejected = True
        for password in weak_passwords:
            validation = wizard.validate_password(password)
            if all(validation.values()):
                print(f"\n[FAIL] Password debil aceptada: {password}")
                all_rejected = False

        if all_rejected:
            print("\n[PASS] Todas las passwords debiles rechazadas")
            return True
        else:
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validate_strong_password():
    """Test: Validación acepta contraseñas fuertes"""
    print("\n" + "=" * 60)
    print("TEST 3: Validación acepta contraseñas fuertes")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        wizard = FirstTimeWizard()

        # Test strong passwords
        strong_passwords = [
            "MyPass123!",
            "Secure@2024",
            "Test#Password1",
            "Admin$Pass99"
        ]

        all_accepted = True
        for password in strong_passwords:
            validation = wizard.validate_password(password)
            if not all(validation.values()):
                print(f"\n[FAIL] Password fuerte rechazada: {password}")
                print(f"  Validacion: {validation}")
                all_accepted = False

        if all_accepted:
            print("\n[PASS] Todas las passwords fuertes aceptadas")
            return True
        else:
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_password_confirmation():
    """Test: Confirmación de contraseña funciona"""
    print("\n" + "=" * 60)
    print("TEST 4: Confirmación de contraseña funciona")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        wizard = FirstTimeWizard()

        # Set matching passwords
        wizard.password_input.setText("MyPass123!")
        wizard.confirm_input.setText("MyPass123!")

        # Trigger validation
        wizard.on_password_changed()
        wizard.on_confirm_changed()

        # Check if match label shows success
        match_text = wizard.match_label.text()
        if "coinciden" in match_text:
            print("\n[PASS] Passwords coincidentes detectadas")
        else:
            print(f"\n[FAIL] No se detectó coincidencia: {match_text}")
            return False

        # Check if create button is enabled
        if wizard.create_btn.isEnabled():
            print("[PASS] Boton crear habilitado con passwords validas")
        else:
            print("[FAIL] Boton crear NO habilitado")
            return False

        # Test non-matching passwords
        wizard.confirm_input.setText("WrongPass456!")
        wizard.on_confirm_changed()

        match_text = wizard.match_label.text()
        if "NO coinciden" in match_text:
            print("[PASS] Passwords diferentes detectadas")
        else:
            print(f"[FAIL] No se detectó diferencia: {match_text}")
            return False

        # Button should be disabled
        if not wizard.create_btn.isEnabled():
            print("[PASS] Boton crear deshabilitado con passwords diferentes")
            return True
        else:
            print("[FAIL] Boton crear sigue habilitado")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_password_saved_to_env():
    """Test: Contraseña se guarda en .env correctamente"""
    print("\n" + "=" * 60)
    print("TEST 5: Contraseña se guarda en .env correctamente")
    print("=" * 60)

    try:
        # Use test env
        test_env = ".env.test_wizard"
        Path(test_env).unlink(missing_ok=True)

        # Clear env vars
        import os
        for key in ['PASSWORD_HASH', 'PASSWORD_SALT']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)

        # Verify it's first time
        if not auth.is_first_time():
            print("\n[FAIL] No es primera vez cuando deberia serlo")
            Path(test_env).unlink(missing_ok=True)
            return False

        print("\n[INFO] Simulando creacion de password via wizard...")

        # Simulate wizard creating password
        password = "TestWizard123!"
        auth.set_password(password)

        # Verify password was saved
        if not auth.is_first_time():
            print("[PASS] Password guardada (is_first_time = False)")
        else:
            print("[FAIL] Password NO guardada")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Verify password works
        if auth.verify_password(password):
            print("[PASS] Password verificada correctamente")
        else:
            print("[FAIL] Password NO verifica")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Cleanup
        Path(test_env).unlink(missing_ok=True)
        return True

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_toggle_password_visibility():
    """Test: Toggle mostrar/ocultar contraseña funciona"""
    print("\n" + "=" * 60)
    print("TEST 6: Toggle mostrar/ocultar contraseña funciona")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        wizard = FirstTimeWizard()

        from PyQt6.QtWidgets import QLineEdit

        # Initial state: password hidden
        if wizard.password_input.echoMode() == QLineEdit.EchoMode.Password:
            print("\n[PASS] Password inicialmente oculta")
        else:
            print("\n[FAIL] Password NO oculta inicialmente")
            return False

        # Toggle to show
        wizard.toggle_password_visibility()

        if wizard.password_input.echoMode() == QLineEdit.EchoMode.Normal:
            print("[PASS] Password visible despues de toggle")
        else:
            print("[FAIL] Password NO visible despues de toggle")
            return False

        # Toggle back to hide
        wizard.toggle_password_visibility()

        if wizard.password_input.echoMode() == QLineEdit.EchoMode.Password:
            print("[PASS] Password oculta despues de segundo toggle")
            return True
        else:
            print("[FAIL] Password NO oculta despues de segundo toggle")
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todos los tests de Fase 2"""
    print("\n" + "=" * 60)
    print("FASE 2: TEST DE FIRSTTIMEWIZARD")
    print("=" * 60 + "\n")

    tests = [
        test_wizard_has_required_widgets,
        test_validate_weak_password,
        test_validate_strong_password,
        test_password_confirmation,
        test_password_saved_to_env,
        test_toggle_password_visibility
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
    print("RESUMEN DE TESTS - FASE 2")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nTests pasados: {passed}/{total}")

    if passed == total:
        print("\n*** FASE 2 COMPLETADA EXITOSAMENTE! ***")
        print("\nFirstTimeWizard funcionando:")
        print("  [OK] Todos los widgets presentes")
        print("  [OK] Validacion rechaza passwords debiles")
        print("  [OK] Validacion acepta passwords fuertes")
        print("  [OK] Confirmacion de password funciona")
        print("  [OK] Password se guarda en .env")
        print("  [OK] Toggle mostrar/ocultar funciona")
        print("  [OK] Todos los tests pasaron")
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
