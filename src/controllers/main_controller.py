"""
Main Controller
"""
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.config_manager import ConfigManager
from core.clipboard_manager import ClipboardManager
from controllers.clipboard_controller import ClipboardController
from models.category import Category
from models.item import Item


class MainController:
    """Main application controller - coordinates all app logic"""

    def __init__(self):
        # Initialize managers
        self.config_manager = ConfigManager()
        self.clipboard_manager = ClipboardManager()

        # Initialize controllers
        self.clipboard_controller = ClipboardController(self.clipboard_manager)

        # Data
        self.categories: List[Category] = []
        self.current_category: Optional[Category] = None

        # Load initial data
        self.load_data()

    def load_data(self) -> None:
        """Load configuration and categories"""
        print("Loading configuration...")
        self.config_manager.load_config()

        print("Loading categories...")
        self.categories = self.config_manager.load_default_categories()

        print(f"Loaded {len(self.categories)} categories")
        for cat in self.categories:
            print(f"  - {cat.name}: {len(cat.items)} items")

    def get_categories(self) -> List[Category]:
        """Get all categories"""
        return self.categories

    def get_category(self, category_id: str) -> Optional[Category]:
        """Get a specific category by ID"""
        return self.config_manager.get_category(category_id)

    def set_current_category(self, category_id: str) -> bool:
        """Set the currently active category"""
        category = self.get_category(category_id)
        if category:
            self.current_category = category
            print(f"Active category: {category.name}")
            return True
        return False

    def get_current_category(self) -> Optional[Category]:
        """Get the currently active category"""
        return self.current_category

    def copy_item_to_clipboard(self, item: Item) -> bool:
        """Copy an item to clipboard"""
        return self.clipboard_controller.copy_item(item)

    def get_clipboard_history(self, limit: int = 10):
        """Get clipboard history"""
        return self.clipboard_controller.get_history(limit)

    def get_setting(self, key: str, default=None):
        """Get a configuration setting"""
        return self.config_manager.get_setting(key, default)

    def set_setting(self, key: str, value) -> bool:
        """Set a configuration setting"""
        return self.config_manager.set_setting(key, value)
