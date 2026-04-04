import io
from typing import Dict, Tuple

import pandas as pd


# Ya no lanzaremos excepción por columnas faltantes, pero la dejamos por si el archivo está corrupto
class DatasetValidationException(Exception):
    pass

class DataFrameValidator:
    """
    Clase encargada de validar la estructura básica del dataset en memoria.
    Se ha flexibilizado para aceptar datasets crudos sin cabeceras estrictas.
    """
    
    # 🔹 Cabeceras deseadas (pero ahora opcionales para la ingesta)
    DESIRED_HEADERS = ["zone_code", "zone_name"]

    @classmethod
    def extract_metrics(cls, file_content: bytes, file_format: str) -> Tuple[pd.DataFrame, Dict[str, int]]:
        try:
            # 1. LEER EN MEMORIA
            if file_format == 'csv':
                df = pd.read_csv(io.BytesIO(file_content))
            elif file_format == 'json':
                df = pd.read_json(io.BytesIO(file_content))
            else:
                raise ValueError(f"Formato no soportado: {file_format}")

            total_records = len(df)
            df_columns = df.columns.tolist()

            
            # Verificamos si tiene las columnas exactas
            has_desired_columns = all(col in df_columns for col in cls.DESIRED_HEADERS)

            df_clean = df.copy()

            if has_desired_columns:
                # Si tiene la suerte de venir con las cabeceras exactas, hacemos limpieza temprana
                df_clean = df_clean.dropna(subset=cls.DESIRED_HEADERS)
                df_clean["zone_code"] = pd.to_numeric(df_clean["zone_code"], errors="coerce")
                df_clean = df_clean.dropna(subset=["zone_code"])
            else:
                # Si no las tiene, simplemente aceptamos el archivo tal cual viene.
                # La limpieza real se hará en el módulo de Análisis/Transformación.
                pass

            # 3. CONTADORES FINALES
            valid_records = len(df_clean)
            invalid_records = total_records - valid_records

            metrics = {
                "record_count": total_records,
                "valid_record_count": valid_records,
                "invalid_record_count": invalid_records
            }

            return df_clean, metrics

        except pd.errors.EmptyDataError:
            raise ValueError("El archivo está estructuralmente vacío")
        except Exception as e:
            raise ValueError(f"Error procesando archivo en memoria: {str(e)}")