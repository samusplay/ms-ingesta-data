from fastapi import APIRouter

from app.routers import dataset_router, prueba_router

#enrutador
api_router=APIRouter()

#Registrar rutas hijas
api_router.include_router(prueba_router.router,prefix="/api/v1/ingesta",tags=(["Pruebas"]))

#Registramos ruta datasets

api_router.include_router(
    dataset_router.router,
    prefix="/api/v1/ingesta",
    tags=["Datasets"]
)
