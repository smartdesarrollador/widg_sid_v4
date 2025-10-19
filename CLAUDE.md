# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Widget Sidebar is a Windows desktop application for managing clipboard content, built with PyQt6 and SQLite. It provides a persistent sidebar widget for quick access to frequently used commands, URLs, and code snippets across 8 predefined categories (Git, CMD, Docker, Python, NPM, URLs, Snippets, Config).

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

### Database Layer (`src/database/`)
The application uses SQLite for persistence:

- `db_manager.py`: Database operations with context managers for transactions
- `migrations.py`: Database schema migrations
- Database file: `widget_sidebar.db` (created automatically on first run)

Schema includes: `settings`, `categories`, `items`, `clipboard_history`, `hotkeys`

**Important:** Database connection uses `check_same_thread=False` for PyQt6 compatibility. Always use the transaction context manager for write operations:
```python
with db.transaction() as conn:
    conn.execute(...)
```

### Entry Point Flow
1. `main.py` initializes logging and handles frozen/script execution paths
2. Creates `MainController` which initializes `ConfigManager` with SQLite
3. `ConfigManager` loads categories/items from database
4. `MainWindow` created with controller reference
5. Hotkey manager and tray manager initialized
6. Categories loaded into sidebar UI

### Window Architecture
- **MainWindow**: Frameless, always-on-top sidebar (70px wide, 80% screen height)
- **FloatingPanel**: Separate window for displaying category items, positioned adjacent to sidebar
- **SettingsWindow**: Modal dialog with 4 tabs (Categories, Appearance, Hotkeys, General)

### Signal/Slot Communication
PyQt6 signals connect components:
- `category_selected` (str): Emitted when category clicked in sidebar
- `item_selected` (Item): Emitted when item clicked in content panel
- `item_copied` (Item): Emitted after successful clipboard copy

## Key Implementation Details

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

## Common Tasks

### Adding a New Category Programmatically
```python
# Via ConfigManager
category_data = {
    'name': 'New Category',
    'icon': '🆕',
    'color': '#007acc',
    'order_index': 8
}
category_id = config_manager.db.add_category(category_data)
```

### Adding Items to Category
```python
item_data = {
    'category_id': category_id,
    'name': 'My Command',
    'content': 'git status',
    'item_type': 'command',
    'order_index': 0
}
item_id = config_manager.db.add_item(item_data)
```

### Modifying Global Hotkey
Edit `src/core/hotkey_manager.py` and update the key combination in `setup_hotkeys()` method.

## Version History

- **3.0.0**: Settings window with full CRUD for categories/items, appearance customization, export/import
- **2.0.0**: Global hotkeys, system tray, search functionality, SQLite migration
- **1.0.0**: Initial release with sidebar, content panel, dark theme, animations
