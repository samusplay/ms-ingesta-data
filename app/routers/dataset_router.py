import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.application.dataset_service import DatasetService
from app.application.validators.dataframe_validator import (
    DataFrameValidator,
    DatasetValidationException,
)
from app.infrastructure.database import get_db
from app.infrastructure.repositories.dataset_repository import DatasetRepository

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

    # Inyección de dependencias
    repo = DatasetRepository()
    validator = DataFrameValidator()
    service = DatasetService(repo, validator)

    try:
        # Procesamos y recibimos métricas
        dataset, metrics = await service.process_dataset(db, file, content)
        
        #Resumen estadistico
        return {
            "success": True,
            "data": {
                "dataset_load_id": str(dataset.id),
                "trace_id": str(uuid.uuid4()),
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