from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import AuditLog


router = APIRouter(
    prefix="/api/audit",
    tags=["Audit Trail"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def get_audit_trail(
    db: Session = Depends(get_db),
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return {
        "events": [
            {
                "id": log.id,
                "case_id": log.case_id,
                "event_type": log.event_type,
                "action": log.action,
                "actor": log.actor,
                "status": log.status,
                "description": log.description,
                "created_at": (
                    log.created_at.isoformat()
                    if log.created_at
                    else None
                ),
            }
            for log in logs
        ]
    }