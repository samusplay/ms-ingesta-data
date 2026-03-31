from fastapi import FastAPI
from app.routers.dataset_router import router
from app.infrastructure.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}