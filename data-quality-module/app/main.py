from fastapi import FastAPI

# Router existente
from app.routers.quality_router import router as quality_router

# 🔥 TU router nuevo
from app.routers.inventory_router import router as inventory_router


app = FastAPI(
    title="Data Quality Module",
    description="Métricas de calidad sobre lotes de inventario. Funciona con datos mock si el inventory-service no está disponible.",
    version="1.0.0",
)

# Router original (NO tocar)
app.include_router(quality_router, prefix="/quality")

# 🔥 TU NUEVO ROUTER
app.include_router(inventory_router)