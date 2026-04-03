import hashlib
import os
import re

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.application.validators.dataframe_validator import DataFrameValidator
from app.domain.enums import DatasetStatus
from app.infrastructure.repositories.dataset_repository import DatasetRepository


class DatasetService:
    # Inyectamos el repo y el validador
    def __init__(self, repo: DatasetRepository, validator: DataFrameValidator):
        self.repo = repo
        self.validator = validator

    async def process_dataset(self, db: Session, file: UploadFile, content: bytes):
        # 1. GUARDADO
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
        file_path = os.path.join(upload_dir, safe_name)
        file_format = safe_name.split(".")[-1].lower()

        with open(file_path, "wb") as f:
            f.write(content)

        checksum = hashlib.md5(content).hexdigest()

        # 2. VALIDACIÓN
        try:
            df_clean, metrics = self.validator.extract_metrics(file_path, file_format)

        except ValueError as e:
            # 🔴 crear dataset en estado REJECTED
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

            if os.path.exists(file_path):
                os.remove(file_path)

            raise e

        # 3. TRANSACCIÓN DE BASE DE DATOS
        try:
            dataset = self.repo.create_dataset_load(db, safe_name)
            db.flush()

            self.repo.create_file_reference(
                db=db,
                dataset_id=str(dataset.id),
                path=file_path,
                fmt=file_format,
                checksum=checksum
            )

            # 🔹 estado correcto según Jira
            status = DatasetStatus.VALIDATED.value

            self.repo.update_counts(
                db=db,
                dataset_id=str(dataset.id),
                total=metrics["total"],
                valid=metrics["valid"],
                invalid=metrics["invalid"],
                status=status
            )

            db.commit()

            return dataset

        except Exception as e:
            db.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e