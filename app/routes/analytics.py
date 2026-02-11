from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import RequestLog
from app.db.session import SessionLocal

router = APIRouter(prefix="/analytics")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/top-keys")
def top_keys(db: Session = Depends(get_db)):
    rows = db.query(RequestLog.api_key).all()
    return [r[0] for r in rows]


@router.get("/requests")
def list_requests(db: Session = Depends(get_db)):
    logs = db.query(RequestLog).order_by(RequestLog.created_at.desc()).limit(50).all()

    return [
        {
            "id": log.id,
            "api_key": log.api_key,
            "path": log.path,
            "status_code": log.status_code,
            "cache_status": log.cache_status,
            "cache_key": log.cache_key,
            "cache_ttl": log.cache_ttl,
            "circuit_state": log.circuit_state,
            "circuit_blocked": log.circuit_blocked,
            "upstream_latency_ms": log.upstream_latency_ms,
            "upstream_error_type": log.upstream_error_type,
            "created_at": log.created_at,
        }
        for log in logs
    ]
