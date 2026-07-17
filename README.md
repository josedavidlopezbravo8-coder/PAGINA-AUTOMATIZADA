# Ebook-AiCommerce

Proyecto independiente con las tareas **Dev7** y **Dev9** del Sprint 1 de BookFlow AI Commerce.

| Servicio            | Puerto | Descripción                                              |
|---------------------|--------|----------------------------------------------------------|
| data-quality-module | 8007   | Métricas de calidad sobre lotes de inventario (Dev7)     |
| bff-gateway         | 8009   | Proxy/gateway que enruta peticiones a microservicios (Dev9) |

> **Aislamiento:** `data-quality-module` llama al `inventory-service` vía HTTP.
> Como no está en este proyecto, usa **datos mock automáticamente** — sin errores.
> `bff-gateway` enruta `/api/quality/*` correctamente.
> Cualquier otra ruta devuelve **503 controlado en JSON**.

---

## Levantar el proyecto

```bash
# 1. Preparar variables de entorno (solo la primera vez)
cp .env.example .env

# 2. Construir imágenes y levantar ambos servicios
docker-compose up --build

# 3. Levantar un servicio por separado
docker-compose up --build data-quality-module
docker-compose up --build bff-gateway

# 4. Ver logs en tiempo real
docker-compose logs -f

# 5. Detener
docker-compose down
```

---

## Probar Dev7 — data-quality-module `:8007`

### Health check
```
GET http://localhost:8007/quality/health
```

### Resumen global de calidad
```
GET http://localhost:8007/quality/summary
```
Respuesta esperada (datos mock, inventory no está corriendo):
```json
{
  "total_batches": 3,
  "completed_batches": 2,
  "failed_batches": 1,
  "total_items_processed": 67,
  "total_errors": 9,
  "overall_error_rate": 0.1343,
  "batches": [...]
}
```

### Listar lotes con tasa de error
```
GET http://localhost:8007/quality/batches
```

### Reporte detallado de un lote
```
GET http://localhost:8007/quality/batches/1/report
```

### Lote inexistente (404 controlado)
```
GET http://localhost:8007/quality/batches/9999/report
```

---

## Probar Dev9 — bff-gateway `:8009`

### Health check del gateway
```
GET http://localhost:8009/health
```

### Enrutar a data-quality-module (funciona ✓)
```
GET http://localhost:8009/api/quality/summary
GET http://localhost:8009/api/quality/batches
GET http://localhost:8009/api/quality/batches/1/report
```

### Servicio no disponible (503 controlado)
```
GET http://localhost:8009/api/catalog/books/
```
Respuesta esperada:
```json
{
  "detail": "Servicio 'catalog' no disponible: ConnectError"
}
```

### Servicio no registrado (404 controlado)
```
GET http://localhost:8009/api/servicio-inventado/ruta
```

---

## Ejecutar tests

```bash
# Desde la carpeta del servicio
cd data-quality-module
pip install -r requirements.txt
pytest tests/ -v

cd ../bff-gateway
pip install -r requirements.txt
pytest tests/ -v
```

---

## Estructura del proyecto

```
Ebook-AiCommerce/
├── data-quality-module/        ← Dev7
│   ├── app/
│   │   ├── domain/quality.py          (modelos + datos mock)
│   │   ├── application/quality_use_cases.py  (lógica + fallback)
│   │   └── routers/quality_router.py  (endpoints)
│   ├── tests/test_quality.py
│   ├── Dockerfile
│   └── requirements.txt
├── bff-gateway/                ← Dev9
│   ├── app/
│   │   ├── proxy.py            (cliente HTTP con manejo de errores)
│   │   └── routers/gateway_router.py  (rutas del gateway)
│   ├── tests/test_gateway.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env                        ← gitignoreado
├── .env.example                ← plantilla para compartir
├── .gitignore
└── README.md
```
