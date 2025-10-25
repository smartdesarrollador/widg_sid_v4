"""Script para agregar columna is_favorite"""
import sqlite3

db_path = "widget_sidebar.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar columnas actuales
    cursor.execute("PRAGMA table_info(items)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'is_favorite' in columns:
        print("OK: La columna is_favorite ya existe")
    else:
        print("Agregando columna is_favorite...")
        cursor.execute("ALTER TABLE items ADD COLUMN is_favorite BOOLEAN DEFAULT 0")
        conn.commit()
        print("OK: Columna is_favorite agregada exitosamente")

    conn.close()
    print("Migracion completada")

except Exception as e:
    print(f"ERROR: {e}")
