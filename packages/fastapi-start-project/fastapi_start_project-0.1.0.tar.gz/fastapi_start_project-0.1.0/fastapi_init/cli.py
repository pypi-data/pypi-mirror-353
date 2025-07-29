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
<h1>¡Hola desde FastAPI + Jinja2!</h1>
{%endblock%}

{%block scripts%}
<script src="{{url_for('static', path='/js/index.js')}}"></script>
{%endblock%}
"""
        crear_archivo(base_path / "templates" / "base.html", base_html.strip())
        crear_archivo(base_path / "templates" / "index.html", index_html.strip())
        crear_archivo(base_path / "static" / "js" / "index.js")
        crear_archivo(base_path / "static" / "styles" / "style.css")

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
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DATABASE_URL = "{db_url}"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()
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