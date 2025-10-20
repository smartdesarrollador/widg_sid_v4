"""
Test de Fase 4: Integración con main.py
Tests de integración del sistema de autenticación
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.auth_manager import AuthManager
from core.session_manager import SessionManager


def test_first_time_detection():
    """Test: is_first_time() detecta correctamente primera ejecución"""
    print("=" * 60)
    print("TEST 1: is_first_time() detecta primera ejecución")
    print("=" * 60)

    try:
        # Setup - clean environment
        test_env = ".env.test_integration"
        Path(test_env).unlink(missing_ok=True)

        # Clear env vars
        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'FAILED_ATTEMPTS', 'LOCK_TIMESTAMP']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)

        # Should be first time
        if auth.is_first_time():
            print("\n[PASS] is_first_time() = True (sin password)")
        else:
            print("\n[FAIL] is_first_time() = False cuando deberia ser True")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Set password
        auth.set_password("FirstTime123!")

        # Should NOT be first time now
        if not auth.is_first_time():
            print("[PASS] is_first_time() = False (con password)")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("[FAIL] is_first_time() = True cuando deberia ser False")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_validation_flow():
    """Test: Flujo de validación de sesión funciona"""
    print("\n" + "=" * 60)
    print("TEST 2: Flujo de validación de sesión")
    print("=" * 60)

    try:
        # Setup
        test_env = ".env.test_integration"
        Path(test_env).unlink(missing_ok=True)

        for key in ['SESSION_TOKEN', 'SESSION_EXPIRES']:
            os.environ.pop(key, None)

        session = SessionManager(test_env)

        # No session initially
        if not session.validate_session():
            print("\n[PASS] Sin sesion inicialmente")
        else:
            print("\n[FAIL] Sesion valida cuando no deberia")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Create session
        token = session.create_session(remember=False)
        print(f"[INFO] Sesion creada (token: {token[:20]}...)")

        # Session should be valid now
        if session.validate_session():
            print("[PASS] Sesion valida despues de crear")
        else:
            print("[FAIL] Sesion NO valida despues de crear")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Invalidate session
        session.invalidate_session()
        print("[INFO] Sesion invalidada")

        # Session should be invalid now
        if not session.validate_session():
            print("[PASS] Sesion invalida despues de cerrar")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("[FAIL] Sesion sigue valida despues de cerrar")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_authentication_flow_first_time():
    """Test: Flujo de autenticación - primera vez"""
    print("\n" + "=" * 60)
    print("TEST 3: Flujo de autenticación - primera vez")
    print("=" * 60)

    try:
        # Setup - clean environment
        test_env = ".env.test_integration"
        Path(test_env).unlink(missing_ok=True)

        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'SESSION_TOKEN', 'SESSION_EXPIRES']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)
        session = SessionManager(test_env)

        print("\n[INFO] Simulando flujo de primera vez...")

        # Step 1: Check if first time
        if auth.is_first_time():
            print("[PASS] Es primera vez")
        else:
            print("[FAIL] NO es primera vez")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Step 2: User creates password (simulated)
        password = "NewPassword123!"
        auth.set_password(password)
        print(f"[INFO] Password creada: {password}")

        # Step 3: Verify password works
        if auth.verify_password(password):
            print("[PASS] Password verificada correctamente")
        else:
            print("[FAIL] Password NO verificada")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Step 4: NOT first time anymore
        if not auth.is_first_time():
            print("[PASS] Ya NO es primera vez")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("[FAIL] Sigue siendo primera vez")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_authentication_flow_with_session():
    """Test: Flujo de autenticación - con sesión válida"""
    print("\n" + "=" * 60)
    print("TEST 4: Flujo de autenticación - con sesión válida")
    print("=" * 60)

    try:
        # Setup
        test_env = ".env.test_integration"
        Path(test_env).unlink(missing_ok=True)

        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'SESSION_TOKEN', 'SESSION_EXPIRES']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)
        session = SessionManager(test_env)

        print("\n[INFO] Configurando password y sesion...")

        # Setup password
        auth.set_password("TestPass123!")

        # Create session
        session.create_session(remember=True)  # 24 hours

        # Simulate app startup - check session
        if session.validate_session():
            print("[PASS] Sesion valida - skip login")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("[FAIL] Sesion NO valida")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_authentication_flow_login():
    """Test: Flujo de autenticación - login normal"""
    print("\n" + "=" * 60)
    print("TEST 5: Flujo de autenticación - login normal")
    print("=" * 60)

    try:
        # Setup
        test_env = ".env.test_integration"
        Path(test_env).unlink(missing_ok=True)

        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'SESSION_TOKEN', 'SESSION_EXPIRES', 'FAILED_ATTEMPTS']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)
        session = SessionManager(test_env)

        print("\n[INFO] Configurando password...")

        # Setup password
        correct_password = "MyPass123!"
        auth.set_password(correct_password)

        # Simulate app startup - no session
        if not session.validate_session():
            print("[PASS] Sin sesion - mostrar login")
        else:
            print("[FAIL] Sesion valida cuando no deberia")
            Path(test_env).unlink(missing_ok=True)
            return False

        # User enters wrong password
        if not auth.verify_password("WrongPass123!"):
            print("[PASS] Password incorrecta rechazada")
            auth.increment_failed_attempts()
        else:
            print("[FAIL] Password incorrecta aceptada")
            Path(test_env).unlink(missing_ok=True)
            return False

        # User enters correct password
        if auth.verify_password(correct_password):
            print("[PASS] Password correcta aceptada")
            auth.reset_failed_attempts()
        else:
            print("[FAIL] Password correcta rechazada")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Create session after successful login
        session.create_session(remember=False)

        # Verify session created
        if session.validate_session():
            print("[PASS] Sesion creada despues de login")
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


def test_logout_invalidates_session():
    """Test: Cerrar sesión invalida el token"""
    print("\n" + "=" * 60)
    print("TEST 6: Cerrar sesión invalida el token")
    print("=" * 60)

    try:
        # Setup
        test_env = ".env.test_integration"
        Path(test_env).unlink(missing_ok=True)

        for key in ['SESSION_TOKEN', 'SESSION_EXPIRES']:
            os.environ.pop(key, None)

        session = SessionManager(test_env)

        print("\n[INFO] Creando sesion...")

        # Create session
        session.create_session(remember=True)

        # Verify session valid
        if session.validate_session():
            print("[PASS] Sesion valida inicialmente")
        else:
            print("[FAIL] Sesion NO valida")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Logout (invalidate session)
        print("[INFO] Cerrando sesion...")
        session.invalidate_session()

        # Verify session invalid
        if not session.validate_session():
            print("[PASS] Sesion invalidada correctamente")

            # Verify token and expires cleared
            token = os.environ.get("SESSION_TOKEN", "")
            expires = os.environ.get("SESSION_EXPIRES", "0")

            if token == "" and expires == "0":
                print("[PASS] Token y expires limpiados")
                Path(test_env).unlink(missing_ok=True)
                return True
            else:
                print(f"[FAIL] Token/expires NO limpiados (token={token}, expires={expires})")
                Path(test_env).unlink(missing_ok=True)
                return False
        else:
            print("[FAIL] Sesion sigue valida")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todos los tests de Fase 4"""
    print("\n" + "=" * 60)
    print("FASE 4: TEST DE INTEGRACIÓN")
    print("=" * 60 + "\n")

    tests = [
        test_first_time_detection,
        test_session_validation_flow,
        test_authentication_flow_first_time,
        test_authentication_flow_with_session,
        test_authentication_flow_login,
        test_logout_invalidates_session
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
    print("RESUMEN DE TESTS - FASE 4")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nTests pasados: {passed}/{total}")

    if passed == total:
        print("\n*** FASE 4 COMPLETADA EXITOSAMENTE! ***")
        print("\nIntegracion funcionando:")
        print("  [OK] Deteccion de primera vez")
        print("  [OK] Validacion de sesion")
        print("  [OK] Flujo primera vez")
        print("  [OK] Flujo con sesion valida")
        print("  [OK] Flujo login normal")
        print("  [OK] Cerrar sesion funciona")
        print("  [OK] Todos los tests pasaron")
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
