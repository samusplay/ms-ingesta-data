import pandas as pd


class DataFrameValidator:
    #Clase para tratar los formatos
    def extract_metrics(self,file_path:str,file_format:str)->dict:
        try:
            #leer el archivo
            if file_format=='csv':
                df=pd.read_csv(file_path)
            elif file_format=='json':
                df=pd.read_json(file_path)
            else:
                raise ValueError("Formato No soportado")
            #calcular metricas
            total=len(df)
            #elimina filas
            valid=len(df.dropna())
            invalid=total-valid
            #retornamos respuesta
            return{
                "total": total,
                "valid": valid,
                "invalid": invalid
            }
        except pd.errors.EmptyDataError:
            raise ValueError("El archivo esta estructuralmente vacio")
        except Exception as e:
            raise ValueError(f"Error procesando archivo:{str(e)}")