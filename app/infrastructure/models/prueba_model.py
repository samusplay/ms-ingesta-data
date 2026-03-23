#Orm
from sqlalchemy import Column, Integer, String

from app.infrastructure.database import Base


# El modelo si sabe de base de datos
class PruebaModel(Base):
    #nombre de la
    __tablename__="prueba"

    id=Column(Integer, primary_key=True, index=True)
    texto_prueba=Column(String,nullable=False)
