from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.config_router import router

app = FastAPI(
    title="Config Module",
    description="Servicio de configuración reusable para parámetros del sistema.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/config")
