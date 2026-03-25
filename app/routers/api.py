from fastapi import APIRouter

from app.routers import prueba_router

#enrutador
api_router=APIRouter()

#Registrar rutas hijas
api_router.include_router(prueba_router.router,prefix="/api/v1/ingesta",tags=(["Pruebas"]))
