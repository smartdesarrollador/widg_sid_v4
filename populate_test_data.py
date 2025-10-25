"""Script para poblar la base de datos con datos de prueba"""
import sqlite3
import random
from datetime import datetime, timedelta
import sys
import io

# Configurar stdout para UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = "widget_sidebar.db"

# Datos de prueba
categories_data = [
    {"name": "Git", "icon": "🔧", "order": 1},
    {"name": "Docker", "icon": "🐳", "order": 2},
    {"name": "Python", "icon": "🐍", "order": 3},
    {"name": "JavaScript", "icon": "📜", "order": 4},
    {"name": "Linux", "icon": "🐧", "order": 5},
    {"name": "URLs", "icon": "🌐", "order": 6},
    {"name": "Rutas", "icon": "📁", "order": 7},
    {"name": "Credenciales", "icon": "🔐", "order": 8},
]

items_data = {
    "Git": [
        {"label": "git init", "content": "git init", "type": "CODE", "tags": "init,nuevo", "description": "Inicializar nuevo repositorio"},
        {"label": "git clone", "content": "git clone <url>", "type": "CODE", "tags": "clonar,descargar", "description": "Clonar repositorio remoto"},
        {"label": "git status", "content": "git status", "type": "CODE", "tags": "estado", "description": "Ver estado del repositorio"},
        {"label": "git add all", "content": "git add .", "type": "CODE", "tags": "agregar,staging", "description": "Agregar todos los cambios"},
        {"label": "git commit", "content": 'git commit -m "mensaje"', "type": "CODE", "tags": "commit,guardar", "description": "Crear commit con mensaje"},
        {"label": "git push", "content": "git push origin main", "type": "CODE", "tags": "subir,enviar", "description": "Enviar cambios al remoto"},
        {"label": "git pull", "content": "git pull origin main", "type": "CODE", "tags": "descargar,actualizar", "description": "Traer cambios del remoto"},
        {"label": "git branch", "content": "git branch <nombre>", "type": "CODE", "tags": "rama,branch", "description": "Crear nueva rama"},
        {"label": "git checkout", "content": "git checkout <rama>", "type": "CODE", "tags": "cambiar,rama", "description": "Cambiar de rama"},
        {"label": "git merge", "content": "git merge <rama>", "type": "CODE", "tags": "fusionar,merge", "description": "Fusionar ramas"},
        {"label": "git log", "content": "git log --oneline --graph", "type": "CODE", "tags": "historial,log", "description": "Ver historial de commits"},
        {"label": "git reset", "content": "git reset --hard HEAD~1", "type": "CODE", "tags": "deshacer,reset", "description": "Deshacer último commit"},
    ],
    "Docker": [
        {"label": "docker ps", "content": "docker ps -a", "type": "CODE", "tags": "listar,contenedores", "description": "Listar todos los contenedores"},
        {"label": "docker build", "content": "docker build -t <nombre> .", "type": "CODE", "tags": "construir,imagen", "description": "Construir imagen Docker"},
        {"label": "docker run", "content": "docker run -d -p 8080:80 <imagen>", "type": "CODE", "tags": "ejecutar,run", "description": "Ejecutar contenedor"},
        {"label": "docker stop", "content": "docker stop <container_id>", "type": "CODE", "tags": "detener,stop", "description": "Detener contenedor"},
        {"label": "docker rm", "content": "docker rm <container_id>", "type": "CODE", "tags": "eliminar,remove", "description": "Eliminar contenedor"},
        {"label": "docker images", "content": "docker images", "type": "CODE", "tags": "listar,imagenes", "description": "Listar imágenes"},
        {"label": "docker logs", "content": "docker logs -f <container>", "type": "CODE", "tags": "logs,registros", "description": "Ver logs del contenedor"},
        {"label": "docker exec", "content": "docker exec -it <container> bash", "type": "CODE", "tags": "entrar,bash", "description": "Ejecutar bash en contenedor"},
        {"label": "docker compose up", "content": "docker-compose up -d", "type": "CODE", "tags": "compose,levantar", "description": "Levantar servicios con compose"},
        {"label": "docker compose down", "content": "docker-compose down", "type": "CODE", "tags": "compose,bajar", "description": "Detener servicios compose"},
    ],
    "Python": [
        {"label": "crear virtualenv", "content": "python -m venv venv", "type": "CODE", "tags": "virtualenv,entorno", "description": "Crear entorno virtual"},
        {"label": "activar venv (Win)", "content": "venv\\Scripts\\activate", "type": "CODE", "tags": "activar,windows", "description": "Activar virtualenv en Windows"},
        {"label": "activar venv (Linux)", "content": "source venv/bin/activate", "type": "CODE", "tags": "activar,linux", "description": "Activar virtualenv en Linux"},
        {"label": "pip install", "content": "pip install <paquete>", "type": "CODE", "tags": "instalar,pip", "description": "Instalar paquete"},
        {"label": "pip freeze", "content": "pip freeze > requirements.txt", "type": "CODE", "tags": "requirements,guardar", "description": "Exportar dependencias"},
        {"label": "pip install -r", "content": "pip install -r requirements.txt", "type": "CODE", "tags": "instalar,requirements", "description": "Instalar desde requirements"},
        {"label": "python server", "content": "python -m http.server 8000", "type": "CODE", "tags": "servidor,http", "description": "Servidor HTTP simple"},
        {"label": "pytest", "content": "pytest -v", "type": "CODE", "tags": "test,pruebas", "description": "Ejecutar pruebas"},
        {"label": "black format", "content": "black .", "type": "CODE", "tags": "formatear,black", "description": "Formatear código con Black"},
        {"label": "pylint", "content": "pylint src/", "type": "CODE", "tags": "lint,analisis", "description": "Analizar código con Pylint"},
    ],
    "JavaScript": [
        {"label": "npm init", "content": "npm init -y", "type": "CODE", "tags": "iniciar,npm", "description": "Inicializar proyecto npm"},
        {"label": "npm install", "content": "npm install <paquete>", "type": "CODE", "tags": "instalar,npm", "description": "Instalar paquete"},
        {"label": "npm install -D", "content": "npm install -D <paquete>", "type": "CODE", "tags": "dev,instalar", "description": "Instalar dependencia de desarrollo"},
        {"label": "npm start", "content": "npm start", "type": "CODE", "tags": "iniciar,start", "description": "Iniciar aplicación"},
        {"label": "npm run build", "content": "npm run build", "type": "CODE", "tags": "compilar,build", "description": "Compilar para producción"},
        {"label": "npm test", "content": "npm test", "type": "CODE", "tags": "test,pruebas", "description": "Ejecutar pruebas"},
        {"label": "npx create-react-app", "content": "npx create-react-app <nombre>", "type": "CODE", "tags": "react,crear", "description": "Crear app React"},
        {"label": "node version", "content": "node --version", "type": "CODE", "tags": "version,node", "description": "Ver versión de Node"},
        {"label": "npm update", "content": "npm update", "type": "CODE", "tags": "actualizar,update", "description": "Actualizar paquetes"},
    ],
    "Linux": [
        {"label": "ls -la", "content": "ls -la", "type": "CODE", "tags": "listar,archivos", "description": "Listar archivos detallado"},
        {"label": "chmod 755", "content": "chmod 755 <archivo>", "type": "CODE", "tags": "permisos,chmod", "description": "Cambiar permisos de archivo"},
        {"label": "chown", "content": "chown user:group <archivo>", "type": "CODE", "tags": "propietario,chown", "description": "Cambiar propietario"},
        {"label": "grep buscar", "content": "grep -r 'texto' .", "type": "CODE", "tags": "buscar,grep", "description": "Buscar texto en archivos"},
        {"label": "find archivos", "content": "find . -name '*.py'", "type": "CODE", "tags": "buscar,find", "description": "Buscar archivos por nombre"},
        {"label": "tar comprimir", "content": "tar -czf archivo.tar.gz carpeta/", "type": "CODE", "tags": "comprimir,tar", "description": "Comprimir carpeta"},
        {"label": "tar descomprimir", "content": "tar -xzf archivo.tar.gz", "type": "CODE", "tags": "descomprimir,tar", "description": "Descomprimir archivo"},
        {"label": "df -h", "content": "df -h", "type": "CODE", "tags": "disco,espacio", "description": "Ver espacio en disco"},
        {"label": "du -sh", "content": "du -sh *", "type": "CODE", "tags": "tamaño,carpeta", "description": "Ver tamaño de carpetas"},
        {"label": "ps aux", "content": "ps aux | grep <proceso>", "type": "CODE", "tags": "procesos,ps", "description": "Buscar procesos"},
        {"label": "kill proceso", "content": "kill -9 <PID>", "type": "CODE", "tags": "matar,kill", "description": "Terminar proceso"},
        {"label": "netstat", "content": "netstat -tulpn", "type": "CODE", "tags": "puertos,red", "description": "Ver puertos en uso"},
    ],
    "URLs": [
        {"label": "GitHub", "content": "https://github.com", "type": "URL", "tags": "repositorio,codigo", "description": "Plataforma de repositorios"},
        {"label": "Stack Overflow", "content": "https://stackoverflow.com", "type": "URL", "tags": "ayuda,preguntas", "description": "Comunidad de programadores"},
        {"label": "MDN Web Docs", "content": "https://developer.mozilla.org", "type": "URL", "tags": "documentacion,web", "description": "Documentación web"},
        {"label": "Python Docs", "content": "https://docs.python.org", "type": "URL", "tags": "python,documentacion", "description": "Documentación oficial Python"},
        {"label": "Docker Hub", "content": "https://hub.docker.com", "type": "URL", "tags": "docker,imagenes", "description": "Repositorio de imágenes Docker"},
        {"label": "npm Registry", "content": "https://www.npmjs.com", "type": "URL", "tags": "npm,paquetes", "description": "Registro de paquetes npm"},
        {"label": "RegEx101", "content": "https://regex101.com", "type": "URL", "tags": "regex,testing", "description": "Tester de expresiones regulares"},
        {"label": "Can I Use", "content": "https://caniuse.com", "type": "URL", "tags": "compatibilidad,web", "description": "Compatibilidad de navegadores"},
    ],
    "Rutas": [
        {"label": "Proyectos Python", "content": "C:\\Users\\ASUS\\Desktop\\proyectos_python", "type": "PATH", "tags": "proyectos", "description": "Carpeta de proyectos Python"},
        {"label": "Desktop", "content": "C:\\Users\\ASUS\\Desktop", "type": "PATH", "tags": "escritorio", "description": "Escritorio de Windows"},
        {"label": "Documents", "content": "C:\\Users\\ASUS\\Documents", "type": "PATH", "tags": "documentos", "description": "Carpeta de documentos"},
        {"label": "Downloads", "content": "C:\\Users\\ASUS\\Downloads", "type": "PATH", "tags": "descargas", "description": "Carpeta de descargas"},
    ],
    "Credenciales": [
        {"label": "DB Password", "content": "mySecretPass123!", "type": "TEXT", "is_sensitive": True, "tags": "password,database", "description": "Password de base de datos"},
        {"label": "API Key", "content": "sk-1234567890abcdef", "type": "TEXT", "is_sensitive": True, "tags": "api,key", "description": "Clave API de producción"},
        {"label": "SSH Key", "content": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...", "type": "TEXT", "is_sensitive": True, "tags": "ssh,key", "description": "Clave SSH privada"},
    ],
}

def populate_database():
    """Poblar la base de datos con datos de prueba"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("="*70)
        print("POBLANDO BASE DE DATOS CON DATOS DE PRUEBA")
        print("="*70)

        # Limpiar datos existentes (opcional)
        print("\nLimpiando datos existentes...")
        cursor.execute("DELETE FROM items")
        cursor.execute("DELETE FROM categories")
        conn.commit()
        print("OK: Tablas limpiadas")

        # Insertar categorías
        print("\nInsertando categorías...")
        category_ids = {}

        for cat_data in categories_data:
            cursor.execute("""
                INSERT INTO categories (name, icon, order_index)
                VALUES (?, ?, ?)
            """, (cat_data["name"], cat_data["icon"], cat_data["order"]))

            category_ids[cat_data["name"]] = cursor.lastrowid
            print(f"  + {cat_data['icon']} {cat_data['name']} (ID: {cursor.lastrowid})")

        conn.commit()
        print(f"\nOK: {len(category_ids)} categorías insertadas")

        # Insertar items
        print("\nInsertando items...")
        total_items = 0
        total_favorites = 0

        for category_name, items in items_data.items():
            if category_name not in category_ids:
                continue

            category_id = category_ids[category_name]
            print(f"\n  Categoría: {category_name}")

            for idx, item in enumerate(items, 1):
                # Determinar si será favorito (30% de probabilidad)
                is_favorite = random.random() < 0.3
                favorite_order = idx if is_favorite else 0

                # Generar use_count aleatorio
                use_count = random.randint(0, 100)

                # Generar fecha de último uso (últimos 30 días)
                days_ago = random.randint(0, 30)
                last_used = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")

                # Determinar badge basado en use_count
                if use_count > 50:
                    badge = "popular"
                elif use_count == 0:
                    badge = "nuevo"
                else:
                    badge = None

                cursor.execute("""
                    INSERT INTO items (
                        category_id, label, content, type, tags, description,
                        is_sensitive, is_favorite, favorite_order, use_count,
                        last_used, badge, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """, (
                    category_id,
                    item["label"],
                    item["content"],
                    item["type"],
                    item.get("tags", ""),
                    item.get("description", ""),
                    item.get("is_sensitive", False),
                    is_favorite,
                    favorite_order,
                    use_count,
                    last_used,
                    badge
                ))

                star = "⭐" if is_favorite else "  "
                fire = "🔥" if badge == "popular" else ""
                new = "🆕" if badge == "nuevo" else ""
                lock = "🔒" if item.get("is_sensitive") else ""

                print(f"    {star} {item['label']:<30} {fire}{new}{lock} (usos: {use_count})")

                total_items += 1
                if is_favorite:
                    total_favorites += 1

        conn.commit()
        print("\n" + "="*70)
        print(f"OK: {total_items} items insertados")
        print(f"OK: {total_favorites} items marcados como favoritos")
        print("="*70)

        # Verificar resultados
        print("\nVERIFICACION:")
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        print(f"  Total categorías: {cat_count}")

        cursor.execute("SELECT COUNT(*) FROM items")
        item_count = cursor.fetchone()[0]
        print(f"  Total items: {item_count}")

        cursor.execute("SELECT COUNT(*) FROM items WHERE is_favorite = 1")
        fav_count = cursor.fetchone()[0]
        print(f"  Total favoritos: {fav_count}")

        cursor.execute("SELECT COUNT(*) FROM items WHERE is_sensitive = 1")
        sens_count = cursor.fetchone()[0]
        print(f"  Total sensibles: {sens_count}")

        print("\n" + "="*70)
        print("POBLACION COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\nPuedes reiniciar la aplicacion para ver los datos nuevos.")

        conn.close()
        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    populate_database()
