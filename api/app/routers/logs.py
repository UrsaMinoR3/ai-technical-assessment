from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.auth import verify_api_key
from ..core.database import get_db
from ..models.request_log import RequestLog

router = APIRouter()


@router.get(
    "/logs",
    summary="Request Logs",
    description="Returns all tracked API requests from PostgreSQL. Requires X-API-Key.",
)
async def get_logs(
    limit: int = 100,
    _: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(RequestLog)
        .order_by(RequestLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "endpoint": r.endpoint,
            "input_data": r.input_data,
            "output_ref": r.output_ref,
            "external_usage": r.external_usage,
            "latency_ms": round(r.latency_ms, 2) if r.latency_ms else None,
            "http_status": r.http_status,
        }
        for r in rows
    ]
