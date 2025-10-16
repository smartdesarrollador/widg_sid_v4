# Widget Sidebar - Windows Clipboard Manager

**Version:** 1.0.0
**Framework:** PyQt6
**Architecture:** MVC (Model-View-Controller)

## Descripción

Widget de barra lateral para Windows que funciona como gestor avanzado de portapapeles con navegación jerárquica y categorías predefinidas de comandos útiles.

## Características

- Barra lateral persistente (always-on-top)
- 8 categorías predefinidas: Git, CMD, Docker, Python, NPM, URLs, Snippets, Configuración
- Sistema de copia rápida al portapapeles
- Hotkeys globales personalizables
- Temas dark/light
- Animaciones fluidas

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
```

## Hotkeys por defecto

- `Ctrl+Shift+V`: Toggle ventana
- `Esc`: Cerrar panel

## Tecnologías

- Python 3.10+
- PyQt6
- pyperclip
- pynput

## Estado del Proyecto

**Fase actual:** FASE 3 - UI Implementation ✅ COMPLETADA

- **Fase 1**: ✅ Setup y Configuración
- **Fase 2**: ✅ Core MVC
- **Fase 3**: ✅ UI Completa y Funcional

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
