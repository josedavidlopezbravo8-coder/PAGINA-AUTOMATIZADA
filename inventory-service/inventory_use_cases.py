import csv
from sqlalchemy.orm import Session
from app.domain.inventory import InventoryItem, ImportBatch, ImportError


def process_inventory_file(file, db: Session):
    content = file.file.read().decode("utf-8-sig").splitlines()
    reader = csv.DictReader(content)

    required_columns = ["title", "author", "price", "stock"]

    for col in required_columns:
        if col not in reader.fieldnames:
            return {
                "error": f"Falta columna {col}",
                "columnas_detectadas": reader.fieldnames
            }

    batch = ImportBatch()
    db.add(batch)
    db.commit()
    db.refresh(batch)

    processed = 0
    valid = 0
    invalid = 0

    for i, row in enumerate(reader, start=1):
        processed += 1

        try:
            price = float(row["price"])
            stock = int(row["stock"])

            item = InventoryItem(
                title=row["title"].strip(),
                author=row["author"].strip(),
                price=price,
                stock=stock,
                condition=row.get("condition", "").strip(),
                defects=row.get("defects", "").strip(),
                batch_id=batch.id
            )

            db.add(item)
            valid += 1

        except Exception as e:
            error = ImportError(
                row_number=i,
                message=str(e),
                batch_id=batch.id
            )
            db.add(error)
            invalid += 1

    batch.processed_rows = processed
    batch.valid_rows = valid
    batch.invalid_rows = invalid

    db.commit()
    db.refresh(batch)

    return batch