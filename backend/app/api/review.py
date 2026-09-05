from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import AuditLog, HumanReview, RevenueCase, Customer


router = APIRouter(
    prefix="/api/review",
    tags=["Human Review"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RejectRequest(BaseModel):
    reason: str


def review_to_dict(review: HumanReview, case=None, customer=None):
    return {
        "id": review.id,
        "case_id": review.case_id,
        "reason": review.reason,
        "recommendation": review.recommendation,
        "status": review.status,
        "reviewer": review.reviewer,
        "review_reason": review.review_reason,
        "customer_id": case.customer_id if case else None,
        "customer_name": customer.name if customer else "Unknown customer",
        "amount": float(case.amount or 0) if case else 0,
        "risk_score": float(case.risk_score or 0) if case else 0,
        "scenario": case.scenario if case else None,
        "action": case.action if case else review.recommendation,
        "created_at": (
            review.created_at.isoformat()
            if review.created_at
            else None
        ),
        "reviewed_at": (
            review.reviewed_at.isoformat()
            if review.reviewed_at
            else None
        ),
    }


@router.get("")
def get_review_cases(
    db: Session = Depends(get_db),
):
    reviews = (
        db.query(HumanReview)
        .order_by(HumanReview.created_at.desc())
        .all()
    )

    result = []

    for review in reviews:
        case = (
            db.query(RevenueCase)
            .filter(RevenueCase.case_id == review.case_id)
            .first()
        )

        customer = None

        if case and case.customer_id:
            customer = (
                db.query(Customer)
                .filter(Customer.customer_id == case.customer_id)
                .first()
            )

        result.append(
            review_to_dict(
                review,
                case,
                customer,
            )
        )

    return {
        "cases": result
    }


@router.post("/{case_id}/approve")
def approve_review(
    case_id: str,
    db: Session = Depends(get_db),
):
    review = (
        db.query(HumanReview)
        .filter(
            HumanReview.case_id == case_id,
            HumanReview.status == "pending",
        )
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Pending human review not found",
        )

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

    review.status = "approved"
    review.reviewer = "Human Reviewer"
    review.reviewed_at = datetime.utcnow()

    case.status = "approved"
    case.updated_at = datetime.utcnow()

    audit = AuditLog(
        case_id=case_id,
        event_type="human_review",
        action="approve",
        actor="Human Reviewer",
        status="approved",
        description=(
            "Recovery recommendation approved "
            "by human reviewer."
        ),
        created_at=datetime.utcnow(),
    )

    db.add(audit)
    db.commit()

    return {
        "status": "approved",
        "case_id": case_id,
        "message": "Recovery recommendation approved.",
    }


@router.post("/{case_id}/reject")
def reject_review(
    case_id: str,
    request: RejectRequest,
    db: Session = Depends(get_db),
):
    review = (
        db.query(HumanReview)
        .filter(
            HumanReview.case_id == case_id,
            HumanReview.status == "pending",
        )
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Pending human review not found",
        )

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

    reason = request.reason.strip()

    if not reason:
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required",
        )

    review.status = "rejected"
    review.reviewer = "Human Reviewer"
    review.review_reason = reason
    review.reviewed_at = datetime.utcnow()

    case.status = "rejected"
    case.updated_at = datetime.utcnow()

    audit = AuditLog(
        case_id=case_id,
        event_type="human_review",
        action="reject",
        actor="Human Reviewer",
        status="rejected",
        description=(
            f"Recovery recommendation rejected. "
            f"Reason: {reason}"
        ),
        created_at=datetime.utcnow(),
    )

    db.add(audit)
    db.commit()

    return {
        "status": "rejected",
        "case_id": case_id,
        "reason": reason,
        "message": "Recovery recommendation rejected.",
    }
