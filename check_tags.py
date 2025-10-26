"""Script para verificar los tags en la base de datos"""
import sqlite3
import json

# Conectar a la base de datos
conn = sqlite3.connect("widget_sidebar.db")
cursor = conn.cursor()

# Obtener algunos items con tags
cursor.execute("SELECT id, label, tags, type FROM items WHERE tags IS NOT NULL AND tags != '' AND tags != '[]' LIMIT 10")
rows = cursor.fetchall()

print("Items con tags en la base de datos:")
print("=" * 80)
for row in rows:
    item_id, label, tags, item_type = row
    print(f"ID: {item_id}")
    print(f"Label: {label}")
    print(f"Tags (raw): {repr(tags)}")
    print(f"Tags (type): {type(tags)}")

    # Intentar parsear tags
    try:
        if isinstance(tags, str):
            parsed_tags = json.loads(tags)
            print(f"Tags (parsed): {parsed_tags}")
            print(f"Tags (parsed type): {type(parsed_tags)}")
    except Exception as e:
        print(f"Error parsing tags: {e}")

    print("-" * 80)

conn.close()
