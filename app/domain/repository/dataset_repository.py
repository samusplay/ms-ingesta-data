from typing import Any


class DatasetRepositoryPort:
    """Puerto del repositorio para la persistencia de datasets."""

    def create_dataset_load(self, db: Any, safe_name: str) -> Any:
        raise NotImplementedError()

    def update_counts(self, db: Any, dataset_id: str, total: int, valid: int, invalid: int, status: str) -> None:
        raise NotImplementedError()

    def create_file_reference(self, db: Any, dataset_id: str, path: str, fmt: str, checksum: str) -> None:
        raise NotImplementedError()

    def save_raw_records(self, db: Any, dataset_id: str, records: Any) -> None:
        raise NotImplementedError()

    def get_raw_records(self, db: Any, dataset_load_id: str) -> Any:
        raise NotImplementedError()
