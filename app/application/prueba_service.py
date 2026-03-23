from app.domain.entity.prueba_entity import Prueba
from app.domain.repository.prueba_repository import IPruebaRepository

#Servicio logica de calculos

class PruebaService:
    #inyectamos dependencias Repositorio
    def __init__(self,repository:IPruebaRepository):
        self.repository=repository
    
    def crear_prueba(self,texto:str)->dict:
        """Recibimos datos primititivos"""

        #creamos entidad pura
        nueva_prueba=Prueba(prueba=texto)

        #usamos el contrato
        prueba_guardada=self.repository.guardar(nueva_prueba)

        #devolvemos datos
        return{
            "id":prueba_guardada.id,
            "texto-guardado":prueba_guardada.prueba
        }

