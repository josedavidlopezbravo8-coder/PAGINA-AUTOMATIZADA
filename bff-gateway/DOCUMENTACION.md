# BFF Gateway — Documentación

## Historia de Usuario

> Como sistema, quiero centralizar el acceso del frontend a los microservicios para simplificar contratos y desacoplar la interfaz del backend interno.

---

## Descripción General

El `bff-gateway` es un API Gateway / BFF (Backend For Frontend) implementado con FastAPI. Actúa como **punto único de entrada** para el frontend: recibe todas las peticiones HTTP y las reenvía (proxy) al microservicio correspondiente sin añadir lógica de negocio.

Cuando un microservicio no está disponible, el gateway devuelve un `503` controlado en lugar de propagar el error de red al cliente.

**Puerto:** `8009`  
**Patrón de ruta:** `/api/{servicio}/{ruta}`

---

## Arquitectura

```
Frontend
   │
   ▼
bff-gateway :8009          ← punto único de entrada
   │
   ├── /api/auth/...       →  auth-service        :8001
   ├── /api/inventory/...  →  inventory-service   :8002
   ├── /api/catalog/...    →  catalog-service     :8003
   ├── /api/enrichment/... →  ai-enrichment-mock  :8006
   ├── /api/quality/...    →  data-quality-module :8007
   └── /api/config/...     →  config-module       :8008
```

### Estructura de archivos

```
bff-gateway/
├── app/
│   ├── main.py                  # Punto de entrada FastAPI + CORS
│   ├── proxy.py                 # Lógica de proxy genérico (SERVICE_MAP + proxy_request)
│   └── routers/
│       └── gateway_router.py    # Definición de rutas /health y /api/{service}/{path}
├── tests/
│   └── test_gateway.py          # Tests automáticos
├── requirements.txt
└── Dockerfile
```

**Principio de diseño clave:** el gateway no contiene lógica de negocio. Todo el comportamiento está en `proxy.py`, que reenvía la petición original (método, headers, body, query params) tal cual al servicio destino.

---

## Componentes

### `proxy.py` — Motor de enrutamiento

Define el `SERVICE_MAP`: diccionario que asocia cada nombre de servicio a su URL base (configurable por variable de entorno).

```python
SERVICE_MAP = {
    "auth":       AUTH_SERVICE_URL,       # http://auth-service:8001
    "inventory":  INVENTORY_SERVICE_URL,  # http://inventory-service:8002
    "catalog":    CATALOG_SERVICE_URL,    # http://catalog-service:8003
    "enrichment": AI_ENRICHMENT_URL,      # http://ai-enrichment-mock:8006
    "quality":    DATA_QUALITY_URL,       # http://data-quality-module:8007
    "config":     CONFIG_MODULE_URL,      # http://config-module:8008
}
```

La función `proxy_request` reenvía la petición completa al upstream y retorna su respuesta sin modificarla. Captura `ConnectError` y `TimeoutException` para devolver `503` en lugar de un error no controlado.

### `gateway_router.py` — Rutas expuestas

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Estado del gateway y lista de servicios registrados |
| `GET/POST/PUT/DELETE/PATCH` | `/api/{service}/{path}` | Proxy hacia el microservicio |
| `GET/POST/PUT/DELETE/PATCH` | `/api/{service}` | Proxy hacia la raíz del microservicio |

### `main.py` — Configuración de la app

Registra middleware CORS con `allow_origins=["*"]` para permitir que cualquier frontend consuma el gateway sin restricciones de origen durante el desarrollo.

---

## Endpoints

### `GET /health`
Verifica el estado del gateway y lista los servicios registrados.

**Respuesta:**
```json
{
  "status": "ok",
  "service": "bff-gateway",
  "routes": ["auth", "inventory", "catalog", "enrichment", "quality", "config"],
  "note": "En este proyecto solo 'quality' está activo. Los demás devuelven 503 controlado."
}
```

---

### `GET|POST|PUT|DELETE|PATCH /api/{service}/{path}`
Proxy genérico. El gateway reenvía la petición al microservicio mapeado.

**Ejemplo — consultar errores de un lote vía gateway:**
```
GET /api/quality/quality/batches/1/report
    └── redirige a → http://data-quality-module:8007/quality/batches/1/report
```

**Ejemplo — listar libros del catálogo:**
```
GET /api/catalog/books/
    └── redirige a → http://catalog-service:8003/books/
```

---

## Manejo de Errores

| Situación | Código HTTP | Mensaje |
|-----------|-------------|---------|
| Servicio no registrado en `SERVICE_MAP` | `404` | `"Servicio '{name}' no registrado"` |
| Servicio registrado pero no disponible (timeout / conexión rechazada) | `503` | `"Servicio '{name}' no disponible: {tipo_error}"` |
| El microservicio upstream devuelve un error | Se propaga tal cual | El gateway retorna el mismo código y body del upstream |

---

## Variables de Entorno

| Variable | Valor por defecto | Servicio destino |
|---|---|---|
| `AUTH_SERVICE_URL` | `http://auth-service:8001` | Autenticación |
| `INVENTORY_SERVICE_URL` | `http://inventory-service:8002` | Inventario |
| `CATALOG_SERVICE_URL` | `http://catalog-service:8003` | Catálogo |
| `AI_ENRICHMENT_URL` | `http://ai-enrichment-mock:8006` | Enriquecimiento IA |
| `DATA_QUALITY_URL` | `http://data-quality-module:8007` | Calidad de datos |
| `CONFIG_MODULE_URL` | `http://config-module:8008` | Configuración |

---

## Levantar el Servicio

### Con Docker Compose (junto al data-quality-module)

```bash
cd Ebook-AiCommerce

# Levanta ambos servicios
docker compose up --build -d

# Ver logs del gateway
docker compose logs -f bff-gateway
```

El gateway queda disponible en `http://localhost:8009` y ya puede enrutar a `data-quality-module` en la red interna Docker.

### Localmente (desarrollo)

```bash
cd Ebook-AiCommerce/bff-gateway

pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload
```

---

## Pruebas Manuales

### 1. Verificar que el gateway responde
```bash
curl http://localhost:8009/health
```

### 2. Enrutar al data-quality-module a través del gateway
```bash
# Health del módulo de calidad via gateway
curl http://localhost:8009/api/quality/quality/health

# Errores de un lote via gateway
curl http://localhost:8009/api/quality/quality/batches/1/report

# Resumen de calidad via gateway
curl http://localhost:8009/api/quality/quality/summary
```

### 3. Servicio no registrado → 404
```bash
curl http://localhost:8009/api/servicio-inexistente/ruta
# {"detail":"Servicio 'servicio-inexistente' no registrado"}
```

### 4. Servicio registrado pero no disponible → 503
```bash
curl http://localhost:8009/api/catalog/books/
# {"detail":"Servicio 'catalog' no disponible: ConnectError"}
```

### 5. Inventario no disponible → 503 controlado
```bash
curl http://localhost:8009/api/inventory/
# {"detail":"Servicio 'inventory' no disponible: ConnectError"}
```

---

## Pruebas Automáticas

```bash
cd Ebook-AiCommerce/bff-gateway

pytest tests/ -v
```

**Salida esperada:**
```
tests/test_gateway.py::test_health                         PASSED
tests/test_gateway.py::test_unknown_service_returns_404    PASSED
tests/test_gateway.py::test_unavailable_service_returns_503 PASSED
tests/test_gateway.py::test_unavailable_inventory_returns_503 PASSED

4 passed
```

---

## Criterios de Aceptación — Verificación

| Criterio | Cómo se cumple | Archivo |
|---|---|---|
| El frontend consume servicios a través del gateway | Todas las rutas pasan por `/api/{service}/...` en el puerto `8009` | `routers/gateway_router.py:17` |
| El gateway enruta correctamente | `SERVICE_MAP` + `proxy_request` reenvían la petición al upstream | `proxy.py:9-48` |
| Maneja errores | `503` para servicio no disponible, `404` para servicio no registrado | `proxy.py:22,44` |
| Centraliza acceso | Único `docker-compose.yml`, un solo puerto expuesto al exterior (`8009`) | `docker-compose.yml` |
| El frontend solo consume endpoints del BFF | Solo el puerto `8009` está mapeado al host; los demás servicios son internos | `docker-compose.yml` |
| El BFF enruta a auth, inventory y catalog | `SERVICE_MAP` registra `auth`, `inventory`, `catalog` (y más) | `proxy.py:10-12` |
| No contiene lógica de negocio | `gateway_router.py` solo delega a `proxy_request`; sin transformaciones | `routers/gateway_router.py:18-24` |

---

## Relación con el data-quality-module

Ambos servicios corren en la red Docker `ebook-network`. El gateway depende de `data-quality-module` en el `docker-compose.yml` (`depends_on`). El frontend accede a los reportes de calidad así:

```
Frontend → GET http://localhost:8009/api/quality/quality/batches/1/report
              ↓ proxy
           data-quality-module → GET http://data-quality-module:8007/quality/batches/1/report
```
