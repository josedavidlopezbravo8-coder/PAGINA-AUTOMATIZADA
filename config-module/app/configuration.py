import json
import os
from pathlib import Path
from threading import Lock
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "porcentaje_descuento_base": 0.05,
    "porcentaje_comision": 0.1,
    "limite_stock_minimo": 10,
    "error_rate_threshold": 0.15,
}

CONFIG_FILE_PATH = Path(os.getenv("CONFIG_FILE_PATH", "config_data.json"))

VALIDATORS = {
    "porcentaje_descuento_base": lambda value: isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0,
    "porcentaje_comision": lambda value: isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0,
    "limite_stock_minimo": lambda value: isinstance(value, int) and value >= 0,
    "error_rate_threshold": lambda value: isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0,
}

_LOCK = Lock()


def _ensure_config_file() -> None:
    if not CONFIG_FILE_PATH.exists() or CONFIG_FILE_PATH.stat().st_size == 0:
        save_config(DEFAULT_CONFIG)


def load_config() -> Dict[str, Any]:
    _ensure_config_file()
    with _LOCK:
        with CONFIG_FILE_PATH.open("r", encoding="utf-8") as handle:
            try:
                data = json.load(handle)
            except json.JSONDecodeError:
                save_config(DEFAULT_CONFIG)
                return DEFAULT_CONFIG.copy()
    if not isinstance(data, dict):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    return data


def save_config(config: Dict[str, Any]) -> None:
    with _LOCK:
        with CONFIG_FILE_PATH.open("w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2, ensure_ascii=False)


def get_parameter(key: str, default: Any = None) -> Any:
    config = load_config()
    return config.get(key, default)


def validate_parameter(key: str, value: Any) -> Any:
    if key not in DEFAULT_CONFIG:
        raise KeyError(f"Parámetro '{key}' no está definido")
    if not VALIDATORS[key](value):
        raise ValueError(f"Valor inválido para '{key}': {value}")
    if key in {"porcentaje_descuento_base", "porcentaje_comision", "error_rate_threshold"}:
        return float(value)
    return int(value)


def set_parameter(key: str, value: Any) -> Any:
    validated = validate_parameter(key, value)
    config = load_config()
    config[key] = validated
    save_config(config)
    return config[key]
