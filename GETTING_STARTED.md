# Getting Started - Widget Sidebar

## Instalación y Ejecución

### 1. Verificar Instalación de Dependencias

Las dependencias ya están instaladas. Para verificar:

```bash
pip list | findstr "PyQt6\|pyperclip\|pynput"
```

Deberías ver:
```
PyQt6         6.7.0
PyQt6-Qt6     6.7.0
pyperclip     1.9.0
pynput        1.7.7
```

### 2. Ejecutar Tests

Para verificar que el core MVC funciona correctamente:

```bash
cd C:\Users\ASUS\Desktop\proyectos_python\widget_sidebar
python test_phase2.py
```

**Resultado esperado**: Todos los tests pasan ✓

### 3. Ejecutar la Aplicación

Para iniciar el Widget Sidebar:

```bash
python main.py
```

**Resultado**: Se abrirá una ventana sin marco en el borde derecho de tu pantalla con el texto "Widget Sidebar - Core MVC Loaded - Phase 2 in Progress".

### 4. Probar Funcionalidades

#### Ventana Principal
- ✓ Ventana sin bordes (frameless)
- ✓ Siempre visible (always-on-top)
- ✓ Posicionada automáticamente en borde derecho
- ✓ Arrastrable con el mouse
- ✓ Opacidad 95%

#### Core MVC
- ✓ 8 categorías cargadas
- ✓ 86 items totales
- ✓ ConfigManager funcional
- ✓ ClipboardManager funcional

## Estructura del Proyecto

```
widget_sidebar/
├── main.py                      # Punto de entrada
├── test_phase2.py               # Tests del core MVC
├── config.json                  # Configuración de la app
├── default_categories.json      # Categorías predefinidas
├── requirements.txt             # Dependencias
├── PHASE2_SUMMARY.md           # Resumen de Fase 2
├── src/
│   ├── models/
│   │   ├── category.py         # Modelo Category
│   │   └── item.py             # Modelo Item
│   ├── core/
│   │   ├── config_manager.py   # Gestor de configuración
│   │   └── clipboard_manager.py # Gestor de portapapeles
│   ├── controllers/
│   │   ├── main_controller.py  # Controlador principal
│   │   └── clipboard_controller.py
│   └── views/
│       └── main_window.py      # Ventana principal PyQt6
```

## Categorías Disponibles

1. **Git Commands** (14 items)
   - git status, git add, git commit, etc.

2. **CMD Commands** (13 items)
   - dir, cd, mkdir, ipconfig, etc.

3. **Docker Commands** (16 items)
   - docker ps, docker run, docker-compose, etc.

4. **Python Commands** (15 items)
   - python, pip install, venv, pytest, etc.

5. **NPM Commands** (12 items)
   - npm init, npm install, npm run, etc.

6. **URLs Útiles** (9 items)
   - GitHub, Stack Overflow, Python Docs, etc.

7. **Code Snippets** (7 items)
   - Python main block, try-except, async function, etc.

8. **Configuración** (0 items)
   - Categoría vacía para personalización futura

## Próximas Fases

### Fase 3 (Próxima): UI Development
- Implementar Sidebar con botones de categorías
- Implementar Content Panel con lista de items
- Agregar funcionalidad de clic para copiar
- Implementar búsqueda y filtrado
- Agregar animaciones

### Fase 4: Hotkeys y Tray Icon
- Implementar hotkeys globales (Ctrl+Shift+V)
- Agregar icono en system tray
- Implementar menú contextual

### Fase 5+: Personalización y Features Avanzadas
- Editor de categorías/items
- Temas dark/light
- Import/Export
- Configuración avanzada

## Comandos Útiles

### Tests
```bash
# Ejecutar tests de Fase 2
python test_phase2.py
```

### Aplicación
```bash
# Ejecutar aplicación
python main.py
```

### Git
```bash
# Ver commits
git log --oneline

# Ver estado
git status

# Ver cambios
git diff
```

## Troubleshooting

### Error: ModuleNotFoundError
Si obtienes un error de módulo no encontrado:
```bash
pip install -r requirements.txt
```

### Error: No se carga la configuración
Verifica que existan los archivos:
- `config.json`
- `default_categories.json`

### Ventana no aparece
- Verifica que tienes PyQt6 instalado correctamente
- Ejecuta `python test_phase2.py` para verificar el core

---

**Estado Actual**: Fase 2 Completa ✓
**Última Actualización**: 2025-10-15
