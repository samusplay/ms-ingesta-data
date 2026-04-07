# app/main.py (DENTRO DE MS-TRANSFORM)
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure import models  # noqa
from app.infrastructure.database import Base, check_db_connection, engine
from app.routers.api import api_router


# Gestor de vida de la aplicación (lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\033[94m⚙️  Configurando servicios de TRANSFORMACIÓN...\033[0m")
    
    # 1. Creamos las tablas de transformación físicamente en Postgres
    try:
       
        Base.metadata.create_all(bind=engine)
        print("\033[92m✅ Tablas de TRANSFORMACIÓN sincronizadas\033[0m")
    except Exception as e:
        print(f"\033[91m🚨 Error creando tablas en MS-TRANSFORM: {e}\033[0m")

   
    if check_db_connection():
        print("\033[92m✅ PERSISTENCIA: Conectado a db_transformation\033[0m")
    else:
        print("\033[91m🚨 PERSISTENCIA: Fallo al conectar a db_transformation\033[0m")
    
    yield
    print("\033[93m\nFinalizando procesos de transformación...\033[0m")


app = FastAPI(
    title="API Transformación de Datos",
    description="Responsable de limpiar y estructurar los datos recibidos de Ingesta",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(api_router)


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok", "service": "ms-transform"}