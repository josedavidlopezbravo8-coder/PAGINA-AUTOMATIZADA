# Catalog Service

Servicio de catálogo para gestión de libros y categorías en el proyecto Ebook-AiCommerce.

## Descripción

Este microservicio proporciona una API REST para:
- Crear y listar libros
- Gestionar categorías
- Obtener estadísticas de libros por categoría
- Contar libros totales

## Tecnologías

- **Node.js** con Express.js
- **PostgreSQL** como base de datos
- **Docker** para contenerización

## Estructura del Proyecto

```
catalog-service/
├── Dockerfile          # Configuración de Docker
├── index.js            # Servidor principal
├── package.json        # Dependencias de Node.js
├── .env                # Variables de entorno (local)
├── .env.example        # Ejemplo de configuración
├── scripts/
│   └── init-db.js      # Script de inicialización de BD
└── node_modules/       # Dependencias instaladas
```

## Endpoints de la API

### Libros

#### Crear un libro
- **POST** `/books`
- **Body** (JSON):
  ```json
  {
    "title": "Título del libro",
    "author": "Autor del libro",
    "category": "Nombre de la categoría (opcional)",
    "isbn": "ISBN (opcional)",
    "issn": "ISSN (opcional)"
  }
  ```
- **Respuesta** (201 Created):
  ```json
  {
    "id": 1,
    "title": "Título del libro",
    "author": "Autor del libro",
    "isbn": null,
    "issn": null,
    "created_at": "2026-04-04T...",
    "updated_at": "2026-04-04T...",
    "category": "Nombre de la categoría"
  }
  ```

#### Listar libros
- **GET** `/books`
- **Query params** (opcionales):
  - `page`: Número de página (default: 1)
  - `limit`: Elementos por página (default: 10, max: 100)
  - `q`: Búsqueda por título o autor
  - `category`: Filtrar por categoría
- **Respuesta** (200 OK):
  ```json
  {
    "page": 1,
    "limit": 10,
    "total": 25,
    "results": [
      {
        "id": 1,
        "title": "Título",
        "author": "Autor",
        "isbn": null,
        "issn": null,
        "category": { "id": 1, "name": "Categoría" },
        "created_at": "2026-04-04T...",
        "updated_at": "2026-04-04T..."
      }
    ]
  }
  ```

#### Contar libros totales
- **GET** `/books/count`
- **Respuesta** (200 OK):
  ```json
  {
    "total": 25
  }
  ```

#### Obtener libro por ID
- **GET** `/books/:id`
- **Parámetros**: `id` (número entero positivo)
- **Respuesta** (200 OK):
  ```json
  {
    "id": 1,
    "title": "Título",
    "author": "Autor",
    "isbn": null,
    "issn": null,
    "category": { "id": 1, "name": "Categoría" },
    "created_at": "2026-04-04T...",
    "updated_at": "2026-04-04T..."
  }
  ```

#### Estadísticas por categoría (con mínimo)
- **GET** `/books/genres/minimum`
- **Query params**: `min` (mínimo de libros por categoría, default: 2)
- **Respuesta** (200 OK):
  ```json
  [
    {
      "id": 1,
      "name": "Categoría",
      "book_count": 5
    }
  ]
  ```

#### Estadísticas por categoría (todos)
- **GET** `/books/genres/count`
- **Respuesta** (200 OK):
  ```json
  [
    {
      "id": 1,
      "name": "Categoría",
      "book_count": 5
    }
  ]
  ```

### Categorías

#### Listar categorías
- **GET** `/categories`
- **Respuesta** (200 OK):
  ```json
  [
    {
      "id": 1,
      "name": "Categoría",
      "created_at": "2026-04-04T...",
      "updated_at": "2026-04-04T..."
    }
  ]
  ```

#### Crear categoría
- **POST** `/categories`
- **Body** (JSON):
  ```json
  {
    "name": "Nombre de la categoría"
  }
  ```
- **Respuesta** (201 Created):
  ```json
  {
    "id": 1,
    "name": "Nombre de la categoría",
    "created_at": "2026-04-04T...",
    "updated_at": "2026-04-04T..."
  }
  ```

## Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y configura:

```bash
# Base de datos
DATABASE_URL=postgres://postgres:1234@localhost:5432/catalog

# Puerto del servidor
PORT=3000
```

### Base de Datos

El servicio requiere PostgreSQL. Las tablas se crean automáticamente al iniciar.

Esquema:
- `categories`: id, name, created_at, updated_at
- `books`: id, title, author, category_id, isbn, issn, created_at, updated_at

## Ejecución

### Localmente

1. Instalar dependencias:
   ```bash
   npm install
   ```

2. Configurar PostgreSQL localmente.

3. Copiar y configurar `.env`.

4. Ejecutar:
   ```bash
   npm start
   ```

El servidor estará en `http://localhost:3000`.

### Con Docker

1. Desde la raíz del proyecto (`Ebook-AiCommerce`):
   ```bash
   docker-compose up --build
   ```

Esto levantará:
- PostgreSQL en puerto 5432
- Catalog Service en puerto 3000
- Otros servicios del proyecto

## Desarrollo

### Scripts disponibles

- `npm start`: Inicia el servidor
- `npm run dev`: Inicia con nodemon (desarrollo)
- `npm run ensure-db`: Inicializa la base de datos (requiere conexión)

### Migraciones

Las migraciones se ejecutan automáticamente al iniciar el servidor.

## Integración

Este servicio se integra con:
- `bff-gateway`: Expone endpoints al frontend
- `data-quality-module`: Procesa datos de calidad

Configurar en `bff-gateway`:
```bash
CATALOG_SERVICE_URL=http://catalog-service:3000
```

## Notas

- Las categorías se crean automáticamente al crear libros si no existen.
- Los campos `isbn` e `issn` son opcionales.
- La paginación en `/books` es automática.
- Errores comunes: 400 (datos inválidos), 404 (no encontrado), 500 (error interno).
