"""
Config Manager
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add models to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.category import Category


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            # Get the project root directory
            self.base_dir = Path(__file__).parent.parent.parent
        else:
            self.base_dir = Path(base_dir)

        self.config_file = self.base_dir / "config.json"
        self.default_categories_file = self.base_dir / "default_categories.json"

        self.config_data: Dict[str, Any] = {}
        self.categories: List[Category] = []

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                return self.config_data
            else:
                print(f"Config file not found: {self.config_file}")
                return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def save_config(self, config_data: Optional[Dict[str, Any]] = None) -> bool:
        """Save configuration to config.json"""
        try:
            data_to_save = config_data if config_data is not None else self.config_data

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def load_default_categories(self) -> List[Category]:
        """Load default categories from default_categories.json"""
        try:
            if not self.default_categories_file.exists():
                print(f"Default categories file not found: {self.default_categories_file}")
                return []

            with open(self.default_categories_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            categories_data = data.get("categories", [])
            self.categories = []

            for cat_data in categories_data:
                category = Category.from_dict(cat_data)
                if category.validate():
                    self.categories.append(category)

            print(f"Loaded {len(self.categories)} categories")
            return self.categories

        except Exception as e:
            print(f"Error loading default categories: {e}")
            return []

    def get_categories(self) -> List[Category]:
        """Get all categories"""
        if not self.categories:
            self.load_default_categories()
        return self.categories

    def get_category(self, category_id: str) -> Optional[Category]:
        """Get a specific category by ID"""
        for category in self.categories:
            if category.id == category_id:
                return category
        return None

    def add_category(self, category: Category) -> bool:
        """Add a new category"""
        if category.validate():
            self.categories.append(category)
            return True
        return False

    def update_category(self, category_id: str, updated_category: Category) -> bool:
        """Update an existing category"""
        for i, cat in enumerate(self.categories):
            if cat.id == category_id:
                self.categories[i] = updated_category
                return True
        return False

    def delete_category(self, category_id: str) -> bool:
        """Delete a category by ID"""
        for i, cat in enumerate(self.categories):
            if cat.id == category_id:
                self.categories.pop(i)
                return True
        return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting from config"""
        if not self.config_data:
            self.load_config()
        return self.config_data.get("settings", {}).get(key, default)

    def set_setting(self, key: str, value: Any) -> bool:
        """Set a specific setting in config"""
        if not self.config_data:
            self.load_config()

        if "settings" not in self.config_data:
            self.config_data["settings"] = {}

        self.config_data["settings"][key] = value
        return self.save_config()

    def export_config(self, export_path: Path) -> bool:
        """Export configuration to a file"""
        try:
            export_data = {
                "config": self.config_data,
                "categories": [cat.to_dict() for cat in self.categories]
            }

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False

    def import_config(self, import_path: Path) -> bool:
        """Import configuration from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "config" in data:
                self.config_data = data["config"]
                self.save_config()

            if "categories" in data:
                self.categories = []
                for cat_data in data["categories"]:
                    category = Category.from_dict(cat_data)
                    if category.validate():
                        self.categories.append(category)

            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False
