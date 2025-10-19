"""
Test de Fase 2: Cifrado automatico en Base de Datos
"""
import sys
import os
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.db_manager import DBManager
from core.encryption_manager import EncryptionManager


def test_add_sensitive_item():
    """Test: Agregar item sensible cifra el contenido automaticamente"""
    print("=" * 60)
    print("TEST 1: Agregar Item Sensible (Cifrado Automatico)")
    print("=" * 60)

    # Crear DB en memoria para tests
    db = DBManager(":memory:")

    # Crear categoria de prueba
    cat_id = db.add_category("Passwords", "lock", 0)
    print(f"\n[OK] Categoria creada: ID {cat_id}")

    # Agregar item sensible
    password = "MiPasswordSuperSecreto123!@#"
    item_id = db.add_item(
        category_id=cat_id,
        label="Gmail Password",
        content=password,
        item_type='TEXT',
        is_sensitive=True
    )
    print(f"[OK] Item sensible agregado: ID {item_id}")
    print(f"    Password original: {password}")

    # Verificar en BD que esta cifrado
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT content, is_sensitive FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()

    encrypted_content = row[0]
    is_sensitive = row[1]

    print(f"    Contenido en BD: {encrypted_content[:50]}...")
    print(f"    is_sensitive: {is_sensitive}")

    # Verificar que esta cifrado
    if encrypted_content != password:
        print("\n[PASS] El contenido esta CIFRADO en la BD")
        # Verificar que empieza con formato Fernet
        if encrypted_content.startswith("gAAAAA"):
            print("[PASS] Formato Fernet correcto (AES-256)")
            return True
        else:
            print("[FAIL] No tiene formato Fernet")
            return False
    else:
        print("\n[FAIL] El contenido NO esta cifrado!")
        return False


def test_get_sensitive_item_decrypts():
    """Test: Obtener item sensible descifra automaticamente"""
    print("\n" + "=" * 60)
    print("TEST 2: Obtener Item Sensible (Descifrado Automatico)")
    print("=" * 60)

    db = DBManager(":memory:")

    # Crear categoria
    cat_id = db.add_category("Passwords", "lock", 0)

    # Agregar item sensible
    original_password = "SecretPassword456"
    item_id = db.add_item(
        category_id=cat_id,
        label="Email",
        content=original_password,
        is_sensitive=True
    )
    print(f"\n[OK] Item sensible creado con password: {original_password}")

    # Obtener item usando get_item()
    retrieved_item = db.get_item(item_id)

    if retrieved_item:
        retrieved_content = retrieved_item['content']
        print(f"[OK] Item recuperado")
        print(f"    Contenido descifrado: {retrieved_content}")

        if retrieved_content == original_password:
            print("\n[PASS] El contenido se DESCIFRO correctamente")
            return True
        else:
            print(f"\n[FAIL] Contenido no coincide!")
            print(f"    Esperado: {original_password}")
            print(f"    Obtenido: {retrieved_content}")
            return False
    else:
        print("[FAIL] No se pudo recuperar el item")
        return False


def test_get_items_by_category_decrypts():
    """Test: Obtener items por categoria descifra los sensibles"""
    print("\n" + "=" * 60)
    print("TEST 3: get_items_by_category() Descifra Items Sensibles")
    print("=" * 60)

    db = DBManager(":memory:")

    # Crear categoria
    cat_id = db.add_category("Credentials", "key", 0)

    # Agregar varios items (sensibles y normales)
    items_data = [
        {"label": "GitHub Token", "content": "ghp_abc123xyz", "sensitive": True},
        {"label": "API Endpoint", "content": "https://api.example.com", "sensitive": False},
        {"label": "Database Password", "content": "db_pass_987", "sensitive": True},
        {"label": "Public URL", "content": "https://example.com", "sensitive": False}
    ]

    for item_data in items_data:
        db.add_item(
            category_id=cat_id,
            label=item_data['label'],
            content=item_data['content'],
            is_sensitive=item_data['sensitive']
        )

    print(f"\n[OK] {len(items_data)} items agregados (2 sensibles, 2 normales)")

    # Obtener todos los items
    retrieved_items = db.get_items_by_category(cat_id)

    print(f"[OK] {len(retrieved_items)} items recuperados")

    # Verificar que los sensibles estan descifrados
    all_correct = True
    for i, original in enumerate(items_data):
        retrieved = retrieved_items[i]
        print(f"\n  Item {i+1}: {retrieved['label']}")
        print(f"    Sensible: {retrieved['is_sensitive']}")
        print(f"    Contenido: {retrieved['content']}")

        if retrieved['content'] == original['content']:
            print(f"    [OK] Contenido correcto")
        else:
            print(f"    [FAIL] Contenido no coincide!")
            all_correct = False

    if all_correct:
        print("\n[PASS] Todos los items descifrados correctamente")
        return True
    else:
        print("\n[FAIL] Algunos items no se descifraron bien")
        return False


def test_update_sensitive_item():
    """Test: Actualizar item sensible cifra el nuevo contenido"""
    print("\n" + "=" * 60)
    print("TEST 4: Actualizar Item Sensible (Cifrado Automatico)")
    print("=" * 60)

    db = DBManager(":memory:")

    # Crear categoria
    cat_id = db.add_category("Passwords", "lock", 0)

    # Crear item sensible
    original = "OldPassword123"
    item_id = db.add_item(
        category_id=cat_id,
        label="Test Account",
        content=original,
        is_sensitive=True
    )
    print(f"\n[OK] Item creado con password: {original}")

    # Actualizar el contenido
    new_password = "NewPassword456"
    db.update_item(item_id, content=new_password)
    print(f"[OK] Item actualizado con nuevo password: {new_password}")

    # Verificar en BD que el nuevo contenido esta cifrado
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM items WHERE id = ?", (item_id,))
    encrypted_in_db = cursor.fetchone()[0]

    print(f"    Contenido en BD: {encrypted_in_db[:50]}...")

    # Verificar que NO es texto plano
    if encrypted_in_db != new_password:
        print("[PASS] Nuevo contenido esta CIFRADO en BD")
    else:
        print("[FAIL] Nuevo contenido NO esta cifrado!")
        return False

    # Recuperar item y verificar que se descifra correctamente
    retrieved = db.get_item(item_id)
    if retrieved['content'] == new_password:
        print("[PASS] Nuevo contenido se DESCIFRA correctamente")
        return True
    else:
        print(f"[FAIL] Descifrado incorrecto: {retrieved['content']}")
        return False


def test_mark_item_as_sensitive():
    """Test: Marcar item existente como sensible cifra el contenido"""
    print("\n" + "=" * 60)
    print("TEST 5: Marcar Item Existente como Sensible")
    print("=" * 60)

    db = DBManager(":memory:")

    # Crear categoria
    cat_id = db.add_category("Passwords", "lock", 0)

    # Crear item NORMAL (no sensible)
    plaintext = "PlainTextPassword"
    item_id = db.add_item(
        category_id=cat_id,
        label="Test Item",
        content=plaintext,
        is_sensitive=False
    )
    print(f"\n[OK] Item normal creado: {plaintext}")

    # Verificar que esta en texto plano en BD
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM items WHERE id = ?", (item_id,))
    content_in_db = cursor.fetchone()[0]
    print(f"[OK] Contenido en BD (texto plano): {content_in_db}")

    # Marcar como sensible
    db.update_item(item_id, is_sensitive=True)
    print("[OK] Item marcado como sensible")

    # Actualizar el contenido (esto deberia cifrarlo)
    new_content = "NowEncryptedPassword"
    db.update_item(item_id, content=new_content)
    print(f"[OK] Contenido actualizado: {new_content}")

    # Verificar que ahora esta cifrado
    cursor.execute("SELECT content, is_sensitive FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    encrypted_content = row[0]
    is_sensitive = row[1]

    print(f"    is_sensitive: {is_sensitive}")
    print(f"    Contenido en BD: {encrypted_content[:50]}...")

    if encrypted_content != new_content and is_sensitive == 1:
        print("\n[PASS] Contenido ahora esta CIFRADO")

        # Verificar descifrado
        retrieved = db.get_item(item_id)
        if retrieved['content'] == new_content:
            print("[PASS] Descifrado correcto")
            return True
        else:
            print("[FAIL] Descifrado incorrecto")
            return False
    else:
        print("\n[FAIL] Contenido NO se cifro")
        return False


def test_normal_items_not_encrypted():
    """Test: Items normales NO se cifran"""
    print("\n" + "=" * 60)
    print("TEST 6: Items Normales NO se Cifran")
    print("=" * 60)

    db = DBManager(":memory:")

    # Crear categoria
    cat_id = db.add_category("URLs", "link", 0)

    # Agregar item normal (no sensible)
    url = "https://github.com/anthropics/claude-code"
    item_id = db.add_item(
        category_id=cat_id,
        label="GitHub Repo",
        content=url,
        is_sensitive=False
    )
    print(f"\n[OK] Item normal creado: {url}")

    # Verificar que esta en texto plano en BD
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT content, is_sensitive FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    content_in_db = row[0]
    is_sensitive = row[1]

    print(f"    is_sensitive: {is_sensitive}")
    print(f"    Contenido en BD: {content_in_db}")

    if content_in_db == url and is_sensitive == 0:
        print("\n[PASS] Item normal NO esta cifrado (correcto)")
        return True
    else:
        print("\n[FAIL] Item normal se cifro incorrectamente")
        return False


def main():
    """Ejecutar todos los tests de Fase 2"""
    print("\n" + "=" * 60)
    print("FASE 2: TEST DE CIFRADO EN BASE DE DATOS")
    print("=" * 60 + "\n")

    tests = [
        test_add_sensitive_item,
        test_get_sensitive_item_decrypts,
        test_get_items_by_category_decrypts,
        test_update_sensitive_item,
        test_mark_item_as_sensitive,
        test_normal_items_not_encrypted
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
        print("\nSistema de cifrado en BD funcionando:")
        print("  [OK] add_item() cifra contenido sensible")
        print("  [OK] get_item() descifra contenido sensible")
        print("  [OK] get_items_by_category() descifra sensibles")
        print("  [OK] update_item() cifra contenido actualizado")
        print("  [OK] Items normales NO se cifran")
        print("  [OK] Todos los tests pasaron")
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
