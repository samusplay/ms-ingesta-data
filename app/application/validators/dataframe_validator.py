import pandas as pd


class DataFrameValidator:
    """
    Clase encargada de validar la estructura y contenido del dataset
    """

    # 🔹 Cabeceras obligatorias
    REQUIRED_HEADERS = ["zone_code", "zone_name"]

    def validate_headers(self, df: pd.DataFrame):
        """
        Valida que el dataframe tenga las columnas obligatorias
        """
        missing = [col for col in self.REQUIRED_HEADERS if col not in df.columns]

        if missing:
            raise ValueError(f"Faltan las siguientes columnas obligatorias: {missing}")

    def extract_metrics(self, file_path: str, file_format: str):
        """
        Lee el archivo, valida estructura y calcula métricas
        """
        try:
            #  Leer archivo
            if file_format == 'csv':
                df = pd.read_csv(file_path)
            elif file_format == 'json':
                df = pd.read_json(file_path)
            else:
                raise ValueError("Formato No soportado")

            #  VALIDAR CABECERAS (CA1)
            self.validate_headers(df)

            #  TOTAL DE FILAS (CA2)
            total = len(df)

            #  LIMPIEZA DE DATOS (CA3)

            # Eliminar filas con nulos en columnas obligatorias
            df_clean = df.dropna(subset=["zone_code", "zone_name"]).copy()

            # Convertir zone_code a numérico
            df_clean["zone_code"] = pd.to_numeric(df_clean["zone_code"], errors="coerce")

            # Eliminar filas donde la conversión falló
            df_clean = df_clean.dropna(subset=["zone_code"])

            #  CONTADORES
            valid = len(df_clean)
            invalid = total - valid

            #  RETORNAR DATA LIMPIA + MÉTRICAS
            return df_clean, {
                "total": total,
                "valid": valid,
                "invalid": invalid
            }

        except pd.errors.EmptyDataError:
            raise ValueError("El archivo está estructuralmente vacío")

        except Exception as e:
            raise ValueError(f"Error procesando archivo: {str(e)}")