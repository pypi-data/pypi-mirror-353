import os
import subprocess
import sys
import time
from pathlib import Path

def run_command(command, cwd=None):
    print(f"\n⚙️ Ejecutando: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Error ejecutando: {command}")
        sys.exit(1)

def get_python_executable(venv_path):
    if os.name == 'nt':
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def run_pip(venv_path, args):
    python_exe = get_python_executable(venv_path)
    comando = f'"{python_exe}" -m pip {args}'
    run_command(comando)

def crear_archivo(path, contenido=""):
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenido)

def main():
    print("🚀 Bienvenido al generador de proyectos FastAPI 🔥\n")

    nombre_proyecto = input("Nombre del proyecto: ").strip()
    usar_alembic = input("¿Quieres agregar migraciones con Alembic? (s/n): ").strip().lower().startswith('s')
    usar_docker = input("¿Quieres usar Docker? (s/n): ").strip().lower().startswith('s')
    usar_templates = input("¿Quieres agregar plantillas con JinJa? (s/n): ").strip().lower().startswith('s')

    print("¿Qué base de datos vas a usar?")
    print("1. SQLite (default)")
    print("2. PostgreSQL")
    print("3. MySQL")
    db_opcion = input("Elige (1/2/3): ").strip()
    if db_opcion not in ['1', '2', '3']:
        db_opcion = '1'

    base_path = Path(nombre_proyecto)
    if base_path.exists():
        print(f"❌ ERROR: La carpeta '{nombre_proyecto}' ya existe.")
        sys.exit(1)
    base_path.mkdir()

    carpetas = ["models", "database", "routes", "schemas", "services"]
    if usar_templates:
        carpetas += ["templates", "static"]

    for carpeta in carpetas:
        full_path = base_path / carpeta
        full_path.mkdir(parents=True, exist_ok=True)
        if carpeta not in ["templates", "static"]:
            crear_archivo(full_path / "__init__.py")

    if usar_templates:
        for sub in ["styles", "js", "images", "audio"]:
            (base_path / "static" / sub).mkdir(parents=True, exist_ok=True)

        base_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi APP</title>
    <!-- Estilos -->
    {% block styles%}{%endblock%}
</head>
<body>
    {% block content %}{%endblock%}
    <!-- Scripts -->
    {% block scripts %}{%endblock%}
</body>
</html>
"""
        index_html = """
{% extends "base.html" %}
{%block styles%}
<link rel="stylesheet" href="{{url_for('static', path='/styles/style.css')}}">
{%endblock%}

{%block content%}
<div class="container">
    <a href="https://fastapi.tiangolo.com/es/" target="_blank">
        <img class="fastapi-logo" src="https://christophergs.com/assets/images/ultimate-fastapi-tut-pt-1/fastapi-logo.png" alt="fastapi-logo">
    </a>
    <span class="plus">+</span>
    <h1><a href="#">¡Start Project!</a></h1><!-- Pendiente link repo -->
</div>
{%endblock%}

{%block scripts%}
<script src="{{url_for('static', path='/js/index.js')}}"></script>
{%endblock%}
""" 
        style_css = """ 
/* Estilos generales */
body{
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #272525;
    color: #d9d4d4;
    margin: 0;
    padding: 0;
    font-family: sans-serif;
}

.fastapi-logo{
    cursor: pointer;
    max-width: 400px;
    filter: drop-shadow(0 0 5px #019083);
    transition: filter .5s;
}
.fastapi-logo:hover{
    filter: drop-shadow(0 0 10px #019083);
}
.container{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.plus{
    font-size: xx-large
}

h1{
    margin-top: 5px;
    font-family: "Ancizar Sans", sans-serif;
    font-optical-sizing: auto;
    font-style: italic;
    font-size: 60px;
    color: #019083;
    cursor: pointer;
    transition: text-shadow .5s;
    text-shadow: 0 0 5px #019083;
    animation-name: start-project;
}

h1:hover{
    text-shadow: 0 0 10px #019083;
}

/* Animaciónes */
@keyframes logo-fade-in {
    0% {
        opacity: 0;
        transform: scale(0.8);
        filter: drop-shadow(0 0 0px #019083);
    }
    100% {
        opacity: 1;
        transform: scale(1);
        filter: drop-shadow(0 0 5px #019083);
    }
}

@keyframes title-glow {
    0% {
        opacity: 0;
        text-shadow: 0 0 0px #019083;
        transform: translateY(-20px);
    }
    50% {
        opacity: 1;
        text-shadow: 0 0 15px #01d4aa;
        transform: translateY(0);
    }
    100% {
        text-shadow: 0 0 5px #019083;
    }
}

@keyframes plus-pulse {
    0% {
        transform: scale(1);
        text-shadow: 0 0 5px #cfb577;
    }
    50% {
        transform: scale(1.2);
        text-shadow: 0 0 15px #f8cc67;
    }
    100% {
        transform: scale(1);
        text-shadow: 0 0 5px #a48336;
    }
}
/* Aplica las animaciones */
.fastapi-logo {
    animation: logo-fade-in 1.2s ease-out forwards;
}

h1 {
    animation: title-glow 1.5s ease-out forwards;
}
.plus {
    font-size: 62px;
    animation: plus-pulse 2s infinite ease-in-out;
    color: #f8cd67af;
    transition: transform 0.3s;
}
 """
        crear_archivo(base_path / "templates" / "base.html", base_html.strip())
        crear_archivo(base_path / "templates" / "index.html", index_html.strip())
        crear_archivo(base_path / "static" / "styles" / "style.css", style_css.strip())
        crear_archivo(base_path / "static" / "js" / "index.js")

        main_py = f"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes import router

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.include_router(router)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {{"request": request}})
"""
    else:
        main_py = f"""
from fastapi import FastAPI
from routes import router

app = FastAPI()
app.include_router(router)

@app.get("/")
async def root():
    return {{"message": "¡Bienvenido a {nombre_proyecto}!"}}
"""
    crear_archivo(base_path / "main.py", main_py.strip())

    db_url = {
        '1': f"sqlite:///./{nombre_proyecto}.db",
        '2': "postgresql+asyncpg://user:password@localhost/dbname",
        '3': "mysql+aiomysql://user:password@localhost/dbname"
    }[db_opcion]

    config_py = f"""

# Modulos esternos
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Definimos la URL de conexión
# Usamos asyncmy como driver asincrónico para MySQL
DATABASE_URL = "{db_url}"

# Creamos el motor de conexión asíncrono
engine = create_async_engine(
    DATABASE_URL,
    echo=True,    # Para mostrar en consola las consultas SQL ejecutadas
)

# Creamos la fábrica de sesiones asíncronas
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

# Base declarativa para los modelos
class Base(DeclarativeBase):
    pass

# Dependencia para obtener una sesión en cada operación
async def get_session():

    async with async_session() as session:
        yield session
"""
    crear_archivo(base_path / "database" / "config.py", config_py.strip())

    routes_init = """
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}
"""
    crear_archivo(base_path / "routes" / "__init__.py", routes_init.strip())

    print("\n⏳ Creando entorno virtual...")
    venv_path = base_path / "venv"
    run_command(f"python -m venv {venv_path}")

    python_exe = get_python_executable(venv_path).resolve()
    for _ in range(5):
        if python_exe.exists():
            break
        print("⌛ Esperando a que el entorno virtual esté listo...")
        time.sleep(1)
    else:
        print(f"❌ No se encontró el ejecutable: {python_exe}")
        sys.exit(1)

    print(f"✅ Ejecutable detectado: {python_exe}")

    print("\n⏳ Actualizando pip...")
    run_pip(venv_path, "install --upgrade pip")

    print("\n📦 Instalando dependencias...")
    deps = "fastapi uvicorn sqlalchemy"
    if db_opcion == '1':
        deps += " aiosqlite"
    elif db_opcion == '2':
        deps += " asyncpg"
    else:
        deps += " aiomysql"
    if usar_templates:
        deps += " jinja2"
    run_pip(venv_path, f"install {deps}")

    if usar_alembic:
        run_pip(venv_path, "install alembic")
        print("\n⚙️ Inicializando Alembic...")
        run_command(f'"{python_exe}" -m alembic init alembic', cwd=base_path)
        print("📝 Alembic inicializado. Configura alembic.ini y env.py para tu base de datos.")

    if usar_docker:
        dockerfile = f"""
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy
"""
        if usar_alembic:
            dockerfile += "RUN pip install alembic\n"
        if db_opcion == '2':
            dockerfile += "RUN pip install asyncpg\n"
        elif db_opcion == '3':
            dockerfile += "RUN pip install aiomysql\n"
        if usar_templates:
            dockerfile += "RUN pip install jinja2\n"
        dockerfile += """
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        crear_archivo(base_path / "Dockerfile", dockerfile.strip())

    print("\n🎉 Proyecto creado con éxito en la carpeta:", nombre_proyecto)

    print("\n🚀 Iniciando servidor...")
    print(f"➡️ Ejecutable: {python_exe}")
    print(f"➡️ cwd: {base_path.resolve()}")
    run_command(f'"{python_exe}" -m uvicorn main:app --reload', cwd=base_path.resolve())

if __name__ == "__main__":
    main()