"""
Migration script for Widget Sidebar
Migrates data from JSON files to SQLite database
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from .db_manager import DBManager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_json_to_sqlite(
    json_config_path: str = "config.json",
    json_defaults_path: str = "default_categories.json",
    db_path: str = "widget_sidebar.db"
) -> None:
    """
    Migrate data from JSON files to SQLite database

    Args:
        json_config_path: Path to config.json file
        json_defaults_path: Path to default_categories.json file
        db_path: Path to SQLite database file

    Raises:
        FileNotFoundError: If required JSON files don't exist
        json.JSONDecodeError: If JSON files are invalid
        Exception: If migration fails
    """

    print("="*60)
    print("🔄 Iniciando migración de JSON a SQLite...")
    print("="*60)

    # Counters for statistics
    stats = {
        'settings': 0,
        'categories': 0,
        'items': 0,
        'history': 0
    }

    try:
        # Step 1: Create DBManager instance
        print("\n[1/6] Creando base de datos...")
        db = DBManager(db_path)
        print(f"✅ Base de datos inicializada: {db_path}")

        # Step 2: Load and migrate config.json
        config_path = Path(json_config_path)
        config_data = {}

        if config_path.exists():
            print(f"\n[2/6] Leyendo {json_config_path}...")
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            print(f"✅ Archivo cargado: {json_config_path}")
        else:
            print(f"\n[2/6] ⚠️  {json_config_path} no encontrado, usando valores por defecto")
            config_data = {'settings': {}, 'categories': [], 'history': []}

        # Step 3: Migrate settings
        print("\n[3/6] Migrando configuraciones...")
        settings = config_data.get('settings', {})

        # Flatten nested settings (like window_position)
        flat_settings = {}
        for key, value in settings.items():
            if isinstance(value, dict):
                # For nested objects, store as JSON
                flat_settings[key] = value
            else:
                flat_settings[key] = value

        for key, value in flat_settings.items():
            db.set_setting(key, value)
            stats['settings'] += 1

        print(f"✅ Configuraciones migradas: {stats['settings']} settings")

        # Step 4: Load and migrate default_categories.json
        defaults_path = Path(json_defaults_path)

        if defaults_path.exists():
            print(f"\n[4/6] Leyendo {json_defaults_path}...")
            with open(defaults_path, 'r', encoding='utf-8') as f:
                defaults_data = json.load(f)
            print(f"✅ Archivo cargado: {json_defaults_path}")

            # Migrate predefined categories
            print("   Migrando categorías predefinidas...")
            predefined_categories = defaults_data.get('categories', [])

            for cat_data in predefined_categories:
                # Add category
                cat_id = db.add_category(
                    name=cat_data['name'],
                    icon=cat_data.get('icon'),
                    is_predefined=True
                )
                stats['categories'] += 1

                # Add items for this category
                items = cat_data.get('items', [])
                for item_data in items:
                    # Determine item type
                    content = item_data['content']
                    item_type = _determine_item_type(content)

                    db.add_item(
                        category_id=cat_id,
                        label=item_data['label'],
                        content=content,
                        item_type=item_type,
                        icon=item_data.get('icon'),
                        is_sensitive=item_data.get('is_sensitive', False),
                        tags=item_data.get('tags', [])
                    )
                    stats['items'] += 1

                print(f"   ✓ {cat_data['name']}: {len(items)} items")

            print(f"✅ Categorías predefinidas: {len(predefined_categories)} categorías, {stats['items']} items")
        else:
            print(f"\n[4/6] ⚠️  {json_defaults_path} no encontrado")

        # Step 5: Migrate custom categories from config.json
        print("\n[5/6] Migrando categorías personalizadas...")
        custom_categories = config_data.get('categories', [])
        custom_items_count = 0

        if custom_categories:
            for cat_data in custom_categories:
                # Add custom category
                cat_id = db.add_category(
                    name=cat_data['name'],
                    icon=cat_data.get('icon'),
                    is_predefined=False
                )
                stats['categories'] += 1

                # Add items
                items = cat_data.get('items', [])
                for item_data in items:
                    content = item_data['content']
                    item_type = _determine_item_type(content)

                    db.add_item(
                        category_id=cat_id,
                        label=item_data['label'],
                        content=content,
                        item_type=item_type,
                        icon=item_data.get('icon'),
                        is_sensitive=item_data.get('is_sensitive', False),
                        tags=item_data.get('tags', [])
                    )
                    custom_items_count += 1

                print(f"   ✓ {cat_data['name']}: {len(items)} items")

            print(f"✅ Categorías personalizadas: {len(custom_categories)} categorías, {custom_items_count} items")
        else:
            print("✅ Sin categorías personalizadas")

        # Step 6: Migrate clipboard history
        print("\n[6/6] Migrando historial de portapapeles...")
        history = config_data.get('history', [])

        if history:
            for hist_entry in history:
                # History entries from JSON might not have item_id
                content = hist_entry.get('content', '') if isinstance(hist_entry, dict) else str(hist_entry)
                db.add_to_history(item_id=None, content=content)
                stats['history'] += 1

            print(f"✅ Historial migrado: {stats['history']} entradas")
        else:
            print("✅ Sin historial previo")

        # Close database connection
        db.close()

        # Print final statistics
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("="*60)
        print(f"\n📊 Estadísticas:")
        print(f"   • Settings:   {stats['settings']} configuraciones")
        print(f"   • Categorías: {stats['categories']} categorías")
        print(f"   • Items:      {stats['items'] + custom_items_count} items totales")
        print(f"   • Historial:  {stats['history']} entradas")
        print(f"\n📁 Base de datos creada en: {Path(db_path).absolute()}")
        print("="*60)

    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        print(f"\n❌ Error: Archivo no encontrado - {e}")
        raise

    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON: {e}")
        print(f"\n❌ Error: JSON inválido - {e}")
        raise

    except Exception as e:
        logger.error(f"Error durante la migración: {e}")
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        raise


def _determine_item_type(content: str) -> str:
    """
    Determine item type based on content

    Args:
        content: Item content string

    Returns:
        str: Item type (TEXT, URL, CODE, PATH)
    """
    content_lower = content.lower().strip()

    # Check if it's a URL
    if content_lower.startswith(('http://', 'https://', 'www.')):
        return 'URL'

    # Check if it's a file path
    if '\\' in content or content.startswith('/') or content.startswith('./'):
        return 'PATH'

    # Check if it's code (contains common code patterns)
    code_indicators = [
        'git ', 'docker ', 'npm ', 'pip ', 'python ',
        'cd ', 'mkdir ', 'chmod ', 'chown ',
        '#!/', 'def ', 'class ', 'import ', 'from ',
        'function', 'const ', 'let ', 'var ',
        '<?php', '<?=', 'SELECT', 'INSERT', 'UPDATE'
    ]

    for indicator in code_indicators:
        if indicator in content_lower or content_lower.startswith(indicator):
            return 'CODE'

    # Default to TEXT
    return 'TEXT'


def backup_json_files(
    config_path: str = "config.json",
    defaults_path: str = "default_categories.json",
    backup_suffix: str = ".backup"
) -> None:
    """
    Create backup copies of JSON files before migration

    Args:
        config_path: Path to config.json
        defaults_path: Path to default_categories.json
        backup_suffix: Suffix to add to backup files
    """
    import shutil

    print("🔄 Creando backup de archivos JSON...")

    config = Path(config_path)
    if config.exists():
        backup_path = config.with_suffix(config.suffix + backup_suffix)
        shutil.copy2(config, backup_path)
        print(f"✅ Backup creado: {backup_path}")

    defaults = Path(defaults_path)
    if defaults.exists():
        backup_path = defaults.with_suffix(defaults.suffix + backup_suffix)
        shutil.copy2(defaults, backup_path)
        print(f"✅ Backup creado: {backup_path}")


if __name__ == "__main__":
    """
    Run migration when script is executed directly
    """
    import sys

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Uso: python -m src.database.migrations [opciones]")
            print("\nOpciones:")
            print("  -h, --help     Mostrar esta ayuda")
            print("  --backup       Crear backup antes de migrar")
            print("\nEjemplo:")
            print("  python -m src.database.migrations")
            print("  python -m src.database.migrations --backup")
            sys.exit(0)

        if sys.argv[1] == '--backup':
            backup_json_files()

    # Run migration
    try:
        migrate_json_to_sqlite()
    except Exception as e:
        print(f"\n❌ La migración falló: {e}")
        sys.exit(1)
