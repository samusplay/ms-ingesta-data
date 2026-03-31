from pydantic import BaseModel


class DatasetRequest(BaseModel):
    file_name: str
    storage_path: str
    file_format: str
    checksum: str
    total: int
    valid: int
    invalid: int