from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.domain.models.models import DatasetFileReference, DatasetLoad, DatasetRecord


class DatasetRepositoryPort(ABC):
    """
    PUERTO DEL DOMINIO: Define qué debe hacer cualquier repositorio de datasets,
    sin importar qué base de datos se use.
    """

    @abstractmethod
    def create_dataset_load(self, db: Any, file_name: str) -> DatasetLoad:
        pass

    @abstractmethod
    def create_file_reference(self, db: Any, dataset_id: str, path: str, fmt: str, checksum: str) -> DatasetFileReference:
        pass

    @abstractmethod
    def update_counts(self, db: Any, dataset_id: str, total: int, valid: int, invalid: int, status: str) -> DatasetLoad:
        pass

    @abstractmethod
    def save_raw_records(self, db: Any, dataset_id: str, records: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    def get_raw_records(self, db: Any, dataset_id: str) -> List[DatasetRecord]:
        pass