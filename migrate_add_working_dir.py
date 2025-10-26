"""
Migration script to add working_dir column to items table
"""
import sqlite3
from pathlib import Path

def migrate():
    """Add working_dir column to items table"""
    db_path = Path(__file__).parent / "widget_sidebar.db"

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'working_dir' in columns:
            print("[OK] Column 'working_dir' already exists in items table")
        else:
            print("Adding 'working_dir' column to items table...")
            cursor.execute("""
                ALTER TABLE items
                ADD COLUMN working_dir TEXT
            """)
            conn.commit()
            print("[OK] Successfully added 'working_dir' column to items table")

        # Show current schema
        print("\nCurrent items table schema:")
        cursor.execute("PRAGMA table_info(items)")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")

    except Exception as e:
        print(f"[ERROR] Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
