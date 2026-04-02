

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.infrastructure.database import Base


#Modelos en la Base de datos 
class DatasetLoadORM(Base):
    __tablename__ = "dataset_load"

    id = Column(String, primary_key=True)
    file_name = Column(String, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    record_count = Column(Integer, nullable=True)
    valid_record_count = Column(Integer, nullable=True)
    invalid_record_count = Column(Integer, nullable=True)

class DatasetFileReferenceORM(Base):
    __tablename__ = "dataset_file_reference"

    id = Column(String, primary_key=True)
    dataset_load_id = Column(String, ForeignKey("dataset_load.id"))
    storage_path = Column(String, nullable=False)
    file_format = Column(String, nullable=False)
    checksum = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)