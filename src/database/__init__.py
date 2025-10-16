"""
Database module for Widget Sidebar
Provides SQLite database management functionality
"""

from .db_manager import DBManager
from .migrations import migrate_json_to_sqlite, backup_json_files

__all__ = ['DBManager', 'migrate_json_to_sqlite', 'backup_json_files']
