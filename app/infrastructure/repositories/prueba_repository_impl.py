#importaciones
from sqlalchemy.orm import Session

from app.domain.entity.prueba_entity import Prueba
from app.domain.repository.prueba_repository import IPruebaRepository
from app.infrastructure.models.prueba_model import PruebaModel


class SqlAlchemyPruebaRepository(IPruebaRepository):
    #Implementamos el repositorio
    def __init__(self,db:Session):
        self.db=db
    
    #Mapeamos la entidad Pura
    def guardar(self,prueba:Prueba)->Prueba:
        nuevo_registro=PruebaModel(texto_prueba=prueba.prueba)

        #guardamos
        self.db.add(nuevo_registro)
        self.db.commit()
        self.db.refresh(nuevo_registro) #Obtener id  a la entidad

        #mapeamos el modelo de base de datos
        prueba.id=nuevo_registro.id
        return prueba
    
    def obtener_todas(self)->list[Prueba]:
        pass