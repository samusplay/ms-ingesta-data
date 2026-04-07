from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class DatasetLoad:
    id: UUID
    file_name: str
    uploaded_at: datetime
    status: str
    record_count: int | None = None
    valid_record_count: int | None = None
    invalid_record_count: int | None = None


@dataclass
class DatasetFileReference:
    id: UUID
    dataset_load_id: UUID
    storage_path: str
    file_format: str
    checksum: str
    created_at: datetime
    
@dataclass
class DatasetRecord:
    id:UUID
    dataset_load_id:UUID
    row_data:dict