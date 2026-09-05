from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import RevenueCase


router = APIRouter(
    prefix="/api/cases",
    tags=["Cases"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def case_to_dict(case: RevenueCase):
    return {
        "id": case.case_id,
        "case_id": case.case_id,
        "customer_id": case.customer_id,
        "scenario": case.scenario,
        "event_type": case.event_type,
        "amount": float(case.amount or 0),
        "risk_score": float(case.risk_score or 0),
        "diagnosis": case.diagnosis,
        "decision": case.decision,
        "policy_result": case.policy_result,
        "action": case.action,
        "status": case.status,
        "payment_status": case.payment_status,
        "failure_reason": case.failure_reason,
        "retry_count": case.retry_count or 0,
        "created_at": (
            case.created_at.isoformat()
            if case.created_at
            else None
        ),
        "updated_at": (
            case.updated_at.isoformat()
            if case.updated_at
            else None
        ),
    }


@router.get("")
def get_cases(
    db: Session = Depends(get_db),
):
    cases = (
        db.query(RevenueCase)
        .order_by(RevenueCase.created_at.desc())
        .all()
    )

    return {
        "cases": [
            case_to_dict(case)
            for case in cases
        ]
    }


@router.get("/{case_id}")
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = (
        db.query(RevenueCase)
        .filter(
            RevenueCase.case_id == case_id
        )
        .first()
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Revenue case not found",
        )

    return {
        "case": case_to_dict(case)
    }