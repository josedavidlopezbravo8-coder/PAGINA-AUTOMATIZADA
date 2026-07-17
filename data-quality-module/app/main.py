from fastapi import FastAPI
from app.routers.quality_router import router

app = FastAPI(
    title="Data Quality Module",
    description="Métricas de calidad sobre lotes de inventario. Funciona con datos mock si el inventory-service no está disponible.",
    version="1.0.0",
)

app.include_router(router, prefix="/quality")
