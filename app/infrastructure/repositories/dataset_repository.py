from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from app.domain.enums import DatasetStatus
from app.infrastructure.db import Base
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey


# =========================
# ORM MODELS
# =========================

class DatasetLoadORM(Base):
    __tablename__ = "dataset_load"

    id = Column(String, primary_key=True)
    file_name = Column(String, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    record_count = Column(Integer)
    valid_record_count = Column(Integer)
    invalid_record_count = Column(Integer)


class DatasetFileReferenceORM(Base):
    __tablename__ = "dataset_file_reference"

    id = Column(String, primary_key=True)
    dataset_load_id = Column(String, ForeignKey("dataset_load.id"))
    storage_path = Column(String, nullable=False)
    file_format = Column(String, nullable=False)
    checksum = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


# =========================
# REPOSITORY (SOLID - SRP)
# =========================

class DatasetRepository:

    def create_dataset_load(self, db: Session, file_name: str):
        dataset = DatasetLoadORM(
            id=str(uuid4()),
            file_name=file_name,
            uploaded_at=datetime.utcnow(),
            status=DatasetStatus.PROCESSING.value
        )
        db.add(dataset)
        return dataset

    def create_file_reference(self, db: Session, dataset_id: str, path: str, fmt: str, checksum: str):
        ref = DatasetFileReferenceORM(
            id=str(uuid4()),
            dataset_load_id=dataset_id,
            storage_path=path,
            file_format=fmt,
            checksum=checksum,
            created_at=datetime.utcnow()
        )
        db.add(ref)
        return ref

    def update_counts(self, db: Session, dataset_id: str, total: int, valid: int, invalid: int, status: str):
        dataset = db.query(DatasetLoadORM).filter_by(id=dataset_id).first()

        dataset.record_count = total
        dataset.valid_record_count = valid
        dataset.invalid_record_count = invalid
        dataset.status = status

        return dataset