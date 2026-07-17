import os
import httpx
from fastapi import Request, Response, HTTPException

TIMEOUT = 5.0

# En este proyecto solo están activos quality y (opcionalmente) los demás.
# Si un servicio no está corriendo, el gateway devuelve 503 controlado.
SERVICE_MAP = {
    "auth":      os.getenv("AUTH_SERVICE_URL",      "http://auth-service:8001"),
    "inventory": os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8002"),
    "catalog":   os.getenv("CATALOG_SERVICE_URL",   "http://catalog-service:8003"),
    "enrichment":os.getenv("AI_ENRICHMENT_URL",     "http://ai-enrichment-mock:8006"),
    "quality":   os.getenv("DATA_QUALITY_URL",      "http://data-quality-module:8007"),
    "config":    os.getenv("CONFIG_MODULE_URL",      "http://config-module:8008"),
}


async def proxy_request(service_name: str, path: str, request: Request) -> Response:
    base_url = SERVICE_MAP.get(service_name)
    if base_url is None:
        raise HTTPException(status_code=404, detail=f"Servicio '{service_name}' no registrado")

    url = f"{base_url}/{path}" if path else base_url
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "content-length")}

    try:
        body = await request.body()
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            upstream = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=dict(request.query_params),
            )
        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers=dict(upstream.headers),
            media_type=upstream.headers.get("content-type", "application/json"),
        )
    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Servicio '{service_name}' no disponible: {type(exc).__name__}",
        )
