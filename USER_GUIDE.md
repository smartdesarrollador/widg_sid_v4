# Widget Sidebar - Guía de Usuario

**Version:** 3.0.0
**Fecha:** Octubre 2025

---

## Tabla de Contenidos

1. [Instalación](#instalación)
2. [Inicio Rápido](#inicio-rápido)
3. [Interfaz Principal](#interfaz-principal)
4. [Categorías Predefinidas](#categorías-predefinidas)
5. [Uso Básico](#uso-básico)
6. [Búsqueda](#búsqueda)
7. [Hotkeys (Atajos de Teclado)](#hotkeys-atajos-de-teclado)
8. [Configuración](#configuración)
9. [Personalización](#personalización)
10. [Tips y Trucos](#tips-y-trucos)
11. [Troubleshooting](#troubleshooting)

---

## Instalación

### Opción 1: Ejecutable Portable (Recomendado)

**Requisitos:**
- Windows 10/11
- No requiere Python ni dependencias

**Pasos:**
1. Descarga `WidgetSidebar.exe` desde la carpeta `dist/`
2. Coloca el ejecutable en cualquier carpeta de tu preferencia
3. Ejecuta `WidgetSidebar.exe`
4. ¡Listo! La aplicación está corriendo

**Nota:** El widget es portable, puedes copiar la carpeta completa a otro PC sin problemas.

### Opción 2: Desde Código Fuente

**Requisitos:**
- Python 3.10 o superior
- pip (gestor de paquetes de Python)

**Pasos:**
1. Clona o descarga el repositorio
2. Abre terminal en la carpeta del proyecto
3. Crea entorno virtual:
   ```bash
   python -m venv venv
   ```
4. Activa el entorno virtual:
   ```bash
   .\venv\Scripts\activate
   ```
5. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
6. Ejecuta la aplicación:
   ```bash
   python main.py
   ```

---

## Inicio Rápido

**5 pasos para empezar:**

1. **Inicia la aplicación** → Aparece una barra vertical en el lado derecho de tu pantalla
2. **Click en una categoría** (ej: Git, CMD) → El panel se expande mostrando comandos
3. **Click en un comando** → Se copia automáticamente al portapapeles
4. **Pega donde necesites** → `Ctrl+V` para usar el comando copiado
5. **Hotkey global** → Presiona `Ctrl+Shift+V` para mostrar/ocultar el widget desde cualquier app

---

## Interfaz Principal

El Widget Sidebar tiene 3 componentes principales:

### 1. Barra Lateral (Sidebar)

```
┌────────┐
│   WS   │  ← Logo/Título
├────────┤
│  Git   │  ← Botón de categoría
├────────┤
│  CMD   │
├────────┤
│ Docker │
├────────┤
│   ...  │
├────────┤
│   ⚙    │  ← Configuración
└────────┘
```

- **Ancho:** 70px (configurable)
- **Posición:** Borde derecho de la pantalla
- **Always on top:** Siempre visible sobre otras ventanas
- **Draggable:** Arrastra con el mouse para mover

### 2. Panel de Contenido (Content Panel)

```
┌─────────────────────────────┐
│  Git                        │  ← Nombre de categoría
├─────────────────────────────┤
│  🔍 Buscar items...    ×   │  ← Búsqueda
├─────────────────────────────┤
│  git status                 │  ← Item clickeable
│  git add .                  │
│  git commit -m ""           │
│  git push                   │
│  ...                        │
└─────────────────────────────┘
```

- **Ancho:** 300px (configurable)
- **Expandible:** Se muestra al seleccionar categoría
- **Scrolleable:** Lista de items con scroll
- **Búsqueda:** Filtra items en tiempo real

### 3. System Tray Icon

- **Icono azul "WS"** en la bandeja del sistema
- **Click izquierdo:** Mostrar/ocultar ventana
- **Click derecho:** Menú contextual
  - Mostrar/Ocultar
  - Configuración
  - Salir

---

## Categorías Predefinidas

El widget incluye 8 categorías con comandos útiles:

### 1. 📦 Git (14 comandos)
Comandos Git más comunes:
- `git status` - Ver estado del repositorio
- `git add .` - Agregar todos los cambios
- `git commit -m "mensaje"` - Hacer commit
- `git push` - Subir cambios
- `git pull` - Descargar cambios
- Y más...

### 2. 💻 CMD (13 comandos)
Comandos de línea de comandos de Windows:
- `cd ..` - Subir un directorio
- `dir` - Listar archivos
- `cls` - Limpiar consola
- `ipconfig` - Configuración de red
- `tasklist` - Listar procesos
- Y más...

### 3. 🐋 Docker (16 comandos)
Comandos Docker para contenedores:
- `docker ps` - Ver contenedores activos
- `docker images` - Listar imágenes
- `docker build -t nombre .` - Construir imagen
- `docker run` - Ejecutar contenedor
- `docker-compose up` - Iniciar servicios
- Y más...

### 4. 🐍 Python (15 comandos)
Comandos Python y pip:
- `python --version` - Ver versión
- `pip install paquete` - Instalar paquete
- `pip list` - Listar paquetes
- `python -m venv venv` - Crear entorno virtual
- `pytest` - Ejecutar tests
- Y más...

### 5. 📦 NPM (12 comandos)
Comandos NPM y Node.js:
- `npm init` - Inicializar proyecto
- `npm install` - Instalar dependencias
- `npm start` - Iniciar proyecto
- `npm run build` - Compilar proyecto
- `npm test` - Ejecutar tests
- Y más...

### 6. 🌐 URLs (9 links)
URLs útiles para desarrollo:
- GitHub
- Stack Overflow
- MDN Web Docs
- Python Docs
- Docker Hub
- Y más...

### 7. 📝 Snippets (7 snippets)
Fragmentos de código comunes:
- Try-catch block
- For loop
- Function template
- Class template
- Y más...

### 8. ⚙ Configuración (0 items)
Categoría reservada para configuraciones personalizadas.

---

## Uso Básico

### Copiar un Comando

1. **Click en categoría** (ej: Git)
   - El panel se expande con animación suave (250ms)
   - Se muestran todos los comandos de Git

2. **Click en un comando** (ej: "git status")
   - El botón flashea en azul (feedback visual)
   - El comando se copia automáticamente al portapapeles
   - Duración del flash: 500ms

3. **Usa el comando**
   - Ve a tu terminal, editor o donde necesites
   - Presiona `Ctrl+V` para pegar
   - ¡Listo!

### Navegar Entre Categorías

- **Click en otra categoría** → Panel cambia de contenido inmediatamente
- **Solo una categoría activa** → La anterior se desactiva automáticamente
- **Borde azul izquierdo** → Indica categoría activa

### Cerrar el Panel

- **Click en otra parte** → El panel permanece abierto
- **Esc** → Cierra el panel (próximamente)
- **Cerrar ventana (X)** → Minimiza a system tray (no cierra la app)

---

## Búsqueda

### Usar la Búsqueda

1. **Abre una categoría** (ej: Docker)
2. **Click en el SearchBar** (o automáticamente tiene foco)
3. **Escribe tu búsqueda** (ej: "build")
4. **Espera 300ms** (debouncing automático)
5. **Items filtrados** → Solo aparecen los que coinciden

### Características de Búsqueda

- **Case-insensitive:** Busca sin distinguir mayúsculas/minúsculas
- **Busca en:** Label y content de los items
- **Debouncing:** 300ms de delay para mejor performance
- **Tiempo real:** Actualización instantánea
- **Botón clear (×):** Limpia la búsqueda rápidamente

### Ejemplos de Búsqueda

**Categoría Git:**
- Buscar "commit" → Muestra: git commit, git commit --amend
- Buscar "push" → Muestra: git push, git push origin
- Buscar "" (vacío) → Muestra todos los items

**Categoría Docker:**
- Buscar "ps" → Muestra: docker ps, docker ps -a
- Buscar "build" → Muestra: docker build, docker-compose build

---

## Hotkeys (Atajos de Teclado)

### Hotkeys Globales

**Funcionan desde cualquier aplicación:**

#### `Ctrl+Shift+V` - Toggle Ventana
- **Función:** Mostrar/ocultar el widget
- **Uso:** Presiona desde cualquier app (navegador, editor, etc.)
- **Estado inicial:** Widget visible
- **Primer press:** Oculta el widget
- **Segundo press:** Muestra el widget
- **Útil para:** Acceso rápido sin usar el mouse

#### `Ctrl+Shift+1` - Categoría 1 (Próximamente)
- **Función:** Abrir directamente la primera categoría (Git)
- **Estado:** En desarrollo

#### `Ctrl+Shift+2` - Categoría 2 (Próximamente)
- **Función:** Abrir directamente la segunda categoría (CMD)
- **Estado:** En desarrollo

#### `Ctrl+Shift+3` - Categoría 3 (Próximamente)
- **Función:** Abrir directamente la tercera categoría (Docker)
- **Estado:** En desarrollo

### Hotkeys Locales

**Solo funcionan cuando el widget tiene foco:**

#### `Esc` - Cerrar Panel (Próximamente)
- **Función:** Cerrar el panel expandido
- **Estado:** En desarrollo

---

## Configuración

Acceso a la configuración:
- **Opción 1:** Click en botón ⚙ (parte inferior del sidebar)
- **Opción 2:** Right-click en tray icon → "Configuración"

### Ventana de Configuración

**Tamaño:** 600×650px
**Tipo:** Modal (bloquea interacción con ventana principal)
**Tabs:** 4 pestañas

---

### Tab 1: Categorías

**Gestiona tus categorías e items**

#### Panel Izquierdo - Categorías (200px)

**Botones:**
- **[+]** Agregar categoría
  - Click → Aparece diálogo
  - Escribe nombre → OK
  - Categoría agregada al final

- **[-]** Eliminar categoría
  - Selecciona categoría → Click [-]
  - Confirmación → "¿Eliminar categoría y todos sus items?"
  - Sí → Categoría eliminada

- **Reordenar** (Drag & Drop)
  - Click y mantén en categoría
  - Arrastra arriba/abajo
  - Suelta en nueva posición

**Contador de items:**
- Cada categoría muestra: `Nombre (X)` donde X = cantidad de items

#### Panel Derecho - Items (280px+)

**Botones:**
- **[+]** Agregar item
  - Click → Abre ItemEditorDialog
  - Llena formulario → Guardar
  - Item agregado a categoría actual

- **[✎]** Editar item
  - Selecciona item → Click [✎]
  - O: Double-click en item
  - Modifica campos → Guardar
  - Item actualizado

- **[-]** Eliminar item
  - Selecciona item → Click [-]
  - Confirmación → "¿Eliminar item 'nombre'?"
  - Sí → Item eliminado

#### ItemEditorDialog

**Campos:**

1. **Label*** (requerido)
   - Nombre del item
   - Ejemplo: "Git Status"
   - Aparece en la lista de items

2. **Tipo**
   - TEXT (default) - Texto simple
   - URL - Link web (valida formato http://)
   - CODE - Código fuente
   - PATH - Ruta de archivo

3. **Content*** (requerido)
   - Contenido a copiar
   - Multilínea (QTextEdit)
   - Ejemplo: `git status`
   - Se copia al portapapeles al hacer click

4. **Tags** (opcional)
   - Separados por comas
   - Ejemplo: `git, version control, status`
   - Para futuras búsquedas avanzadas

**Validación:**
- Label y Content no pueden estar vacíos
- Si Tipo = URL, valida formato http:// o https://
- Mensaje de error si validación falla

---

### Tab 2: Apariencia

**Personaliza la apariencia del widget**

#### Grupo: Tema

- **Theme selector**
  - Dark (activo) ✓
  - Light (próximamente) ⏳

#### Grupo: Ventana

- **Opacidad**
  - Slider: 50% a 100%
  - Default: 95%
  - Ejemplo: 80% → Ventana semi-transparente
  - Útil para: Ver lo que hay detrás del widget

- **Ancho sidebar**
  - SpinBox: 60px a 100px
  - Default: 70px
  - Ejemplo: 80px → Botones más anchos
  - Mínimo: 60px para que quepa texto

- **Ancho panel**
  - SpinBox: 250px a 400px
  - Default: 300px
  - Ejemplo: 350px → Más espacio para items largos
  - Afecta el ancho total cuando panel está abierto

#### Grupo: Animaciones

- **Velocidad**
  - SpinBox: 100ms a 500ms
  - Default: 250ms
  - Ejemplo: 150ms → Animaciones más rápidas
  - 500ms → Animaciones más lentas y suaves

**Nota:** Algunos cambios requieren reiniciar la aplicación.

---

### Tab 3: Hotkeys

**Visualiza y configura atajos de teclado**

#### Tabla de Hotkeys

| Acción | Combinación | Cambiar |
|--------|-------------|---------|
| Toggle ventana | Ctrl+Shift+V | [Cambiar] ✓ |
| Categoría 1 | Ctrl+Shift+1 | [Cambiar] ⏳ |
| Categoría 2 | Ctrl+Shift+2 | [Cambiar] ⏳ |
| Categoría 3 | Ctrl+Shift+3 | [Cambiar] ⏳ |

**Estado actual:**
- ✓ = Funcional y configurable
- ⏳ = Próximamente

**Botón [Cambiar]:**
- Click → Muestra mensaje informativo
- Funcionalidad de captura de teclas en desarrollo
- Por ahora, editar manualmente en config.json

**Notas importantes:**
- Los hotkeys son **globales** (funcionan en toda la PC)
- Cambios requieren **reiniciar la aplicación**
- Evita conflictos con atajos del sistema

---

### Tab 4: General

**Opciones generales de comportamiento**

#### Grupo: Comportamiento

- **☑ Minimizar a tray al cerrar ventana**
  - Default: Activado ✓
  - Si activo: Click en X → Minimiza a tray
  - Si inactivo: Click en X → Cierra la aplicación
  - Recomendado: Activado para acceso rápido

- **☑ Mantener ventana siempre visible**
  - Default: Activado ✓
  - Si activo: Ventana siempre encima (always-on-top)
  - Si inactivo: Ventana puede quedar detrás de otras
  - Recomendado: Activado para sidebar

- **☐ Iniciar con Windows**
  - Default: Desactivado
  - Estado: Próximamente ⏳
  - Función: Auto-iniciar al arrancar Windows

#### Grupo: Portapapeles

- **Máximo items historial**
  - SpinBox: 10 a 50 items
  - Default: 20 items
  - Función: Cuántos items recordar en historial
  - Mayor número = más memoria usada

#### Grupo: Import/Export

- **[Exportar...] button**
  - Click → Abre QFileDialog
  - Selecciona ubicación y nombre
  - Formato: JSON
  - Contenido: Config + Categories completas
  - Uso: Backup o transferir a otro PC

- **[Importar...] button**
  - Click → Abre QFileDialog
  - Selecciona archivo JSON previamente exportado
  - Validación automática
  - Mensaje: "Reinicie la aplicación"
  - Uso: Restaurar backup o importar de otro PC

#### Grupo: Acerca de

Información de la aplicación:
- **Nombre:** Widget Sidebar
- **Versión:** 3.0.0
- **Framework:** PyQt6
- **Architecture:** MVC
- **Descripción:** Gestor avanzado de portapapeles

---

### Guardar Cambios

**3 botones en la parte inferior:**

#### [Cancelar]
- Cierra ventana sin guardar
- Todos los cambios se pierden
- Útil si cambias de opinión

#### [Aplicar]
- Guarda cambios en config.json
- Ventana permanece abierta
- Puedes seguir editando
- Muestra mensaje: "Configuración aplicada"
- Algunos cambios se aplican inmediatamente:
  - Opacity (opacidad de ventana)
  - Sidebar recarga categorías

#### [Guardar]
- Guarda cambios en config.json
- Cierra la ventana automáticamente
- Es igual a [Aplicar] + [Cancelar]
- Cambios aplicados inmediatamente cuando es posible

---

## Personalización

### Agregar una Categoría Personalizada

**Ejemplo: Crear categoría "Database"**

1. Abre Configuración (⚙)
2. Tab "Categorías"
3. Click [+] (agregar categoría)
4. Escribe: "Database"
5. Click OK
6. Nueva categoría "Database (0)" aparece en la lista

### Agregar Items a tu Categoría

**Ejemplo: Agregar comandos MySQL**

1. Selecciona categoría "Database"
2. Click [+] (agregar item)
3. Llena formulario:
   - **Label:** MySQL Connect
   - **Tipo:** CODE
   - **Content:** `mysql -u root -p`
   - **Tags:** mysql, database, connect
4. Click "Guardar"
5. Repite para más comandos:
   - MySQL Show Databases: `SHOW DATABASES;`
   - MySQL Use Database: `USE nombre_db;`
   - MySQL Show Tables: `SHOW TABLES;`

### Editar Items Existentes

**Ejemplo: Mejorar comando de Git**

1. Selecciona categoría "Git"
2. Double-click en "git commit"
3. Modifica content:
   - Antes: `git commit -m ""`
   - Después: `git commit -m "feat: "`
4. Click "Guardar"
5. Ahora al copiar incluye "feat:" al inicio

### Eliminar Items Innecesarios

**Ejemplo: Limpiar categoría CMD**

1. Selecciona categoría "CMD"
2. Selecciona item que no usas (ej: "tasklist")
3. Click [-] (eliminar)
4. Confirma "Sí"
5. Item eliminado

### Export/Import de Configuración

#### Exportar (Backup)

**Uso: Guardar tu configuración personalizada**

1. Configuración → Tab "General"
2. Click "Exportar..."
3. Selecciona ubicación (ej: Desktop)
4. Nombre: `widget_backup_2025-10-15.json`
5. Click "Guardar"
6. Archivo JSON creado con:
   - Todas las configuraciones
   - Todas las categorías
   - Todos los items

#### Importar (Restaurar)

**Uso: Restaurar backup o importar de otro PC**

1. Configuración → Tab "General"
2. Click "Importar..."
3. Selecciona archivo JSON
4. Confirma importación
5. Mensaje: "Configuración importada. Reinicie la aplicación"
6. Cierra y vuelve a abrir el widget
7. Todo restaurado

**Formato del JSON:**
```json
{
  "config": {
    "settings": { ... },
    ...
  },
  "categories": [
    {
      "id": "git_commands",
      "name": "Git",
      "items": [ ... ]
    },
    ...
  ]
}
```

---

## Tips y Trucos

### 🚀 Productividad

1. **Hotkey Maestro**
   - Memoriza `Ctrl+Shift+V` para acceso instantáneo
   - No necesitas alt-tab al widget
   - Trabaja en cualquier app y presiona el hotkey

2. **Búsqueda Rápida**
   - El SearchBar tiene foco automático al abrir categoría
   - Empieza a escribir inmediatamente
   - Usa clear (×) para limpiar y ver todo

3. **Categorías Favoritas**
   - Pon tus categorías más usadas arriba
   - Arrastra en modo edición para reordenar
   - Acceso más rápido a comandos frecuentes

4. **Items Descriptivos**
   - Usa labels claros: "Git: Push to origin" mejor que "push"
   - Tags ayudan a encontrar items: `git, remote, push`
   - Content puede tener comentarios inline

### 🎨 Personalización

5. **Opacidad Perfecta**
   - 95%: Default, buena visibilidad
   - 85%: Ver código detrás del widget
   - 100%: Opaco, sin distracciones

6. **Ancho Ideal**
   - Sidebar 70px: Textos cortos pero legibles
   - Panel 300px: Suficiente para la mayoría
   - Panel 350px: Para comandos largos de Docker

7. **Animaciones**
   - 250ms: Default, balance perfecto
   - 150ms: Más rápido, para usuarios expertos
   - 400ms: Más suave, mejor en PCs lentos

### 💾 Backup

8. **Exporta Regularmente**
   - Haz backup mensual de tu config
   - Nombra con fecha: `widget_2025-10.json`
   - Guarda en cloud (Dropbox, Drive, etc.)

9. **Configs por Proyecto**
   - Export config específica para proyectos
   - `widget_frontend.json` - Comandos de React
   - `widget_backend.json` - Comandos de Python/Django
   - Importa según proyecto actual

### 🔧 Optimización

10. **Limpieza de Items**
    - Revisa categorías cada mes
    - Elimina comandos que no usas
    - Menos items = búsqueda más rápida

11. **Tags Estratégicos**
    - Usa tags consistentes
    - Ejemplo: `git, remote` para todos los comandos remote
    - Facilita búsquedas futuras

12. **Historial Óptimo**
    - 20 items: Default, suficiente para mayoría
    - 30 items: Si copias muchos comandos diferentes
    - 10 items: Si solo usas comandos frecuentes

---

## Troubleshooting

### Problemas Comunes

#### 1. El widget no inicia

**Síntomas:** Double-click en .exe, no pasa nada

**Soluciones:**
- Verifica que no esté ya corriendo (busca en System Tray)
- Revisa Task Manager si hay proceso "WidgetSidebar.exe"
- Ejecuta como Administrador (right-click → "Run as administrator")
- Verifica antivirus no esté bloqueando
- Comprueba logs en la carpeta del ejecutable

#### 2. Hotkeys no funcionan

**Síntomas:** `Ctrl+Shift+V` no hace nada

**Soluciones:**
- Verifica otra app no esté usando el mismo hotkey
- Cierra apps que capturan teclado (gaming overlays, etc.)
- Reinicia el widget
- Cambia el hotkey en configuración
- Verifica permisos (ejecuta como Admin)

#### 3. Items no se copian al portapapeles

**Síntomas:** Click en item, flashea azul, pero no se copia

**Soluciones:**
- Intenta pegar en Notepad para verificar
- Verifica gestor de portapapeles no esté interfiriendo
- Reinicia el widget
- Revisa que el item tenga content (no vacío)

#### 4. Ventana desaparece

**Síntomas:** Widget no visible en pantalla

**Soluciones:**
- Presiona `Ctrl+Shift+V` (puede estar oculto)
- Busca ícono en System Tray → Click izquierdo
- Right-click en tray → "Mostrar/Ocultar"
- Si cambió resolución, puede estar fuera de pantalla
  - Cierra y vuelve a abrir

#### 5. Búsqueda no filtra

**Síntomas:** Escribes en SearchBar, items no se filtran

**Soluciones:**
- Espera 300ms (debouncing automático)
- Verifica que la categoría tenga items
- Prueba con query más simple (1-2 caracteres)
- Click en clear (×) y vuelve a intentar
- Reinicia el widget

#### 6. Configuración no se guarda

**Síntomas:** Cambios en config no persisten

**Soluciones:**
- Verifica que clickeaste "Guardar" o "Aplicar"
- Revisa permisos de escritura en carpeta
- Busca archivo `config.json` en carpeta del .exe
- Verifica que no sea read-only
- Ejecuta como Administrador

#### 7. System Tray icon no aparece

**Síntomas:** No hay ícono WS en bandeja del sistema

**Soluciones:**
- Verifica "Show hidden icons" (flecha en tray)
- Reinicia el widget
- Revisa configuración de Windows (Settings → Taskbar → Tray)
- Algunos antivirus bloquean tray icons

#### 8. Animaciones lentas o entrecortadas

**Síntomas:** Panel se expande con lag

**Soluciones:**
- Reduce velocidad de animación (Settings → Apariencia → 150ms)
- Cierra apps pesadas
- Actualiza drivers gráficos
- Verifica recursos del PC (RAM, CPU)
- Reduce opacidad a 90%

#### 9. Widget en pantalla incorrecta (multi-monitor)

**Síntomas:** Widget aparece en monitor secundario

**Soluciones:**
- Arrastra el widget al monitor deseado
- Configuración se guarda automáticamente
- Cierra y vuelve a abrir, debe recordar posición
- Si persiste, elimina `config.json` y reinicia

#### 10. Fuentes o textos borrosos

**Síntomas:** Texto difícil de leer

**Soluciones:**
- Ajusta DPI scaling de Windows
- Verifica resolución de pantalla
- Aumenta ancho de sidebar (Settings → Apariencia)
- Ajusta opacidad a 100%
- Reinicia el widget después de cambios

### Reportar Bugs

Si encuentras un problema no listado aquí:

1. Verifica que sea reproducible
2. Anota pasos exactos para reproducir
3. Captura screenshot si es problema visual
4. Revisa archivo de logs (si existe)
5. Crea issue en GitHub con:
   - Descripción del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshot/video si aplica
   - Windows version
   - Widget Sidebar version

---

## Recursos Adicionales

### Documentación

- **README.md** - Información general del proyecto
- **PHASE5_SUMMARY.md** - Documentación técnica de configuración
- **PHASE4_SUMMARY.md** - Documentación de hotkeys y tray
- **PHASE3_SUMMARY.md** - Documentación de UI

### Soporte

- **GitHub Issues** - Reporta bugs o solicita features
- **GitHub Discussions** - Preguntas y discusiones
- **Email** - Contacto directo para soporte

### Contribuir

El proyecto es open source. Contribuciones bienvenidas:
- Fork del repositorio
- Crea branch para tu feature
- Commit con mensajes claros
- Pull request con descripción detallada

---

## Changelog

### Version 3.0.0 (2025-10-15)

**Fase 5 - Settings & Configuration:**
- ✅ Ventana de configuración completa con 4 tabs
- ✅ Editor de categorías e items con CRUD
- ✅ Configuración de apariencia (tema, opacidad, dimensiones)
- ✅ Configuración de hotkeys (visualización)
- ✅ Configuración general (comportamiento, export/import)
- ✅ Persistencia de configuración en config.json

### Version 2.0.0 (2025-10-14)

**Fase 4 - Hotkeys, Tray & Search:**
- ✅ Hotkey global Ctrl+Shift+V para toggle ventana
- ✅ System tray icon con menú contextual
- ✅ SearchBar con debouncing (300ms)
- ✅ SearchEngine para filtrado case-insensitive
- ✅ Minimize to tray (no cierra app)

### Version 1.0.0 (2025-10-13)

**Fase 3 - UI Complete:**
- ✅ Sidebar con 8 categorías
- ✅ ContentPanel expandible con animaciones
- ✅ Feedback visual al copiar (flash azul)
- ✅ Dark theme profesional

---

## Licencia

MIT License - Libre uso, modificación y distribución

---

## Créditos

**Desarrollado con:**
- Python 3.10+
- PyQt6 (GUI Framework)
- pyperclip (Clipboard management)
- pynput (Global hotkeys)

**Compilado con:**
- PyInstaller (Standalone executable)

---

**¡Disfruta usando Widget Sidebar!**

Para más información, visita el repositorio en GitHub.
