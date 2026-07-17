import os
import httpx
from typing import List, Optional
from app.domain.quality import (
    BatchSummary, QualitySummary, ErrorDetail, BatchQualityReport,
    MOCK_BATCHES, MOCK_ERRORS,
)

INVENTORY_BASE = os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8002")
TIMEOUT = 3.0


def _batch_to_summary(b: dict) -> BatchSummary:
    total  = b.get("processed_rows") or b.get("total_rows", 0)
    errors = b.get("invalid_rows")   or b.get("error_rows", 0)
    valid  = b.get("valid_rows", 0)
    rate   = round(errors / total, 4) if total else 0.0
    return BatchSummary(
        batch_id=b["id"],
        filename=b.get("file_name") or b.get("filename", ""),
        status=b.get("status", ""),
        total_rows=total,
        valid_rows=valid,
        error_rows=errors,
        error_rate=rate,
    )


async def get_quality_summary() -> QualitySummary:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{INVENTORY_BASE}/batches/")
            r.raise_for_status()
            batches_raw = r.json()
    except Exception:
        batches_raw = MOCK_BATCHES

    summaries  = [_batch_to_summary(b) for b in batches_raw]
    completed  = sum(1 for s in summaries if s.status == "completed")
    failed     = sum(1 for s in summaries if s.status == "failed")
    total_items  = sum(s.total_rows  for s in summaries)
    total_errors = sum(s.error_rows  for s in summaries)
    overall_rate = round(total_errors / total_items, 4) if total_items else 0.0

    return QualitySummary(
        total_batches=len(summaries),
        completed_batches=completed,
        failed_batches=failed,
        total_items_processed=total_items,
        total_errors=total_errors,
        overall_error_rate=overall_rate,
        batches=summaries,
    )


async def get_batch_report(batch_id: int) -> Optional[BatchQualityReport]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r_batch  = await client.get(f"{INVENTORY_BASE}/batches/{batch_id}")
            r_batch.raise_for_status()
            batch_raw = r_batch.json()

            r_errors  = await client.get(f"{INVENTORY_BASE}/batches/{batch_id}/errors")
            r_errors.raise_for_status()
            errors_raw = r_errors.json()
    except Exception:
        batch_raw = next((b for b in MOCK_BATCHES if b["id"] == batch_id), None)
        if batch_raw is None:
            return None
        errors_raw = MOCK_ERRORS.get(batch_id, [])

    total  = batch_raw.get("processed_rows") or batch_raw.get("total_rows", 0)
    errors_count = batch_raw.get("invalid_rows") or batch_raw.get("error_rows", 0)
    rate   = round(errors_count / total, 4) if total else 0.0

    errors = [
        ErrorDetail(
            row_number=e.get("row_number", 0),
            field=e.get("field") or e.get("error_type", ""),
            message=e.get("message", ""),
            raw_value=e.get("raw_value") or e.get("raw_data"),
        )
        for e in errors_raw
    ]

    return BatchQualityReport(
        batch_id=batch_id,
        filename=batch_raw.get("file_name") or batch_raw.get("filename", ""),
        status=batch_raw.get("status", ""),
        total_rows=total,
        valid_rows=batch_raw.get("valid_rows", 0),
        error_rows=errors_count,
        error_rate=rate,
        errors=errors,
    )
