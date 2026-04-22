import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.application.service.dataset_service import DatasetService
from app.application.validators.dataframe_validator import (
    DataFrameValidator,
    DatasetValidationException,
)
from app.infrastructure.database import get_db

# 👇 Importamos SOLAMENTE la implementación concreta
from app.infrastructure.repositories.dataset_repository import DatasetRepositoryImpl

router = APIRouter()

@router.post("/datasets", status_code=200) 
async def create_dataset(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    # Validación de formato inicial
    nombre, extension = os.path.splitext(file.filename)
    if extension.lower() not in [".csv", ".json"]:
        raise HTTPException(
            status_code=400, 
            detail="Formato no válido. Por favor suba un archivo CSV o JSON."
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=400, 
            detail="El archivo está vacío o corrupto."
        )

    # 👇 CORRECCIÓN: Inyección de dependencias usando la implementación concreta (Impl)
    repo = DatasetRepositoryImpl()
    validator = DataFrameValidator()
    service = DatasetService(repo, validator)

    try:
        # Procesamos y recibimos métricas
        dataset, metrics = await service.process_dataset(db, file, content)
        
        trace_id_str = str(uuid.uuid4())
        dataset_id_str = str(dataset.id)

        # Enviar evento de auditoría asíncronamente
        from app.infrastructure.http_audit_client import HttpAuditClient
        import asyncio
        audit_client = HttpAuditClient()
        asyncio.create_task(
            audit_client.send_audit_event(
                reference_id=dataset_id_str,
                trace_id=trace_id_str,
                summary=f"Carga y validación inicial de dataset completada. Records validos: {metrics['valid_record_count']}"
            )
        )
        
        #Resumen estadistico
        return {
            "success": True,
            "data": {
                "dataset_load_id": dataset_id_str,
                "trace_id": trace_id_str,
                "metrics": {
                    "total_records": metrics["record_count"],
                    "valid_records": metrics["valid_record_count"],
                    "invalid_records": metrics["invalid_record_count"],
                    "final_status": "VALIDATED"
                }
            },
            "error": None
        }

    except DatasetValidationException as dve:
        # CA 1: Retornar 422 Unprocessable Entity
        raise HTTPException(status_code=422, detail=dve.message)
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    

# Endpoint para que ms-transform traiga los datos
@router.get("/datasets/{dataset_load_id}/raw", status_code=200)
async def get_raw_dataset_records(
    dataset_load_id: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint para que ms-transform pueda obtener los datos validados 
    del dataset en formato JSON.
    """
    # 1. Instanciamos la implementación concreta de nuestro repositorio
    repo = DatasetRepositoryImpl()
    validator = DataFrameValidator()
    
    # 2. Inyectamos el repo y el validador en el servicio
    service = DatasetService(repo, validator)

    try:
        # 3. Llamamos al caso de uso que creamos en el servicio
        records = await service.get_dataset_raw_data(db, dataset_load_id)
        
        # 4. Cumplimos con el contrato esperado (StandardResponse)
        return {
            "success": True,
            "data": records,
            "error": None
        }
    except Exception as e:
        # Si algo falla (ej: el ID no existe o no hay datos), lanzamos 404
        print(f"Error al obtener dataset raw data: {e}")
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron registros para el dataset ID: {dataset_load_id}"
        )