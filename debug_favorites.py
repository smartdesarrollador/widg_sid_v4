"""Script para debugear el problema de favoritos"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.db_manager import DBManager
from models.item import Item

# Crear conexión a base de datos
db = DBManager("widget_sidebar.db")

# Test 1: Ver estructura de la tabla items
print("=" * 80)
print("ESTRUCTURA DE LA TABLA ITEMS")
print("=" * 80)
cursor = db.connect().cursor()
cursor.execute("PRAGMA table_info(items);")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]}")

# Test 2: Ver cuántos items favoritos hay
print("\n" + "=" * 80)
print("ITEMS FAVORITOS EN LA BASE DE DATOS")
print("=" * 80)
cursor.execute("SELECT COUNT(*) FROM items WHERE is_favorite = 1;")
count = cursor.fetchone()[0]
print(f"Total items favoritos: {count}")

# Test 3: Ver algunos items favoritos
cursor.execute("SELECT id, label, is_favorite FROM items WHERE is_favorite = 1 LIMIT 5;")
favorites = cursor.fetchall()
print("\nPrimeros 5 items favoritos:")
for fav in favorites:
    print(f"  ID: {fav[0]}, Label: {fav[1]}, is_favorite: {fav[2]}")

# Test 4: Cargar items de Git con get_items_by_category
print("\n" + "=" * 80)
print("ITEMS DE GIT CARGADOS CON get_items_by_category")
print("=" * 80)
items_data = db.get_items_by_category(17)  # Git category
print(f"Total items cargados: {len(items_data)}")

for item_data in items_data[:5]:
    print(f"\nItem: {item_data['label']}")
    print(f"  ID: {item_data['id']}")
    print(f"  has 'is_favorite' key: {'is_favorite' in item_data}")
    if 'is_favorite' in item_data:
        print(f"  is_favorite value: {item_data['is_favorite']}")
        print(f"  is_favorite type: {type(item_data['is_favorite'])}")

# Test 5: Convertir a modelo Item y ver atributos
print("\n" + "=" * 80)
print("ITEMS CONVERTIDOS A MODELO Item")
print("=" * 80)
from core.config_manager import ConfigManager
config_mgr = ConfigManager()
category = config_mgr.get_category(17)  # Git
if category:
    print(f"Category: {category.name}")
    print(f"Total items: {len(category.items)}")

    for item in category.items[:5]:
        print(f"\nItem: {item.label}")
        print(f"  ID: {item.id}")
        print(f"  has 'is_favorite' attr: {hasattr(item, 'is_favorite')}")
        if hasattr(item, 'is_favorite'):
            print(f"  is_favorite value: {item.is_favorite}")
            print(f"  is_favorite type: {type(item.is_favorite)}")

db.close()
print("\n" + "=" * 80)
print("Debug completado")
