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
bff-gateway :8009
   │
   ├── /api/auth/...       →  auth-service        :8001
   ├── /api/inventory/...  →  inventory-service   :8002
   ├── /api/catalog/...    →  catalog-service     :8003
   ├── /api/enrichment/... →  ai-enrichment-mock  :8006
   ├── /api/quality/...    →  data-quality-module :8007
   └── /api/config/...     →  config-module       :8008
```

---

## 🆕 Módulo de Inventario (Aporte Individual)

### Autor

Camilo Velasco

### Descripción

Se desarrolló un módulo de inventario encargado de procesar archivos CSV con información de productos. Este módulo permite validar datos, almacenar productos válidos y registrar errores encontrados durante el procesamiento.

---

### Funcionalidades implementadas

* Carga de archivos CSV
* Validación de datos (precio, stock)
* Registro de errores por fila
* Almacenamiento de productos válidos
* Consulta de productos procesados
* Consulta de errores por lote

---

### Endpoints principales

#### POST /inventario/subir

Permite subir un archivo CSV con productos y procesarlo.

Respuesta:

* Cantidad de filas procesadas
* Filas válidas
* Filas inválidas

---

#### GET /lote/{id}/errores

Retorna los errores encontrados en un lote procesado.

---

#### GET /lote/{id}/productos

Retorna los productos válidos almacenados en el sistema.

---

### Ejemplo de funcionamiento

* Se sube un archivo CSV con productos
* El sistema valida cada fila
* Los errores se almacenan con detalle
* Los productos válidos se guardan correctamente
* Se pueden consultar ambos resultados mediante endpoints

---

### Tecnologías utilizadas

* FastAPI
* Python
* Docker

---

### Integración con el sistema

El módulo de inventario se integra con el sistema principal mediante el API Gateway, permitiendo acceder a sus endpoints desde:

```
http://localhost:8009/api/inventory/
```

---

### Relación con otros módulos

El módulo de inventario trabaja en conjunto con:

* Data Quality Module
* BFF Gateway

---

## Componentes

### `proxy.py` — Motor de enrutamiento

Define el `SERVICE_MAP`: diccionario que asocia cada nombre de servicio a su URL base.

```python
SERVICE_MAP = {
    "auth":       AUTH_SERVICE_URL,
    "inventory":  INVENTORY_SERVICE_URL,
    "catalog":    CATALOG_SERVICE_URL,
    "enrichment": AI_ENRICHMENT_URL,
    "quality":    DATA_QUALITY_URL,
    "config":     CONFIG_MODULE_URL,
}
```

---

## Endpoints del Gateway

### `GET /health`

Verifica el estado del gateway.

---

### `/api/{service}/{path}`

Proxy hacia microservicios.

---

## Manejo de Errores

| Situación              | Código |
| ---------------------- | ------ |
| Servicio no registrado | 404    |
| Servicio no disponible | 503    |

---

## Ejecución

```bash
docker compose up --build -d
```

---

## Pruebas

```bash
curl http://localhost:8009/health
```

---

## Conclusión

Se implementó un módulo de inventario funcional integrado a una arquitectura de microservicios mediante un API Gateway, permitiendo una gestión eficiente y centralizada de datos.
