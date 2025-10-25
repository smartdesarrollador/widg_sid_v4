"""Script para agregar columnas necesarias para favoritos y estadisticas"""
import sqlite3
import os

db_path = "widget_sidebar.db"

if not os.path.exists(db_path):
    print(f"ERROR: Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar columnas actuales
    cursor.execute("PRAGMA table_info(items)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Columnas actuales: {columns}")

    changes_made = False

    # Agregar favorite_order si no existe
    if 'favorite_order' not in columns:
        print("Agregando columna favorite_order...")
        cursor.execute("ALTER TABLE items ADD COLUMN favorite_order INTEGER DEFAULT 0")
        conn.commit()
        print("OK: Columna favorite_order agregada")
        changes_made = True
    else:
        print("OK: La columna favorite_order ya existe")

    # Agregar use_count si no existe
    if 'use_count' not in columns:
        print("Agregando columna use_count...")
        cursor.execute("ALTER TABLE items ADD COLUMN use_count INTEGER DEFAULT 0")
        conn.commit()
        print("OK: Columna use_count agregada")
        changes_made = True
    else:
        print("OK: La columna use_count ya existe")

    # Agregar badge si no existe
    if 'badge' not in columns:
        print("Agregando columna badge...")
        cursor.execute("ALTER TABLE items ADD COLUMN badge TEXT")
        conn.commit()
        print("OK: Columna badge agregada")
        changes_made = True
    else:
        print("OK: La columna badge ya existe")

    # Verificar columnas finales
    cursor.execute("PRAGMA table_info(items)")
    final_columns = [col[1] for col in cursor.fetchall()]
    print(f"\nColumnas finales: {final_columns}")

    conn.close()

    if changes_made:
        print("\nMigracion completada - Se agregaron columnas faltantes")
    else:
        print("\nMigracion completada - Todas las columnas ya existian")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
