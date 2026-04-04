from enum import Enum


class DatasetStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"