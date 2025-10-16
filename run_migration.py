"""
Script temporal para ejecutar migracion sin problemas de encoding
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database.db_manager import DBManager
import json
import shutil
from datetime import datetime

def backup_files():
    """Crear backup de archivos JSON"""
    print("Creando backups...")

    if Path('config.json').exists():
        shutil.copy2('config.json', 'config.json.backup')
        print("  - config.json.backup creado")

    if Path('default_categories.json').exists():
        shutil.copy2('default_categories.json', 'default_categories.json.backup')
        print("  - default_categories.json.backup creado")

def determine_item_type(content: str) -> str:
    """Determinar tipo de item basado en contenido"""
    if content.startswith(('http://', 'https://', 'www.')):
        return 'URL'

    if '\\' in content or (content.startswith('/') and '/' in content[1:]):
        return 'PATH'

    code_indicators = [
        'git ', 'npm ', 'python ', 'pip ', 'docker ',
        'cd ', 'mkdir ', 'rm ', 'cp ', 'mv ',
        'def ', 'class ', 'import ', 'from ',
        '#!/', '&&', '||', '$(', '${',
        'SELECT', 'INSERT', 'UPDATE', 'DELETE'
    ]

    if any(cmd in content for cmd in code_indicators):
        return 'CODE'

    return 'TEXT'

def migrate():
    """Ejecutar migracion"""
    print("\nEjecutando migracion...")

    # Inicializar DB
    db = DBManager('widget_sidebar.db')
    print("  - Base de datos inicializada")

    # Migrar settings
    if Path('config.json').exists():
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            settings = config.get('settings', {})

            for key, value in settings.items():
                db.set_setting(key, value)

            print(f"  - {len(settings)} settings migrados")

    # Migrar categorias e items
    if Path('default_categories.json').exists():
        with open('default_categories.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            categories = data.get('categories', [])

            total_items = 0

            for cat in categories:
                # Agregar categoria
                cat_id = db.add_category(
                    name=cat['name'],
                    icon=cat.get('icon', ''),
                    is_predefined=cat.get('is_predefined', False)
                )

                # Agregar items
                items = cat.get('items', [])
                for item in items:
                    item_type = determine_item_type(item.get('content', ''))

                    db.add_item(
                        category_id=cat_id,
                        label=item.get('label', ''),
                        content=item.get('content', ''),
                        item_type=item_type,
                        icon=item.get('icon'),
                        is_sensitive=item.get('is_sensitive', False),
                        tags=item.get('tags', [])
                    )
                    total_items += 1

            print(f"  - {len(categories)} categorias migradas")
            print(f"  - {total_items} items migrados")

    db.close()
    print("\nMigracion completada exitosamente!")

if __name__ == '__main__':
    backup_files()
    migrate()
