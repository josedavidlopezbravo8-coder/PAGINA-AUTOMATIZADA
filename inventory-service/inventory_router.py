from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
from app.application.inventory_use_cases import process_inventory_file
from app.database import get_db
from app.domain.inventory import ImportError, InventoryItem

router = APIRouter()

@router.post("/inventario/subir", summary="Carga masiva de inventario desde CSV")
def upload_inventory(file: UploadFile, db: Session = Depends(get_db)):
    result = process_inventory_file(file, db)

    if isinstance(result, dict) and "error" in result:
        return result

    return {
        "id_lote": result.id,
        "filas_procesadas": result.processed_rows,
        "filas_validas": result.valid_rows,
        "filas_invalidas": result.invalid_rows
    }


@router.get("/lote/{id}/errores")
def get_errors(id: int, db: Session = Depends(get_db)):
    return db.query(ImportError).filter(ImportError.batch_id == id).all()


@router.get("/lote/{id}/productos")
def get_items(id: int, db: Session = Depends(get_db)):
    return db.query(InventoryItem).filter(InventoryItem.batch_id == id).all()