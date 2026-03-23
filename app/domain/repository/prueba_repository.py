#contrato para luego implementarlo
from abc import ABC, abstractmethod

from app.domain.entity.prueba_entity import Prueba

# abc es como se definen las interfaces en python

class IPruebaRepository(ABC):

    #Metodos del repository pasandole la entidad
    @abstractmethod
    def guardar(self,prueba:Prueba)->Prueba:
        pass

    def obtener_todas(self)->list[Prueba]:
        pass