from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

# Importamos los estados y entidades PURAS del dominio
from app.domain.enums import DatasetStatus
from app.domain.models import DatasetFileReference, DatasetLoad

# Importamos los modelos de base de datos
from app.infrastructure.models.dataset_orm import (
    DatasetFileReferenceORM,
    DatasetLoadORM,
)


class DatasetRepository:

    def create_dataset_load(self, db: Session, file_name: str) -> DatasetLoad:
        new_id = str(uuid4())
        now = datetime.utcnow()

        # 1. Creamos el objeto para la Base de Datos (ORM)
        dataset_orm = DatasetLoadORM(
            id=new_id,
            file_name=file_name,
            uploaded_at=now,
            status=DatasetStatus.PROCESSING.value
        )
        db.add(dataset_orm)
        

        # 2. Retornamos la entidad pura del Dominio (Aplicamos Inversión de Dependencias)
        return DatasetLoad(
            id=UUID(new_id),
            file_name=file_name,
            uploaded_at=now,
            status=DatasetStatus.PROCESSING.value
        )

    def create_file_reference(self, db: Session, dataset_id: str, path: str, fmt: str, checksum: str) -> DatasetFileReference:
        new_id = str(uuid4())
        now = datetime.utcnow()

        ref_orm = DatasetFileReferenceORM(
            id=new_id,
            dataset_load_id=dataset_id,
            storage_path=path,
            file_format=fmt,
            checksum=checksum,
            created_at=now
        )
        db.add(ref_orm)

        return DatasetFileReference(
            id=UUID(new_id),
            dataset_load_id=UUID(dataset_id),
            storage_path=path,
            file_format=fmt,
            checksum=checksum,
            created_at=now
        )

    def update_counts(self, db: Session, dataset_id: str, total: int, valid: int, invalid: int, status: str) -> DatasetLoad:
        dataset_orm = db.query(DatasetLoadORM).filter_by(id=dataset_id).first()

        if dataset_orm:
            dataset_orm.record_count = total
            dataset_orm.valid_record_count = valid
            dataset_orm.invalid_record_count = invalid
            dataset_orm.status = status

        # Devolvemos el dominio actualizado (Simplificado para el ejemplo)
        return DatasetLoad(
            id=UUID(dataset_orm.id),
            file_name=dataset_orm.file_name,
            uploaded_at=dataset_orm.uploaded_at,
            status=dataset_orm.status,
            record_count=total,
            valid_record_count=valid,
            invalid_record_count=invalid
        )