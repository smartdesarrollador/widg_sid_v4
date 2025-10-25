"""
Script de migración para agregar la columna is_favorite a la tabla items
"""
import sqlite3
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def add_is_favorite_column():
    """Agregar columna is_favorite a la tabla items"""
    db_path = Path(__file__).parent / "widget_sidebar.db"

    if not db_path.exists():
        print(f"❌ Error: Base de datos no encontrada en {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'is_favorite' in columns:
            print("✓ La columna 'is_favorite' ya existe en la tabla items")
            conn.close()
            return True

        # Agregar la columna is_favorite
        print("⏳ Agregando columna 'is_favorite' a la tabla items...")
        cursor.execute("ALTER TABLE items ADD COLUMN is_favorite BOOLEAN DEFAULT 0")
        conn.commit()

        # Verificar que se agregó correctamente
        cursor.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'is_favorite' in columns:
            print("✓ Columna 'is_favorite' agregada exitosamente")

            # Mostrar estadísticas
            cursor.execute("SELECT COUNT(*) FROM items")
            total_items = cursor.fetchone()[0]
            print(f"✓ Total de items en la base de datos: {total_items}")
            print(f"✓ Todos los items ahora tienen is_favorite = 0 por defecto")

            conn.close()
            return True
        else:
            print("❌ Error: No se pudo agregar la columna")
            conn.close()
            return False

    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("MIGRACIÓN: Agregar columna is_favorite")
    print("=" * 70)

    success = add_is_favorite_column()

    print("=" * 70)
    if success:
        print("✓ Migración completada exitosamente")
        print("✓ Ahora puedes marcar items como favoritos")
        print("✓ Reinicia la aplicación para aplicar los cambios")
    else:
        print("❌ La migración falló")
    print("=" * 70)
