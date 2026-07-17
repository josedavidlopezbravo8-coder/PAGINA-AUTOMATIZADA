from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BatchSummary:
    batch_id: int
    filename: str
    status: str
    total_rows: int
    valid_rows: int
    error_rows: int
    error_rate: float


@dataclass
class QualitySummary:
    total_batches: int
    completed_batches: int
    failed_batches: int
    total_items_processed: int
    total_errors: int
    overall_error_rate: float
    batches: List[BatchSummary] = field(default_factory=list)


@dataclass
class ErrorDetail:
    row_number: int
    field: str
    message: str
    raw_value: Optional[str] = None


@dataclass
class BatchQualityReport:
    batch_id: int
    filename: str
    status: str
    total_rows: int
    valid_rows: int
    error_rows: int
    error_rate: float
    errors: List[ErrorDetail] = field(default_factory=list)


# Datos mock usados cuando inventory-service no está disponible
MOCK_BATCHES = [
    {
        "id": 1,
        "filename": "sample_inventory.csv",
        "status": "completed",
        "total_rows": 12,
        "valid_rows": 10,
        "error_rows": 2,
    },
    {
        "id": 2,
        "filename": "libros_enero.xlsx",
        "status": "completed",
        "total_rows": 50,
        "valid_rows": 48,
        "error_rows": 2,
    },
    {
        "id": 3,
        "filename": "lote_fallido.csv",
        "status": "failed",
        "total_rows": 5,
        "valid_rows": 0,
        "error_rows": 5,
    },
]

MOCK_ERRORS = {
    1: [
        {"row_number": 7,  "field": "title",    "message": "El título es obligatorio",         "raw_value": ""},
        {"row_number": 11, "field": "quantity",  "message": "La cantidad no puede ser negativa","raw_value": "-3"},
    ],
    2: [
        {"row_number": 22, "field": "isbn",  "message": "Formato ISBN inválido",         "raw_value": "12345"},
        {"row_number": 45, "field": "price", "message": "El precio no puede ser negativo","raw_value": "-10"},
    ],
    3: [
        {"row_number": i, "field": "book_reference", "message": "Referencia duplicada", "raw_value": f"REF-00{i}"}
        for i in range(1, 6)
    ],
}
