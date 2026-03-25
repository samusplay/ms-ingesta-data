

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.prueba_service import PruebaService
from app.infrastructure.database import get_db
from app.infrastructure.repositories.prueba_repository_impl import (
    SqlAlchemyPruebaRepository,
)
from app.schemas.prueba_service import PruebaCreate, PruebaResponse

router=APIRouter()
@router.post("/test-hexagonal",response_model=PruebaResponse)
def endpoint_crear_prueba(request:PruebaCreate ,db:Session=Depends(get_db)):

    #instaciamos la infrastructura
    repositorio=SqlAlchemyPruebaRepository(db)

    #inyectamos la infrastrcutura al servicio
    service=PruebaService(repository=repositorio)

    #Extraemos del Schema y pasamos al servicio
    resultado=service.crear_prueba(texto=request.texto)

    #devolvemos la respuesta segun el formato del Schema
    return{
        "success":True,
        "data":resultado
    }
