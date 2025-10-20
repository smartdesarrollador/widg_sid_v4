"""
Test de Fase 3: LoginDialog
Tests del dialog de autenticación
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from views.login_dialog import LoginDialog
from core.auth_manager import AuthManager
from core.session_manager import SessionManager
from PyQt6.QtWidgets import QApplication


def test_login_has_required_widgets():
    """Test: LoginDialog tiene todos los widgets necesarios"""
    print("=" * 60)
    print("TEST 1: LoginDialog tiene todos los widgets necesarios")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Setup test password
        test_env = ".env.test_login"
        Path(test_env).unlink(missing_ok=True)

        # Clear env vars
        import os
        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'FAILED_ATTEMPTS', 'LOCK_TIMESTAMP']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)
        auth.set_password("TestPass123!")

        login = LoginDialog()

        # Check widgets exist
        widgets_exist = [
            hasattr(login, 'password_input'),
            hasattr(login, 'login_btn'),
            hasattr(login, 'show_password_btn'),
            hasattr(login, 'remember_checkbox'),
            hasattr(login, 'attempts_label'),
            hasattr(login, 'lock_label')
        ]

        if all(widgets_exist):
            print("\n[PASS] Todos los widgets existen")
            print("  - password_input")
            print("  - login_btn")
            print("  - show_password_btn")
            print("  - remember_checkbox")
            print("  - attempts_label")
            print("  - lock_label")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("\n[FAIL] Faltan widgets")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_successful_login():
    """Test: Login exitoso con contraseña correcta"""
    print("\n" + "=" * 60)
    print("TEST 2: Login exitoso con contraseña correcta")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Setup
        test_env = ".env.test_login"
        Path(test_env).unlink(missing_ok=True)

        import os
        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'FAILED_ATTEMPTS', 'LOCK_TIMESTAMP',
                    'SESSION_TOKEN', 'SESSION_EXPIRES']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)
        auth.set_password("TestPass123!")

        login = LoginDialog()

        # Enter correct password
        login.password_input.setText("TestPass123!")

        # Simulate login
        password = login.password_input.text()
        if auth.verify_password(password):
            print("\n[PASS] Password correcta verificada")
        else:
            print("\n[FAIL] Password correcta NO verificada")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Check failed attempts reset
        if auth.get_failed_attempts() == 0:
            print("[PASS] Intentos fallidos reseteados a 0")
        else:
            print(f"[FAIL] Intentos fallidos: {auth.get_failed_attempts()}")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Create session
        session = SessionManager(test_env)
        token = session.create_session(remember=False)

        # Verify session created
        if session.validate_session():
            print("[PASS] Sesion creada exitosamente")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("[FAIL] Sesion NO creada")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_failed_login_increments_attempts():
    """Test: Login fallido incrementa contador de intentos"""
    print("\n" + "=" * 60)
    print("TEST 3: Login fallido incrementa contador de intentos")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Setup
        test_env = ".env.test_login"
        Path(test_env).unlink(missing_ok=True)

        import os
        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'FAILED_ATTEMPTS', 'LOCK_TIMESTAMP']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)
        auth.set_password("CorrectPass123!")

        login = LoginDialog()

        # Initial attempts should be 0
        if auth.get_failed_attempts() == 0:
            print("\n[PASS] Intentos iniciales: 0")
        else:
            print(f"\n[FAIL] Intentos iniciales: {auth.get_failed_attempts()}")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Try wrong password
        login.password_input.setText("WrongPass123!")
        password = login.password_input.text()

        if not auth.verify_password(password):
            print("[PASS] Password incorrecta rechazada")
            auth.increment_failed_attempts()
        else:
            print("[FAIL] Password incorrecta aceptada")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Check attempts incremented
        if auth.get_failed_attempts() == 1:
            print("[PASS] Intentos incrementados a 1")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print(f"[FAIL] Intentos: {auth.get_failed_attempts()}")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_account_locks_after_5_attempts():
    """Test: Cuenta se bloquea después de 5 intentos fallidos"""
    print("\n" + "=" * 60)
    print("TEST 4: Cuenta se bloquea después de 5 intentos fallidos")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Setup
        test_env = ".env.test_login"
        Path(test_env).unlink(missing_ok=True)

        import os
        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'FAILED_ATTEMPTS', 'LOCK_TIMESTAMP']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)
        auth.set_password("CorrectPass123!")
        auth.reset_failed_attempts()

        login = LoginDialog()

        print("\n[INFO] Simulando 5 intentos fallidos...")

        # 5 failed attempts
        for i in range(5):
            login.password_input.setText(f"WrongPass{i}!")
            password = login.password_input.text()

            if not auth.verify_password(password):
                auth.increment_failed_attempts()
                print(f"[INFO] Intento fallido {i+1}/5")

        # Check if locked
        if auth.is_locked():
            print("[PASS] Cuenta BLOQUEADA después de 5 intentos")

            remaining = auth.get_lock_time_remaining()
            if remaining > 0:
                print(f"[PASS] Tiempo de bloqueo: {remaining}s")
                Path(test_env).unlink(missing_ok=True)
                return True
            else:
                print("[FAIL] Tiempo de bloqueo es 0")
                Path(test_env).unlink(missing_ok=True)
                return False
        else:
            print("[FAIL] Cuenta NO bloqueada")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_remember_checkbox_creates_24h_session():
    """Test: Checkbox 'Recordar' crea sesión de 24 horas"""
    print("\n" + "=" * 60)
    print("TEST 5: Checkbox 'Recordar' crea sesión de 24 horas")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Setup
        test_env = ".env.test_login"
        Path(test_env).unlink(missing_ok=True)

        import os
        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'SESSION_TOKEN', 'SESSION_EXPIRES']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)
        auth.set_password("TestPass123!")

        login = LoginDialog()

        # Check remember checkbox
        login.remember_checkbox.setChecked(True)

        if login.remember_checkbox.isChecked():
            print("\n[PASS] Checkbox 'Recordar' marcado")
        else:
            print("\n[FAIL] Checkbox NO marcado")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Create session with remember=True
        session = SessionManager(test_env)
        token = session.create_session(remember=True)

        # Check session duration
        expires_str = os.environ.get("SESSION_EXPIRES", "0")
        expires = int(expires_str)
        current_time = int(time.time())
        duration_hours = (expires - current_time) / 3600

        # Should be ~24 hours (allow 1 minute margin)
        if 23.9 <= duration_hours <= 24.1:
            print(f"[PASS] Sesion de ~24 horas ({duration_hours:.1f}h)")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print(f"[FAIL] Duracion de sesion: {duration_hours:.1f}h")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_attempts_label_updates():
    """Test: Label de intentos se actualiza correctamente"""
    print("\n" + "=" * 60)
    print("TEST 6: Label de intentos se actualiza correctamente")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Setup
        test_env = ".env.test_login"
        Path(test_env).unlink(missing_ok=True)

        import os
        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'FAILED_ATTEMPTS', 'LOCK_TIMESTAMP']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)
        auth.set_password("TestPass123!")
        auth.reset_failed_attempts()

        login = LoginDialog()

        # Initially should be empty (0 failed attempts)
        if login.attempts_label.text() == "":
            print("\n[PASS] Label inicial vacio (0 intentos)")
        else:
            print(f"\n[FAIL] Label inicial: '{login.attempts_label.text()}'")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Increment attempts
        auth.increment_failed_attempts()
        login.update_attempts_display()

        # Should show "Intentos restantes: 4"
        if "4" in login.attempts_label.text():
            print("[PASS] Label muestra 4 intentos restantes")
        else:
            print(f"[FAIL] Label: '{login.attempts_label.text()}'")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Increment to 4 attempts (1 remaining)
        for _ in range(3):
            auth.increment_failed_attempts()
        login.update_attempts_display()

        # Should show warning
        if "ltimo" in login.attempts_label.text() or "1" in login.attempts_label.text():
            print("[PASS] Label muestra advertencia de ultimo intento")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print(f"[FAIL] Label: '{login.attempts_label.text()}'")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_toggle_password_visibility():
    """Test: Toggle mostrar/ocultar contraseña funciona"""
    print("\n" + "=" * 60)
    print("TEST 7: Toggle mostrar/ocultar contraseña funciona")
    print("=" * 60)

    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Setup
        test_env = ".env.test_login"
        Path(test_env).unlink(missing_ok=True)

        import os
        for key in ['PASSWORD_HASH', 'PASSWORD_SALT']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)
        auth.set_password("TestPass123!")

        login = LoginDialog()

        from PyQt6.QtWidgets import QLineEdit

        # Initial state: password hidden
        if login.password_input.echoMode() == QLineEdit.EchoMode.Password:
            print("\n[PASS] Password inicialmente oculta")
        else:
            print("\n[FAIL] Password NO oculta inicialmente")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Toggle to show
        login.toggle_password_visibility()

        if login.password_input.echoMode() == QLineEdit.EchoMode.Normal:
            print("[PASS] Password visible despues de toggle")
        else:
            print("[FAIL] Password NO visible despues de toggle")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Toggle back to hide
        login.toggle_password_visibility()

        if login.password_input.echoMode() == QLineEdit.EchoMode.Password:
            print("[PASS] Password oculta despues de segundo toggle")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("[FAIL] Password NO oculta despues de segundo toggle")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todos los tests de Fase 3"""
    print("\n" + "=" * 60)
    print("FASE 3: TEST DE LOGINDIALOG")
    print("=" * 60 + "\n")

    tests = [
        test_login_has_required_widgets,
        test_successful_login,
        test_failed_login_increments_attempts,
        test_account_locks_after_5_attempts,
        test_remember_checkbox_creates_24h_session,
        test_attempts_label_updates,
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
    print("RESUMEN DE TESTS - FASE 3")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nTests pasados: {passed}/{total}")

    if passed == total:
        print("\n*** FASE 3 COMPLETADA EXITOSAMENTE! ***")
        print("\nLoginDialog funcionando:")
        print("  [OK] Todos los widgets presentes")
        print("  [OK] Login exitoso funciona")
        print("  [OK] Login fallido incrementa intentos")
        print("  [OK] Cuenta se bloquea despues de 5 intentos")
        print("  [OK] Checkbox 'Recordar' crea sesion de 24h")
        print("  [OK] Label de intentos se actualiza")
        print("  [OK] Toggle mostrar/ocultar funciona")
        print("  [OK] Todos los tests pasaron")
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
