
from pydantic import BaseModel


#lo que esperamos recibir
class PruebaCreate(BaseModel):
    texto:str

#Respuesta
class PruebaResponse(BaseModel):
    success:bool
    data:dict