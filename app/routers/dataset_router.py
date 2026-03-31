from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.db import SessionLocal
from app.application.dataset_service import DatasetService
from app.infrastructure.repositories.dataset_repository import DatasetRepository
from app.schemas.dataset_schema import DatasetRequest
from fastapi import UploadFile, File
import hashlib
import os
router = APIRouter()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/datasets")
def create_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    service = DatasetService(DatasetRepository())

    try:
        import re

        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
        file_path = os.path.join(upload_dir, safe_name)

        content = file.file.read()

        if not content:
            raise ValueError("Archivo vacío")

        with open(file_path, "wb") as f:
            f.write(content)

        checksum = hashlib.md5(content).hexdigest()
        file_format = safe_name.split(".")[-1]

        total = 100
        valid = 100
        invalid = 0

        dataset = service.process_dataset(
            db,
            safe_name,
            file_path,
            file_format,
            checksum,
            total,
            valid,
            invalid
        )

        return {
            "success": True,
            "data": {"dataset_id": dataset.id},
            "error": None
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))