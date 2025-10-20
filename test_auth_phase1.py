"""
Test de Fase 1: AuthManager y SessionManager
Tests del backend de autenticación
"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.auth_manager import AuthManager
from core.session_manager import SessionManager


def test_hash_password():
    """Test: Hash de password genera string válido"""
    print("=" * 60)
    print("TEST 1: Hash de password genera string válido")
    print("=" * 60)

    try:
        # Create test env file
        test_env = ".env.test_auth"
        auth = AuthManager(test_env)

        # Hash a password
        password = "TestPassword123!"
        password_hash, salt = auth.hash_password(password)

        print(f"\n[INFO] Password: {password}")
        print(f"[INFO] Hash length: {len(password_hash)}")
        print(f"[INFO] Salt length: {len(salt)}")

        # Verify hash is 64 characters (SHA256 hex)
        if len(password_hash) == 64:
            print("[PASS] Hash tiene longitud correcta (64 caracteres)")
        else:
            print(f"[FAIL] Hash tiene longitud incorrecta: {len(password_hash)}")
            return False

        # Verify salt is 64 characters
        if len(salt) == 64:
            print("[PASS] Salt tiene longitud correcta (64 caracteres)")
        else:
            print(f"[FAIL] Salt tiene longitud incorrecta: {len(salt)}")
            return False

        # Cleanup
        Path(test_env).unlink(missing_ok=True)
        return True

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_verify_password_correct():
    """Test: Verificación de password correcto funciona"""
    print("\n" + "=" * 60)
    print("TEST 2: Verificación de password correcto funciona")
    print("=" * 60)

    try:
        test_env = ".env.test_auth"
        auth = AuthManager(test_env)

        # Set a password
        password = "MySecurePass123!"
        auth.set_password(password)
        print(f"\n[INFO] Password configurada: {password}")

        # Verify correct password
        if auth.verify_password(password):
            print("[PASS] Password correcto verificado exitosamente")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("[FAIL] Verificación de password correcto falló")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_verify_password_incorrect():
    """Test: Verificación de password incorrecto falla"""
    print("\n" + "=" * 60)
    print("TEST 3: Verificación de password incorrecto falla")
    print("=" * 60)

    try:
        test_env = ".env.test_auth"
        auth = AuthManager(test_env)

        # Set a password
        correct_password = "MySecurePass123!"
        wrong_password = "WrongPassword999!"
        auth.set_password(correct_password)
        print(f"\n[INFO] Password correcta: {correct_password}")
        print(f"[INFO] Password incorrecta: {wrong_password}")

        # Verify wrong password fails
        if not auth.verify_password(wrong_password):
            print("[PASS] Password incorrecta rechazada correctamente")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("[FAIL] Password incorrecta fue aceptada (ERROR)")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_is_first_time():
    """Test: is_first_time() detecta primera instalación"""
    print("\n" + "=" * 60)
    print("TEST 4: is_first_time() detecta primera instalación")
    print("=" * 60)

    try:
        test_env = ".env.test_auth_fresh"

        # Remove test file if exists
        Path(test_env).unlink(missing_ok=True)

        # Clear environment variables from previous tests
        import os
        for key in ['PASSWORD_HASH', 'PASSWORD_SALT', 'FAILED_ATTEMPTS', 'LOCK_TIMESTAMP']:
            os.environ.pop(key, None)

        auth = AuthManager(test_env)

        # Should be first time (no password set)
        if auth.is_first_time():
            print("\n[PASS] is_first_time() retorna True (sin password)")
        else:
            print("\n[FAIL] is_first_time() retorna False cuando debería ser True")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Set a password
        auth.set_password("TestPassword123!")

        # Should NOT be first time now
        if not auth.is_first_time():
            print("[PASS] is_first_time() retorna False (con password)")
        else:
            print("[FAIL] is_first_time() retorna True cuando debería ser False")
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


def test_failed_attempts():
    """Test: Contador de intentos fallidos incrementa"""
    print("\n" + "=" * 60)
    print("TEST 5: Contador de intentos fallidos incrementa")
    print("=" * 60)

    try:
        test_env = ".env.test_auth"
        auth = AuthManager(test_env)

        # Reset attempts
        auth.reset_failed_attempts()
        print("\n[INFO] Intentos reseteados")

        # Should be 0
        if auth.get_failed_attempts() == 0:
            print("[PASS] Intentos iniciales: 0")
        else:
            print(f"[FAIL] Intentos iniciales: {auth.get_failed_attempts()}")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Increment
        auth.increment_failed_attempts()
        print("[INFO] Incrementado +1")

        if auth.get_failed_attempts() == 1:
            print("[PASS] Intentos después de incrementar: 1")
        else:
            print(f"[FAIL] Intentos: {auth.get_failed_attempts()}")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Increment again
        auth.increment_failed_attempts()
        print("[INFO] Incrementado +1")

        if auth.get_failed_attempts() == 2:
            print("[PASS] Intentos después de incrementar: 2")
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


def test_account_lock():
    """Test: Cuenta se bloquea después de 5 intentos"""
    print("\n" + "=" * 60)
    print("TEST 6: Cuenta se bloquea después de 5 intentos")
    print("=" * 60)

    try:
        test_env = ".env.test_auth"
        auth = AuthManager(test_env)

        # Reset
        auth.reset_failed_attempts()
        print("\n[INFO] Reseteando intentos...")

        # Not locked initially
        if not auth.is_locked():
            print("[PASS] Cuenta NO bloqueada inicialmente")
        else:
            print("[FAIL] Cuenta bloqueada cuando no debería")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Increment 5 times
        for i in range(5):
            auth.increment_failed_attempts()
            print(f"[INFO] Intento fallido {i+1}/5")

        # Should be locked now
        if auth.is_locked():
            print("[PASS] Cuenta BLOQUEADA después de 5 intentos")

            # Check lock time
            remaining = auth.get_lock_time_remaining()
            print(f"[INFO] Tiempo restante de bloqueo: {remaining}s")

            if remaining > 0:
                print("[PASS] Tiempo de bloqueo > 0")
                Path(test_env).unlink(missing_ok=True)
                return True
            else:
                print("[FAIL] Tiempo de bloqueo es 0")
                Path(test_env).unlink(missing_ok=True)
                return False
        else:
            print("[FAIL] Cuenta NO bloqueada después de 5 intentos")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_creation():
    """Test: SessionManager crea sesión válida"""
    print("\n" + "=" * 60)
    print("TEST 7: SessionManager crea sesión válida")
    print("=" * 60)

    try:
        test_env = ".env.test_auth"
        session = SessionManager(test_env)

        # Create session
        token = session.create_session(remember=False)
        print(f"\n[INFO] Token creado (longitud: {len(token)})")

        # Verify token length
        if len(token) > 40:
            print("[PASS] Token tiene longitud segura (>40 caracteres)")
        else:
            print(f"[FAIL] Token muy corto: {len(token)}")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Validate session
        if session.validate_session():
            print("[PASS] Sesión válida inmediatamente después de crear")
        else:
            print("[FAIL] Sesión inválida después de crear")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Get token
        retrieved_token = session.get_session_token()
        if retrieved_token == token:
            print("[PASS] Token recuperado coincide con el creado")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("[FAIL] Token recuperado NO coincide")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_invalidation():
    """Test: SessionManager invalida sesión correctamente"""
    print("\n" + "=" * 60)
    print("TEST 8: SessionManager invalida sesión correctamente")
    print("=" * 60)

    try:
        test_env = ".env.test_auth"
        session = SessionManager(test_env)

        # Create session
        session.create_session(remember=False)
        print("\n[INFO] Sesión creada")

        # Verify it's valid
        if session.validate_session():
            print("[PASS] Sesión válida después de crear")
        else:
            print("[FAIL] Sesión inválida después de crear")
            Path(test_env).unlink(missing_ok=True)
            return False

        # Invalidate
        session.invalidate_session()
        print("[INFO] Sesión invalidada")

        # Verify it's invalid now
        if not session.validate_session():
            print("[PASS] Sesión inválida después de invalidar")
            Path(test_env).unlink(missing_ok=True)
            return True
        else:
            print("[FAIL] Sesión aún válida después de invalidar")
            Path(test_env).unlink(missing_ok=True)
            return False

    except Exception as e:
        print(f"\n[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todos los tests de Fase 1"""
    print("\n" + "=" * 60)
    print("FASE 1: TEST DE AUTHMANGER Y SESSIONMANAGER")
    print("=" * 60 + "\n")

    tests = [
        test_hash_password,
        test_verify_password_correct,
        test_verify_password_incorrect,
        test_is_first_time,
        test_failed_attempts,
        test_account_lock,
        test_session_creation,
        test_session_invalidation
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
    print("RESUMEN DE TESTS - FASE 1")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nTests pasados: {passed}/{total}")

    if passed == total:
        print("\n*** FASE 1 COMPLETADA EXITOSAMENTE! ***")
        print("\nAuthManager funcionando:")
        print("  [OK] Hash de passwords (SHA256 + salt)")
        print("  [OK] Verificacion de passwords")
        print("  [OK] Deteccion primera vez")
        print("  [OK] Contador de intentos fallidos")
        print("  [OK] Bloqueo de cuenta")
        print("\nSessionManager funcionando:")
        print("  [OK] Creacion de sesiones")
        print("  [OK] Validacion de sesiones")
        print("  [OK] Invalidacion de sesiones")
        print("  [OK] Todos los tests pasaron")
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
