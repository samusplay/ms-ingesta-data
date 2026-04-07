import hashlib
import re

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.application.validators.dataframe_validator import (
    DataFrameValidator,
    DatasetValidationException,
)
from app.domain.models.enums import DatasetStatus

# IMPORTANTE: Ahora importamos el PUERTO (la interfaz), no la implementación de BD
from app.domain.repository.dataset_repository import DatasetRepositoryPort


class DatasetService:
    # Inyectamos el puerto del dominio (Inversión de Dependencias)
    def __init__(self, repo: DatasetRepositoryPort, validator: DataFrameValidator):
        self.repo = repo
        self.validator = validator

    async def process_dataset(self, db: Session, file: UploadFile, content: bytes):
        # Limpiamos el nombre del archivo para que sea seguro
        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
        file_format = safe_name.split(".")[-1].lower()
        checksum = hashlib.md5(content).hexdigest()

        try:
            # Pasamos los BYTES directamente al validador (io.BytesIO)
            # df_clean es un DataFrame de Pandas
            df_clean, metrics = self.validator.extract_metrics(file_content=content, file_format=file_format)
            
        except DatasetValidationException as e:
            # CA 1: Falla estructural. Registramos como REJECTED en BD.
            dataset = self.repo.create_dataset_load(db, safe_name)
            db.flush()

            self.repo.update_counts(
                db=db,
                dataset_id=str(dataset.id),
                total=0,
                valid=0,
                invalid=0,
                status=DatasetStatus.REJECTED.value
            )
            db.commit()
            raise e # Relanzamos la excepción para que el router devuelva 422

        try:
            dataset = self.repo.create_dataset_load(db, safe_name)
            db.flush()

            self.repo.create_file_reference(
                db=db,
                dataset_id=str(dataset.id),
                path="in_memory_processing_only", # Se mantiene porque ahora la data vive en la tabla, no en disco físico
                fmt=file_format,
                checksum=checksum
            )

            # CA 4: Estado correcto (VALIDATED)
            self.repo.update_counts(
                db=db,
                dataset_id=str(dataset.id),
                total=metrics["record_count"],
                valid=metrics["valid_record_count"],
                invalid=metrics["invalid_record_count"],
                status=DatasetStatus.VALIDATED.value
            )

            # 👇 NUEVO: GUARDAMOS LAS FILAS CRUDAS EN LA BASE DE DATOS 👇
            # Convertimos el DataFrame a una lista de diccionarios
            # Usamos fillna(None) para que los valores NaN de Pandas sean compatibles con JSON (null)
            records_to_save = df_clean.fillna("").to_dict(orient="records")
            
            # Le pasamos la pelota al repositorio para que lo guarde
            self.repo.save_raw_records(db, str(dataset.id), records_to_save)
            # 👆 FIN DE LO NUEVO 👆

            db.commit()
            return dataset, metrics # CA 5: Retornamos las métricas para el body

        except Exception as e:
            db.rollback()
            raise e

    # 👇 NUEVO CASO DE USO PARA EL ENDPOINT GET 👇
    async def get_dataset_raw_data(self, db: Session, dataset_load_id: str):
        """
        Caso de uso: Recupera los datos crudos para dejarlos disponibles 
        para procesos posteriores (ej. ms-transform).
        """
        # El repo nos devuelve una lista de entidades puras (DatasetRecord)
        domain_records = self.repo.get_raw_records(db, dataset_load_id)
        
        # Extraemos solo el diccionario de datos (row_data) para mandarlo limpio por el API
        return [record.row_data for record in domain_records]