from sqlalchemy.orm import Session
from app.domain.enums import DatasetStatus
from app.infrastructure.repositories.dataset_repository import DatasetRepository


class DatasetService:

    def __init__(self, repo: DatasetRepository):
        self.repo = repo

    def process_dataset(
        self,
        db: Session,
        file_name: str,
        path: str,
        fmt: str,
        checksum: str,
        total: int,
        valid: int,
        invalid: int
    ):
        try:
            # CA1
            dataset = self.repo.create_dataset_load(db, file_name)

            # 🔥 FIX CRÍTICO
            db.flush()

            # CA2
            self.repo.create_file_reference(
                db,
                dataset.id,
                path,
                fmt,
                checksum
            )

            # CA3
            status = (
                DatasetStatus.COMPLETED.value
                if invalid == 0
                else DatasetStatus.FAILED.value
            )

            self.repo.update_counts(
                db,
                dataset.id,
                total,
                valid,
                invalid,
                status
            )

            # CA4
            db.commit()

            return dataset

        except Exception:
            db.rollback()
            raise