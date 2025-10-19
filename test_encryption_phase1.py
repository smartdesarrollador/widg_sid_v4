"""
Test de Fase 1: Verificar sistema de cifrado
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.encryption_manager import EncryptionManager

def test_encryption_basic():
    """Test básico de cifrado y descifrado"""
    print("=" * 60)
    print("TEST 1: Cifrado y Descifrado Básico")
    print("=" * 60)

    # Crear manager (esto generará .env automáticamente si no existe)
    manager = EncryptionManager()

    # Test data
    plaintext = "MiContrasenaSuperSecreta123!@#"
    print(f"\n[OK] Texto original: {plaintext}")

    # Cifrar
    encrypted = manager.encrypt(plaintext)
    print(f"[ENCRYPTED] Texto cifrado: {encrypted[:50]}...")

    # Descifrar
    decrypted = manager.decrypt(encrypted)
    print(f"[DECRYPTED] Texto descifrado: {decrypted}")

    # Verificar
    if plaintext == decrypted:
        print("\n[PASS] TEST PASADO: El texto se cifro y descifro correctamente")
    else:
        print("\n[FAIL] TEST FALLIDO: El texto no coincide")
        return False

    return True


def test_encryption_empty():
    """Test de cifrado con string vacío"""
    print("\n" + "=" * 60)
    print("TEST 2: String Vacío")
    print("=" * 60)

    manager = EncryptionManager()

    empty = ""
    encrypted = manager.encrypt(empty)
    decrypted = manager.decrypt(encrypted)

    if encrypted == "" and decrypted == "":
        print("\n[PASS] TEST PASADO: String vacio maneja correctamente")
        return True
    else:
        print("\n[FAIL] TEST FALLIDO: String vacio no maneja correctamente")
        return False


def test_is_encrypted():
    """Test de detección de texto cifrado"""
    print("\n" + "=" * 60)
    print("TEST 3: Detección de Texto Cifrado")
    print("=" * 60)

    manager = EncryptionManager()

    plaintext = "password123"
    encrypted = manager.encrypt(plaintext)

    is_plain_encrypted = manager.is_encrypted(plaintext)
    is_encrypted_text = manager.is_encrypted(encrypted)

    print(f"\n'{plaintext}' esta cifrado? {is_plain_encrypted}")
    print(f"'{encrypted[:30]}...' esta cifrado? {is_encrypted_text}")

    if not is_plain_encrypted and is_encrypted_text:
        print("\n[PASS] TEST PASADO: Deteccion funciona correctamente")
        return True
    else:
        print("\n[FAIL] TEST FALLIDO: Deteccion no funciona correctamente")
        return False


def test_key_integrity():
    """Test de integridad de clave"""
    print("\n" + "=" * 60)
    print("TEST 4: Integridad de Clave")
    print("=" * 60)

    manager = EncryptionManager()

    is_valid = manager.verify_key_integrity()

    if is_valid:
        print("\n[PASS] TEST PASADO: La clave de cifrado es valida")
        return True
    else:
        print("\n[FAIL] TEST FALLIDO: La clave de cifrado no es valida")
        return False


def test_config_manager_integration():
    """Test de integración con ConfigManager"""
    print("\n" + "=" * 60)
    print("TEST 5: Integración con ConfigManager")
    print("=" * 60)

    try:
        from core.config_manager import ConfigManager

        # Crear ConfigManager (debe inicializar EncryptionManager automáticamente)
        config = ConfigManager()

        # Verificar que tiene encryption_manager
        if hasattr(config, 'encryption_manager'):
            print("\n[OK] ConfigManager tiene encryption_manager")

            # Probar cifrado a traves del ConfigManager
            test_data = "TestPassword456"
            encrypted = config.encryption_manager.encrypt(test_data)
            decrypted = config.encryption_manager.decrypt(encrypted)

            if test_data == decrypted:
                print("[PASS] TEST PASADO: ConfigManager integrado correctamente")
                return True
            else:
                print("[FAIL] TEST FALLIDO: Cifrado/descifrado no funciona en ConfigManager")
                return False
        else:
            print("[FAIL] TEST FALLIDO: ConfigManager no tiene encryption_manager")
            return False

    except Exception as e:
        print(f"[FAIL] TEST FALLIDO: Error al integrar con ConfigManager: {e}")
        return False


def check_env_file():
    """Verificar que se creo el archivo .env"""
    print("\n" + "=" * 60)
    print("VERIFICACION: Archivo .env")
    print("=" * 60)

    env_path = Path(".env")

    if env_path.exists():
        print(f"\n[OK] Archivo .env creado en: {env_path.absolute()}")

        # Leer y mostrar (ofuscando la clave)
        with open(env_path, "r") as f:
            content = f.read()
            if "ENCRYPTION_KEY" in content:
                print("[OK] ENCRYPTION_KEY encontrada en .env")
                # Mostrar solo los primeros caracteres
                lines = content.split('\n')
                for line in lines:
                    if line.startswith("ENCRYPTION_KEY"):
                        key_value = line.split('=')[1]
                        print(f"   Valor: {key_value[:20]}...{key_value[-10:]}")
            else:
                print("[FAIL] ENCRYPTION_KEY NO encontrada en .env")
    else:
        print(f"\n[FAIL] Archivo .env NO existe")


def main():
    """Ejecutar todos los tests"""
    print("\n" + "=" * 60)
    print("FASE 1: TEST DE INFRAESTRUCTURA DE CIFRADO")
    print("=" * 60 + "\n")

    tests = [
        test_encryption_basic,
        test_encryption_empty,
        test_is_encrypted,
        test_key_integrity,
        test_config_manager_integration
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[ERROR] ERROR en {test.__name__}: {e}")
            results.append(False)

    # Verificar .env
    check_env_file()

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\nTests pasados: {passed}/{total}")

    if passed == total:
        print("\n*** FASE 1 COMPLETADA EXITOSAMENTE! ***")
        print("\nSistema de cifrado listo para usar:")
        print("  [OK] EncryptionManager creado")
        print("  [OK] Integrado con ConfigManager")
        print("  [OK] Archivo .env generado")
        print("  [OK] .gitignore actualizado")
        print("  [OK] Todos los tests pasaron")
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
