import hashlib
import re

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.application.validators.dataframe_validator import (
    DataFrameValidator,
    DatasetValidationException,
)
from app.domain.enums import DatasetStatus
from app.infrastructure.repositories.dataset_repository import DatasetRepository


class DatasetService:
    def __init__(self, repo: DatasetRepository, validator: DataFrameValidator):
        self.repo = repo
        self.validator = validator

    async def process_dataset(self, db: Session, file: UploadFile, content: bytes):
        # Limpiamos el nombre del archivo para que sea seguro
        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
        file_format = safe_name.split(".")[-1].lower()
        checksum = hashlib.md5(content).hexdigest()

      
        try:
            # Pasamos los BYTES directamente al validador (io.BytesIO)
            df_clean, metrics = self.validator.extract_metrics(file_content=content, file_format=file_format)
            
        except DatasetValidationException as e:
            # CA 1: Falla estructural. Registramos como REJECTED en BD.
            dataset = self.repo.create_dataset_load(db, safe_name)
            db.flush()

            self.repo.update_counts(
                db=db,
                dataset_id=str(dataset.id),
                total=0,
                valid=0,
                invalid=0,
                status=DatasetStatus.REJECTED.value
            )
            db.commit()
            raise e # Relanzamos la excepción para que el router devuelva 422

       
        try:
            dataset = self.repo.create_dataset_load(db, safe_name)
            db.flush()

            self.repo.create_file_reference(
                db=db,
                dataset_id=str(dataset.id),
                # Ya no guardamos path físico temporal. Si usaras S3, aquí iría esa URL.
                path="in_memory_processing_only", 
                fmt=file_format,
                checksum=checksum
            )

            # CA 4: Estado correcto (VALIDATED)
            self.repo.update_counts(
                db=db,
                dataset_id=str(dataset.id),
                total=metrics["record_count"],
                valid=metrics["valid_record_count"],
                invalid=metrics["invalid_record_count"],
                status=DatasetStatus.VALIDATED.value
            )

            db.commit()
            return dataset, metrics # CA 5: Retornamos las métricas para el body

        except Exception as e:
            db.rollback()
            raise e