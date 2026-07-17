from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.configuration import DEFAULT_CONFIG, get_parameter, load_config, set_parameter

router = APIRouter()


class ConfigValue(BaseModel):
    value: Any


@router.get("/")
def read_config():
    return load_config()


@router.get("/{key}")
def read_config_key(key: str):
    if key not in DEFAULT_CONFIG:
        raise HTTPException(status_code=404, detail=f"Parámetro '{key}' no encontrado")
    return {"key": key, "value": get_parameter(key)}


@router.put("/{key}")
def update_config_key(key: str, config_value: ConfigValue):
    if key not in DEFAULT_CONFIG:
        raise HTTPException(status_code=404, detail=f"Parámetro '{key}' no encontrado")
    try:
        new_value = set_parameter(key, config_value.value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"key": key, "value": new_value}
