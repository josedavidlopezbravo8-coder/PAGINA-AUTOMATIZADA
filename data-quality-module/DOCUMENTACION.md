# Módulo de Calidad de Datos — Documentación

## Historia de Usuario

> Como administrador, quiero consultar los errores de carga del inventario para identificar problemas y corregirlos.

--- 

## Descripción General

El `data-quality-module` es un microservicio FastAPI que expone endpoints para consultar la calidad de los lotes de inventario cargados. Cuando el `inventory-service` no está disponible, el módulo opera con datos mock internos de forma automática, lo que permite desarrollo y pruebas sin dependencias externas.

**Puerto:** `8007`  
**Prefijo de rutas:** `/quality`

---

## Arquitectura

```
data-quality-module/
├── app/
│   ├── main.py                        # Punto de entrada FastAPI
│   ├── domain/
│   │   └── quality.py                 # Entidades de dominio + datos mock
│   ├── application/
│   │   └── quality_use_cases.py       # Lógica de negocio (casos de uso)
│   └── routers/
│       └── quality_router.py          # Endpoints HTTP
├── tests/
│   └── test_quality.py                # Tests automáticos
├── requirements.txt
└── Dockerfile
```

---

## Estructura de Dominio (`ImportError`)

### `ErrorDetail`
Representa un error registrado por fila dentro de un lote.

| Campo        | Tipo            | Descripción                              |
|--------------|-----------------|------------------------------------------|
| `row_number` | `int`           | Número de fila donde ocurrió el error    |
| `field`      | `str`           | Campo del inventario que falló           |
| `message`    | `str`           | Descripción del error                    |
| `raw_value`  | `Optional[str]` | Valor original que causó el error        |

### `BatchQualityReport`
Reporte completo de un lote, incluyendo todos sus errores.

| Campo        | Tipo               | Descripción                          |
|--------------|--------------------|--------------------------------------|
| `batch_id`   | `int`              | Identificador del lote               |
| `filename`   | `str`              | Nombre del archivo cargado           |
| `status`     | `str`              | Estado del lote (`completed`/`failed`) |
| `total_rows` | `int`              | Total de filas procesadas            |
| `valid_rows` | `int`              | Filas sin error                      |
| `error_rows` | `int`              | Filas con error                      |
| `error_rate` | `float`            | Tasa de error (0.0 – 1.0)            |
| `errors`     | `List[ErrorDetail]`| Lista de errores por fila            |

---

## Endpoints

### `GET /quality/health`
Verificación de estado del servicio.

**Respuesta:**
```json
{"status": "ok", "service": "data-quality-module"}
```

---

### `GET /quality/batches`
Lista todos los lotes con su resumen de calidad.

**Respuesta:**
```json
[
  {
    "batch_id": 1,
    "filename": "sample_inventory.csv",
    "status": "completed",
    "total_rows": 12,
    "error_rate": 0.1667
  }
]
```

---

### `GET /quality/batches/{batch_id}/report`
Consulta los errores de un lote específico por `batch_id`. **Este es el endpoint principal de la historia de usuario.**

**Parámetro URL:** `batch_id` (integer)

**Respuesta exitosa (200):**
```json
{
  "batch_id": 1,
  "filename": "sample_inventory.csv",
  "status": "completed",
  "total_rows": 12,
  "valid_rows": 10,
  "error_rows": 2,
  "error_rate": 0.1667,
  "errors": [
    {
      "row_number": 7,
      "field": "title",
      "message": "El título es obligatorio",
      "raw_value": ""
    },
    {
      "row_number": 11,
      "field": "quantity",
      "message": "La cantidad no puede ser negativa",
      "raw_value": "-3"
    }
  ]
}
```

**Respuesta lote no encontrado (404):**
```json
{"detail": "Batch no encontrado"}
```

---

### `GET /quality/summary`
Resumen agregado de calidad sobre todos los lotes.

**Respuesta:**
```json
{
  "total_batches": 3,
  "completed_batches": 2,
  "failed_batches": 1,
  "total_items_processed": 67,
  "total_errors": 9,
  "overall_error_rate": 0.1343,
  "batches": [ ... ]
}
```

---

## Datos Mock

Cuando el `inventory-service` no responde, el módulo usa datos de prueba internos definidos en `domain/quality.py`:

| Lote | Archivo               | Estado      | Filas | Errores | Descripción del escenario     |
|------|-----------------------|-------------|-------|---------|-------------------------------|
| 1    | sample_inventory.csv  | completed   | 12    | 2       | Lote válido con errores leves |
| 2    | libros_enero.xlsx     | completed   | 50    | 2       | ISBN inválido y precio negativo |
| 3    | lote_fallido.csv      | failed      | 5     | 5       | Todas las filas con error (archivo inválido) |

---

## Levantar el Servicio

### Con Docker Compose

```bash
cd Ebook-AiCommerce

# Construir e iniciar
docker compose up --build -d data-quality-module

# Ver logs en tiempo real
docker compose logs -f data-quality-module
```

El servicio queda disponible en `http://localhost:8007`.

### Localmente (desarrollo)

```bash
cd Ebook-AiCommerce/data-quality-module

pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8007 --reload
```

---

## Pruebas Manuales

### 1. Verificar que el servicio responde
```bash
curl http://localhost:8007/quality/health
```

### 2. Consultar errores de un lote (criterio principal)
```bash
curl http://localhost:8007/quality/batches/1/report
```

### 3. Simular archivo inválido (lote fallido completo)
```bash
curl http://localhost:8007/quality/batches/3/report
```
Devuelve 5 errores — todas las filas del lote fallaron.

### 4. Verificar respuesta 404 para lote inexistente
```bash
curl http://localhost:8007/quality/batches/9999/report
```

### 5. Listar todos los lotes disponibles
```bash
curl http://localhost:8007/quality/batches
```

---

## Pruebas Automáticas

```bash
cd Ebook-AiCommerce/data-quality-module

pytest tests/ -v
```

**Salida esperada:**
```
tests/test_quality.py::test_health                     PASSED
tests/test_quality.py::test_summary_uses_mock_fallback PASSED
tests/test_quality.py::test_list_batches_fallback      PASSED
tests/test_quality.py::test_batch_report_fallback      PASSED
tests/test_quality.py::test_batch_not_found            PASSED

5 passed
```

---

## Criterios de Aceptación — Verificación

| Criterio                                    | Cómo se cumple                                                    | Archivo                          |
|---------------------------------------------|-------------------------------------------------------------------|----------------------------------|
| Se pueden consultar errores por lote        | `GET /quality/batches/{batch_id}/report`                          | `routers/quality_router.py:52`   |
| Cada error muestra fila y descripción       | Campos `row_number` y `message` en `ErrorDetail`                  | `domain/quality.py:27`           |
| Los errores quedan almacenados              | Persistidos en `inventory-service` o en `MOCK_ERRORS` como fallback | `domain/quality.py:75`          |
| Se puede consultar errores por `batch_id`   | Parámetro `{batch_id}` en la URL del endpoint                     | `routers/quality_router.py:52`   |
| Permite identificar problemas de calidad    | Campos `field` y `raw_value` muestran el origen exacto del error  | `domain/quality.py:28`           |

---

## Variables de Entorno

| Variable               | Valor por defecto                   | Descripción                        |
|------------------------|-------------------------------------|------------------------------------|
| `INVENTORY_SERVICE_URL`| `http://inventory-service:8002`     | URL del servicio de inventario     |

Si `INVENTORY_SERVICE_URL` no responde, el módulo usa datos mock automáticamente sin necesidad de configuración adicional.
