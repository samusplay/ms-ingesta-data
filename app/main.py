from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.database import Base, check_db_connection, engine

# Importamos los modelos para que SQLAlchemy los detecte antes de crear tablas
from app.infrastructure.models import dataset_orm  # noqa
from app.routers.api import api_router


# Gestor de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\033[94m⚙️  Configurando servicios internos...\033[0m")
    
    # 1. Creamos las tablas AQUÍ en el punto de entrada
    try:
        Base.metadata.create_all(bind=engine)
        print("\033[92m✅ Tablas de la base de datos sincronizadas\033[0m")
    except Exception as e:
        print(f"\033[91m🚨 Error creando tablas: {e}\033[0m")

    # 2. Verificamos conexión a Postgres
    if check_db_connection():
        print("\033[92m✅ PERSISTENCIA: Conectado a PostgreSQL\033[0m")
    else:
        print("\033[91m🚨 PERSISTENCIA: Fallo al conectar a PostgreSQL\033[0m")
    
    yield
    print("\033[93m\nFinalizando procesos...\033[0m")

# Instanciamos app
app = FastAPI(
    title="API Ingesta de Datos",
    description="Responsable de recibir datasets y extraer metadatos de carga",
    version="1.0.0",
    lifespan=lifespan
)

# Llamada al enrutador central
app.include_router(api_router)

# Health Check
@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok", "service": "ms-ingestion"}