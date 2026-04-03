from fastapi import APIRouter

from app.routers import dataset_router

#enrutador
api_router=APIRouter()



#Registramos ruta datasets

api_router.include_router(
    dataset_router.router,
    prefix="/api/v1/ingesta",
    tags=["Datasets"]
)
