from typing import Any, Tuple


class DatasetValidationException(Exception):
    """Excepción usada cuando un dataset no cumple las reglas de validación."""
    pass


class DataFrameValidator:
    """Stub mínimo de validador de DataFrame para ms-ingesta-data."""

    def extract_metrics(self, file_content: bytes, file_format: str) -> Tuple[Any, dict]:
        raise NotImplementedError("DataFrameValidator.extract_metrics debe implementarse")
