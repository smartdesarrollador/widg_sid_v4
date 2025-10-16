# Widget Sidebar - Windows Clipboard Manager

**Version:** 3.0.0
**Framework:** PyQt6
**Architecture:** MVC (Model-View-Controller)

## Descripción

Widget de barra lateral completamente configurable para Windows. Funciona como gestor avanzado de portapapeles con navegación jerárquica, categorías personalizables, hotkeys globales, system tray integration y editor completo de configuración.

## Características

### Core Features
- ✅ Barra lateral persistente (always-on-top, frameless)
- ✅ 8 categorías predefinidas: Git, CMD, Docker, Python, NPM, URLs, Snippets, Configuración
- ✅ Sistema de copia rápida al portapapeles con feedback visual
- ✅ Animaciones fluidas (250ms smooth transitions)
- ✅ Dark theme profesional

### Advanced Features (Phase 4)
- ✅ **Hotkey global**: `Ctrl+Shift+V` para toggle ventana desde cualquier app
- ✅ **System Tray**: Ícono en bandeja con menú contextual
- ✅ **SearchBar**: Búsqueda en tiempo real con debouncing (300ms)
- ✅ **Search Engine**: Filtrado inteligente case-insensitive
- ✅ **Minimize to Tray**: Cerrar ventana minimiza a tray (no cierra app)

### Configuration Features (Phase 5)
- ✅ **Settings Window**: Ventana de configuración completa con 4 tabs
- ✅ **Category Editor**: Crear, editar y eliminar categorías e items
- ✅ **Item Editor**: Editor de items con validación (Label, Type, Content, Tags)
- ✅ **Appearance Settings**: Tema, opacidad, dimensiones, velocidad animación
- ✅ **Hotkey Settings**: Visualización y configuración de atajos (próximamente editable)
- ✅ **General Settings**: Comportamiento, historial, export/import configuración
- ✅ **Export/Import**: Guardar y restaurar configuración completa en JSON

## Instalación (Desarrollo)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

```bash
# Ejecutar aplicación
python main.py

# Ejecutar tests
python test_phase5.py
```

### Interacción

**Navegación:**
1. Click en categoría (Git, CMD, etc.)
2. Panel se expande mostrando items
3. Usar SearchBar para filtrar (debouncing 300ms)
4. Click en item para copiar al portapapeles
5. Item flashea azul confirmando copia

**Configuración:**
1. Click en botón ⚙ (parte inferior del sidebar)
2. Se abre ventana de configuración con 4 tabs:
   - **Categorías**: Crear/editar categorías e items
   - **Apariencia**: Tema, opacidad, dimensiones
   - **Hotkeys**: Ver y configurar atajos
   - **General**: Comportamiento, export/import
3. Hacer cambios deseados
4. Click "Guardar" o "Aplicar"

**Hotkeys:**
- `Ctrl+Shift+V`: Toggle ventana (funciona globalmente)

**System Tray:**
- Click izquierdo: Toggle ventana
- Click derecho: Menú contextual
  - Mostrar/Ocultar
  - Configuración
  - Salir

**Cerrar ventana:**
- Click en X → Minimiza a tray (no cierra app)
- Para salir: Tray menu → Salir

## Tecnologías

- Python 3.10+
- PyQt6
- pyperclip
- pynput

## Estado del Proyecto

**Fase actual:** FASE 5 - Settings & Configuration ✅ COMPLETADA

- **Fase 1**: ✅ Setup y Configuración
- **Fase 2**: ✅ Core MVC
- **Fase 3**: ✅ UI Completa y Funcional
- **Fase 4**: ✅ Hotkeys, System Tray, Search
- **Fase 5**: ✅ Settings Window & Configuration (FULLY CONFIGURABLE 🎛️)

## Estructura del Proyecto

```
widget_sidebar/
├── main.py
├── config.json
├── default_categories.json
├── requirements.txt
├── src/
│   ├── models/
│   ├── views/
│   ├── controllers/
│   ├── core/
│   └── utils/
└── assets/
```

## Licencia

MIT
