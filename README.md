# Widget Sidebar - Windows Clipboard Manager

**Version:** 2.0.0
**Framework:** PyQt6
**Architecture:** MVC (Model-View-Controller)

## Descripción

Widget de barra lateral para Windows que funciona como gestor avanzado de portapapeles con navegación jerárquica, categorías predefinidas de comandos útiles, hotkeys globales y system tray integration.

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
python test_phase4.py
```

### Interacción

**Navegación:**
1. Click en categoría (Git, CMD, etc.)
2. Panel se expande mostrando items
3. Usar SearchBar para filtrar (debouncing 300ms)
4. Click en item para copiar al portapapeles
5. Item flashea azul confirmando copia

**Hotkeys:**
- `Ctrl+Shift+V`: Toggle ventana (funciona globalmente)

**System Tray:**
- Click izquierdo: Toggle ventana
- Click derecho: Menú contextual
  - Mostrar/Ocultar
  - Configuración (próximamente)
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

**Fase actual:** FASE 4 - Hotkeys, Tray & Search ✅ COMPLETADA

- **Fase 1**: ✅ Setup y Configuración
- **Fase 2**: ✅ Core MVC
- **Fase 3**: ✅ UI Completa y Funcional
- **Fase 4**: ✅ Hotkeys, System Tray, Search (PRODUCTION READY 🚀)

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
