from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

# Importamos los estados y entidades PURAS del dominio
from app.domain.models.enums import DatasetStatus
from app.domain.models.models import DatasetFileReference, DatasetLoad, DatasetRecord

# IMPORTAMOS EL PUERTO DEL DOMINIO QUE VAMOS A IMPLEMENTAR
from app.domain.repository.dataset_repository import DatasetRepositoryPort

# Importamos los modelos de base de datos
from app.infrastructure.models.dataset_orm import (
    DatasetFileReferenceORM,
    DatasetLoadORM,
    DatasetRecordORM,
)


# AHORA HEREDAMOS DEL PUERTO DEL DOMINIO
class DatasetRepositoryImpl(DatasetRepositoryPort):

    def create_dataset_load(self, db: Session, file_name: str) -> DatasetLoad:
        new_id = str(uuid4())
        now = datetime.utcnow()

        dataset_orm = DatasetLoadORM(
            id=new_id,
            file_name=file_name,
            uploaded_at=now,
            status=DatasetStatus.PROCESSING.value
        )
        db.add(dataset_orm)
        
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

        return DatasetLoad(
            id=UUID(dataset_orm.id),
            file_name=dataset_orm.file_name,
            uploaded_at=dataset_orm.uploaded_at,
            status=dataset_orm.status,
            record_count=total,
            valid_record_count=valid,
            invalid_record_count=invalid
        )

    # --- LOS NUEVOS MÉTODOS PARA JSON ---

    def save_raw_records(self, db: Session, dataset_id: str, records: List[Dict[str, Any]]) -> None:
        orm_records = []
        for row in records:
            orm_records.append(
                DatasetRecordORM(
                    id=str(uuid4()),
                    dataset_load_id=dataset_id,
                    row_data=row
                )
            )
        db.add_all(orm_records)

    def get_raw_records(self, db: Session, dataset_id: str) -> List[DatasetRecord]:
        orm_records = db.query(DatasetRecordORM).filter_by(dataset_load_id=dataset_id).all()
        
        return [
            DatasetRecord(
                id=UUID(orm.id),
                dataset_load_id=UUID(orm.dataset_load_id),
                row_data=orm.row_data
            )
            for orm in orm_records
        ]