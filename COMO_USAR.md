# 🚀 Cómo Usar Widget Sidebar v2.0

## ✅ ESTADO: LISTO PARA USAR

---

## 📋 Opciones Disponibles

### Opción 1: Ejecutar en Modo Desarrollo ⚡

**Uso inmediato** - Para probar el widget sin compilar:

```bash
cd widget_sidebar
python main.py
```

**Esto iniciará**:
- Widget Sidebar con interfaz completa
- Base de datos SQLite operativa
- Todas las categorías cargadas
- Sistema de clipboard funcional

**Ventajas**:
- ✅ Inicio instantáneo
- ✅ Fácil debugging
- ✅ No requiere compilación

---

### Opción 2: Compilar Ejecutable 📦

**Para distribución** - Crea un .exe independiente:

```bash
cd widget_sidebar
build.bat
```

**El script automáticamente**:
1. ✅ Crea backups de archivos JSON
2. ✅ Ejecuta migración a SQLite (si es necesario)
3. ✅ Limpia builds anteriores
4. ✅ Compila con PyInstaller
5. ✅ Copia database a dist/
6. ✅ Copia documentación (USER_GUIDE, README, LICENSE)
7. ✅ Crea paquete **WidgetSidebar_v2.0/**

**Resultado**:
```
WidgetSidebar_v2.0/
├── WidgetSidebar.exe    ← Ejecutable principal
├── widget_sidebar.db     ← Base de datos
├── USER_GUIDE.md         ← Guía de usuario
├── README.md             ← Documentación
└── LICENSE               ← Licencia
```

**Para ejecutar el .exe compilado**:
```bash
# Desde dist/
dist\WidgetSidebar.exe

# O desde el paquete
WidgetSidebar_v2.0\WidgetSidebar.exe
```

**Ventajas**:
- ✅ Ejecutable standalone
- ✅ No requiere Python instalado
- ✅ Fácil de distribuir
- ✅ Profesional

---

## 🎮 Cómo Usar el Widget

Una vez iniciado (modo desarrollo o .exe):

### 1. **Interfaz del Sidebar**
- Sidebar vertical a la izquierda (70px ancho)
- 8 botones de categorías con iconos:
  - 📁 Git
  - 💻 CMD
  - 🐳 Docker
  - 🐍 Python
  - 📦 NPM
  - 🔗 URLs
  - 📝 Snippets
  - ⚙️ Configuración

### 2. **Usar las Categorías**
1. **Clic en un botón** → Panel se expande (300px)
2. **Ver items** → Lista de comandos/snippets disponibles
3. **Clic en un item** → Se copia al portapapeles automáticamente
4. **Efecto visual** → Item parpadea en azul al copiar

### 3. **Funcionalidades**
- ✅ **Copia al portapapeles**: Clic en cualquier item
- ✅ **Panel expandible**: Se muestra/oculta automáticamente
- ✅ **Historial**: Tracking de items copiados
- ✅ **Base de datos**: Todo guardado en SQLite
- ✅ **Categorías personalizables**: 8 categorías pre-configuradas

---

## 🧪 Verificación Antes de Usar

Si quieres verificar que todo esté OK antes de ejecutar:

```bash
cd widget_sidebar
python test_complete_system.py
```

**Esto verifica**:
- ✅ Base de datos SQLite
- ✅ ConfigManager
- ✅ MainController
- ✅ Modelos de datos
- ✅ Migración y compatibilidad

---

## 📊 Contenido Incluido

### Categorías Pre-Configuradas

1. **Git** (14 items)
   - Comandos git esenciales
   - status, add, commit, push, pull, etc.

2. **CMD** (13 items)
   - Comandos de Windows
   - dir, cd, mkdir, ipconfig, ping, etc.

3. **Docker** (16 items)
   - Comandos Docker
   - ps, run, stop, exec, logs, etc.

4. **Python** (15 items)
   - Comandos Python
   - venv, pip, pytest, http.server, etc.

5. **NPM** (12 items)
   - Comandos NPM
   - init, install, run, build, etc.

6. **URLs** (9 items)
   - Links útiles
   - GitHub, Stack Overflow, Python Docs, etc.

7. **Snippets** (7 items)
   - Code snippets
   - Python y JavaScript templates

8. **Configuración** (0 items)
   - Categoría para futuras configuraciones

**Total**: 86 items listos para usar

---

## ⚙️ Configuración de Base de Datos

El widget usa **SQLite** con:
- **Archivo**: `widget_sidebar.db` (57 KB)
- **Tablas**: 4 (settings, categories, items, clipboard_history)
- **Ubicación**: Mismo directorio que el ejecutable

**Migración automática**:
- Si existe `config.json` → Se migra a SQLite
- Si existe `widget_sidebar.db` → Se usa directamente

---

## 🔧 Requisitos

### Para Modo Desarrollo
- ✅ Python 3.11+
- ✅ PyQt6 (instalado)
- ✅ pyperclip (instalado)
- ✅ pynput (instalado)

### Para Ejecutable Compilado
- ✅ Solo Windows (PyInstaller configurado para Windows)
- ❌ No requiere Python instalado
- ❌ No requiere dependencias

---

## 📝 Notas Importantes

### Backups Automáticos
Al compilar, se crean backups:
- `config.json.backup`
- `default_categories.json.backup`

### Base de Datos
- Se crea automáticamente si no existe
- Se incluye en el ejecutable
- Portabilidad: Puedes exportar/importar JSON

### Hotkey (Futuro)
- Actualmente configurado: `Ctrl+Shift+V`
- Funcionalidad de hotkey global en desarrollo

---

## ❓ Solución de Problemas

### El widget no inicia
```bash
# Verificar dependencias
python test_can_run.py

# Verificar base de datos
python test_db_integration.py
```

### Error de compilación
```bash
# Instalar PyInstaller
pip install pyinstaller

# Limpiar y recompilar
rmdir /s /q build dist
build.bat
```

### Base de datos corrupta
```bash
# Re-crear desde JSON
del widget_sidebar.db
python run_migration.py
```

---

## 🎉 ¡Listo para Usar!

**Elige tu opción**:

### 🚀 Desarrollo (Recomendado para pruebas)
```bash
python main.py
```

### 📦 Ejecutable (Recomendado para distribución)
```bash
build.bat
```

**El widget está 100% funcional y listo para producción!** ✨
