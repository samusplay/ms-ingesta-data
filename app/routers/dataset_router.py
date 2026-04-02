
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

#conexion a la base de datos este import
from app.application.dataset_service import DatasetService
from app.application.validators.dataframe_validator import DataFrameValidator
from app.infrastructure.database import get_db
from app.infrastructure.repositories.dataset_repository import DatasetRepository

router=APIRouter()

async def create_dataset(
        file:UploadFile=File(...),
        db:Session=Depends(get_db)
):
    #Rechazamos formatos
    nombre, extension = os.path.splitext(file.filename)
    if extension.lower() not in [".csv", ".json"]:
        raise HTTPException(
            status_code=400, 
            detail="Formato no válido. Por favor suba un archivo CSV o JSON."
        )
    #validacion de integridad del contenido
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=400, 
            detail="El archivo está vacío o corrupto."
        )
    #inyectamos dependencias
    repo=DatasetRepository()
    validator=DataFrameValidator()
    #el service va usar el repo y el validator como parametros
    service=DatasetService(repo,validator)

    #Mostramos respuesta con try y except
    try:
        #pasamos contenido al servicio
        dataset=await service.process_dataset(db,file,content)
        
        return{
            "success": True,
            "data": {
                "dataset_load_id": dataset.id,
                "trace_id": str(uuid.uuid4())
            },
            "error": None
        }
    except ValueError as ve:
        #si pandas detecta que el archivo manda vacio 400
        raise HTTPException(status_code=400,detail=str(ve))
    except Exception as e:
        #Erros 500 interno del servidor
        import traceback
        #muestra el error
        traceback.print_exc()
        raise HTTPException(status_code=500,detail=f"Error interno del servidor:{str(e)}")