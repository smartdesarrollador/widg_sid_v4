# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Widget Sidebar is a Windows desktop application for managing clipboard content, built with PyQt6 and SQLite. It provides a persistent sidebar widget for quick access to frequently used commands, URLs, and code snippets. Features include password protection, encrypted sensitive items, favorites, usage tracking, advanced filtering, and global search.

**Version:** 3.0.0 (SQLite Edition)
**Platform:** Windows 10/11
**Python:** 3.10+

## Development Commands

### Running the Application
```bash
# From source (requires Python 3.10+)
python main.py

# From virtual environment
.\venv\Scripts\activate
python main.py
```

### Building Executable
```bash
# Build standalone .exe with PyInstaller
build.bat

# Output location: dist\WidgetSidebar.exe
# Distribution package: WidgetSidebar_v2.0\
```

### Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Core dependencies:
# - PyQt6 (6.7.0) - GUI framework
# - pyperclip (1.9.0) - Clipboard management
# - pynput (1.7.7) - Global hotkey capture
# - cryptography (41.0.7) - Encryption for sensitive items
# - python-dotenv (1.0.0) - Environment variable management
```

## Architecture

### MVC Pattern
The application follows Model-View-Controller architecture:

- **Models** (`src/models/`): Data structures (Category, Item, Config)
- **Views** (`src/views/`): PyQt6 UI components (MainWindow, Sidebar, ContentPanel, SettingsWindow, FloatingPanel)
- **Controllers** (`src/controllers/`): Business logic (MainController, ClipboardController, NavigationController)

### Core Managers (`src/core/`)
- `config_manager.py`: Configuration persistence via SQLite
- `clipboard_manager.py`: Clipboard operations using pyperclip
- `hotkey_manager.py`: Global hotkey handling with pynput
- `tray_manager.py`: System tray integration
- `search_engine.py`: Real-time search with debouncing
- `state_manager.py`: Application state management
- `auth_manager.py`: User authentication using bcrypt password hashing
- `session_manager.py`: Session management with automatic expiry
- `encryption_manager.py`: Fernet encryption for sensitive item content
- `favorites_manager.py`: Favorites tracking and management
- `usage_tracker.py`: Item usage statistics and analytics
- `stats_manager.py`: Dashboard statistics aggregation
- `notification_manager.py`: In-app notification system
- `category_filter_engine.py`: Category filtering with caching
- `advanced_filter_engine.py`: Complex multi-criteria filtering

### Database Layer (`src/database/`)
The application uses SQLite for persistence:

- `db_manager.py`: Database operations with context managers for transactions
- `migrations.py`: Database schema migrations
- Database file: `widget_sidebar.db` (created automatically on first run)

Schema includes: `settings`, `categories`, `items`, `clipboard_history`

**Important:** Database connection uses `check_same_thread=False` for PyQt6 compatibility. Always use the transaction context manager for write operations:
```python
with db.transaction() as conn:
    conn.execute(...)
```

**Sensitive Item Encryption:** Items marked with `is_sensitive=True` have their `content` field automatically encrypted at the database layer using Fernet encryption. Encryption/decryption happens transparently in `DBManager.add_item()`, `DBManager.update_item()`, and `DBManager.get_items_by_category()`.

### Entry Point Flow
1. `main.py` initializes logging and handles frozen/script execution paths
2. Creates QApplication instance
3. **Authentication flow:**
   - `SessionManager` checks for valid session
   - If first time: `FirstTimeWizard` for password creation
   - If returning: `LoginDialog` for password entry
   - On failure: exits application
4. Creates `MainController` which initializes `ConfigManager` with SQLite
5. `ConfigManager` loads categories/items from database (auto-decrypts sensitive items)
6. `MainWindow` created with controller reference
7. Hotkey manager and tray manager initialized
8. Categories loaded into sidebar UI

### Window Architecture
- **MainWindow**: Frameless, always-on-top sidebar (70px wide, 80% screen height)
- **FloatingPanel**: Separate window for displaying category items, positioned adjacent to sidebar
- **FavoritesFloatingPanel**: Dedicated panel for favorites view
- **StatsFloatingPanel**: Statistics dashboard panel
- **GlobalSearchPanel**: Full-screen search across all items
- **SettingsWindow**: Modal dialog with 4 tabs (Categories, Appearance, Hotkeys, General)
- **CategoryFilterWindow**: Category filtering interface
- **AdvancedFiltersWindow**: Complex multi-criteria filtering UI
- **FirstTimeWizard**: Password setup wizard for first run
- **LoginDialog**: Authentication dialog on subsequent runs

### Signal/Slot Communication
PyQt6 signals connect components:
- `category_selected` (str): Emitted when category clicked in sidebar
- `item_selected` (Item): Emitted when item clicked in content panel
- `item_copied` (Item): Emitted after successful clipboard copy

## Key Implementation Details

### Authentication & Security
- **Password Protection**: First run shows `FirstTimeWizard` to set master password
- **Session Management**: Sessions auto-expire (default 24h), stored in database
- **Password Hashing**: Uses bcrypt via `AuthManager` for secure password storage
- **Encryption**: Sensitive items encrypted with Fernet (symmetric encryption)
  - Encryption key stored in `.env` file (auto-generated on first run)
  - Key derivation: PBKDF2 from master password
  - Encryption/decryption transparent at database layer

### Hotkey System
- Global hotkey `Ctrl+Shift+V` toggles widget visibility from any application
- Managed by `HotkeyManager` using pynput keyboard listener
- Runs in background thread, communicates via PyQt6 signals

### System Tray
- Minimizes to system tray instead of closing
- Context menu: Show/Hide, Settings, Exit
- Double-click tray icon to restore window

### Search Functionality
- Real-time filtering in `search_bar.py` with 300ms debounce
- `search_engine.py` provides fuzzy matching across item names and content
- Filters items within active category

### Favorites & Usage Tracking
- Items can be marked as favorites (`is_favorite` field)
- `usage_tracker.py` tracks item usage with metrics:
  - Last used timestamp
  - Usage count
  - Usage patterns (time-based analytics)
- `favorites_manager.py` provides favorites filtering and management
- Stats available in `StatsFloatingPanel` and `StatsDashboard`

### Category Filtering
- **Basic Filtering**: `CategoryFilterWindow` filters by active/pinned status
- **Advanced Filtering**: `AdvancedFiltersWindow` supports:
  - Text search (name, tags, content)
  - Item count ranges
  - Usage metrics (access count, date ranges)
  - Multiple criteria with AND logic
- **Filter Engine**: `CategoryFilterEngine` with LRU caching for performance

### Global Search
- `GlobalSearchPanel` searches across ALL items in ALL categories
- Real-time filtering with debouncing
- Shows category context for each result
- Click result to copy content to clipboard

### Configuration Persistence
**Migration from JSON to SQLite:** The application originally used JSON files (`config.json`, `default_categories.json`). Now uses SQLite exclusively. The `build.bat` script includes migration step from JSON to database.

### PyInstaller Build
- Spec file: `widget_sidebar.spec`
- Includes SQLite database, resources, and hidden imports for pynput
- Console mode disabled (`console=False`)
- UPX compression enabled

## Project Structure
```
widget_sidebar/
├── main.py                      # Application entry point
├── widget_sidebar.db            # SQLite database (auto-created)
├── config.json                  # Legacy config (deprecated)
├── default_categories.json      # Default categories seed data
├── requirements.txt             # Python dependencies
├── widget_sidebar.spec          # PyInstaller configuration
├── build.bat                    # Build script for Windows exe
└── src/
    ├── models/                  # Data models (Category, Item, Config)
    ├── views/                   # PyQt6 UI components
    │   ├── main_window.py       # Main frameless window
    │   ├── sidebar.py           # Category sidebar
    │   ├── floating_panel.py    # Items display panel
    │   ├── settings_window.py   # Settings dialog
    │   └── widgets/             # Reusable UI widgets
    ├── controllers/             # Business logic layer
    ├── core/                    # Core functionality (config, clipboard, hotkeys, tray, search)
    ├── database/                # SQLite database management
    ├── utils/                   # Utilities (animations, validators, constants, logger)
    └── resources/               # Static resources (if any)
```

## Important Conventions

### Path Handling
The application supports both script and frozen (exe) execution:
```python
if getattr(sys, 'frozen', False):
    base_dir = Path(sys.executable).parent  # Running as exe
else:
    base_dir = Path(__file__).parent        # Running as script
```
Always use this pattern when referencing application files.

### Environment Variables
- `.env` file stores encryption key (auto-generated)
- Never commit `.env` to version control
- `EncryptionManager` handles key generation and loading

### Logging
Comprehensive logging configured in `main.py`:
- Log file: `widget_sidebar_error.log` (overwritten each session)
- Log level: DEBUG
- Global exception handler captures uncaught exceptions
- Use `logger = logging.getLogger(__name__)` in each module

### Window Positioning
MainWindow positions at right edge of screen with 10% margins:
```python
screen_height = screen.availableGeometry().height()
window_height = int(screen_height * 0.8)  # 80% height
```

### Database Access
- ConfigManager owns the DBManager instance
- Always close database on application exit (handled in MainController.__del__)
- Use transactions for data integrity
- **Cache Invalidation**: Call `controller.invalidate_filter_cache()` after any database modifications to ensure filter cache coherency

## Common Tasks

### Adding a New Category Programmatically
```python
# Via DBManager directly
category_id = db.add_category(
    name='New Category',
    icon='🆕',
    is_predefined=False
)
```

### Adding Items to Category
```python
# Regular item
item_id = db.add_item(
    category_id=category_id,
    label='My Command',
    content='git status',
    item_type='CODE'
)

# Sensitive item (auto-encrypted)
item_id = db.add_item(
    category_id=category_id,
    label='API Key',
    content='sk-1234567890',
    item_type='TEXT',
    is_sensitive=True  # Content will be encrypted
)
```

### Working with Encrypted Content
```python
# Encryption happens automatically in DBManager
# When adding/updating items:
db.add_item(..., is_sensitive=True)  # Content encrypted before storage

# When retrieving items:
items = db.get_items_by_category(cat_id)  # Content auto-decrypted if sensitive
```

### Managing Sessions
```python
from core.session_manager import SessionManager

session_mgr = SessionManager()
# Check if session valid
if session_mgr.validate_session():
    print("Valid session")
else:
    # Show login dialog
    pass
```

### Modifying Global Hotkey
Edit `src/core/hotkey_manager.py` and update the key combination in `setup_hotkeys()` method.

## Version History

- **3.0.0**: Settings window with full CRUD for categories/items, appearance customization, export/import
- **2.0.0**: Global hotkeys, system tray, search functionality, SQLite migration
- **1.0.0**: Initial release with sidebar, content panel, dark theme, animations
