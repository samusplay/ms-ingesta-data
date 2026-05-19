import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
import httpx

MS_AUDITORIA_URL = os.getenv("MS_AUDITORIA_URL", "http://ms-auditoria:8000")

async def send_audit_event(trace_id: str, event_type: str, summary: str):
    """Envía un evento de auditoría asíncronamente al ms-auditoria"""
    payload = {
        "event_type": event_type,
        "service_name": "ms-ingestion",
        "trace_id": trace_id,
        "event_summary": summary
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{MS_AUDITORIA_URL}/api/v1/events", json=payload, timeout=5.0)
    except Exception as e:
        print(f"Error enviando evento de auditoría: {e}")

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
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    trace_id = str(uuid.uuid4())
    # Validación de formato inicial
    nombre, extension = os.path.splitext(file.filename)
    if extension.lower() not in [".csv", ".json"]:
        background_tasks.add_task(send_audit_event, trace_id, "FORMAT_ERROR", f"Formato inválido intentado: {extension}")
        raise HTTPException(
            status_code=400, 
            detail="Formato no válido. Por favor suba un archivo CSV o JSON."
        )

    content = await file.read()
    if len(content) == 0:
        background_tasks.add_task(send_audit_event, trace_id, "EMPTY_FILE_ERROR", "Se intentó subir un archivo vacío.")
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
        
        # Enviamos evento de éxito
        summary = f"Carga exitosa del dataset {file.filename} con {metrics['valid_record_count']} registros válidos."
        background_tasks.add_task(send_audit_event, trace_id, "DATA_LOADED", summary)

        #Resumen estadistico
        return {
            "success": True,
            "data": {
                "dataset_load_id": str(dataset.id),
                "trace_id": trace_id,
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
        background_tasks.add_task(send_audit_event, trace_id, "VALIDATION_FAILED", dve.message)
        # CA 1: Retornar 422 Unprocessable Entity
        raise HTTPException(status_code=422, detail=dve.message)
        
    except ValueError as ve:
        background_tasks.add_task(send_audit_event, trace_id, "VALUE_ERROR", str(ve))
        raise HTTPException(status_code=400, detail=str(ve))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Enviamos evento de auditoría asíncrono
        background_tasks.add_task(
            send_audit_event,
            trace_id=trace_id,
            event_type="DATA_LOAD_ERROR",
            summary=f"Error interno del servidor: {str(e)}"
        )
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