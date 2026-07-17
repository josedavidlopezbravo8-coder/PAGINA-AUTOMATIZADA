from fastapi import APIRouter, HTTPException
from app.application.quality_use_cases import get_quality_summary, get_batch_report

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "data-quality-module"}


@router.get("/summary")
async def quality_summary():
    summary = await get_quality_summary()
    return {
        "total_batches": summary.total_batches,
        "completed_batches": summary.completed_batches,
        "failed_batches": summary.failed_batches,
        "total_items_processed": summary.total_items_processed,
        "total_errors": summary.total_errors,
        "overall_error_rate": summary.overall_error_rate,
        "batches": [
            {
                "batch_id": b.batch_id,
                "filename": b.filename,
                "status": b.status,
                "total_rows": b.total_rows,
                "valid_rows": b.valid_rows,
                "error_rows": b.error_rows,
                "error_rate": b.error_rate,
            }
            for b in summary.batches
        ],
    }


@router.get("/batches")
async def list_batches():
    summary = await get_quality_summary()
    return [
        {
            "batch_id": b.batch_id,
            "filename": b.filename,
            "status": b.status,
            "total_rows": b.total_rows,
            "error_rate": b.error_rate,
        }
        for b in summary.batches
    ]


@router.get("/batches/{batch_id}/report")
async def batch_report(batch_id: int):
    report = await get_batch_report(batch_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Batch no encontrado")
    return {
        "batch_id": report.batch_id,
        "filename": report.filename,
        "status": report.status,
        "total_rows": report.total_rows,
        "valid_rows": report.valid_rows,
        "error_rows": report.error_rows,
        "error_rate": report.error_rate,
        "errors": [
            {
                "row_number": e.row_number,
                "field": e.field,
                "message": e.message,
                "raw_value": e.raw_value,
            }
            for e in report.errors
        ],
    }
