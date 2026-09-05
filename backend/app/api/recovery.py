from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..agents.recovery import recovery_agent
from ..database import SessionLocal
from ..models import (
    AuditLog,
    Customer,
    HumanReview,
    RecoveryAction,
    RevenueCase,
)
from ..policy.rules import policy_engine
from ..services.verification import verification_service


router = APIRouter(
    prefix="/api/recovery",
    tags=["Recovery"],
)


class RecoveryRequest(BaseModel):
    action: str


class PaymentVerificationRequest(BaseModel):
    payment_link_id: str


@router.post("/{case_id}")
def execute_recovery(
    case_id: str,
    request: RecoveryRequest,
):
    db: Session = SessionLocal()

    try:
        case = (
            db.query(RevenueCase)
            .filter(RevenueCase.case_id == case_id)
            .first()
        )

        if not case:
            raise HTTPException(
                status_code=404,
                detail="Revenue case not found",
            )

        if case.status == "recovered":
            return {
                "success": False,
                "status": "already_recovered",
                "message": "This case has already been recovered.",
            }

        customer = (
            db.query(Customer)
            .filter(
                Customer.customer_id == case.customer_id
            )
            .first()
        )

        customer_name = (
            customer.name
            if customer
            else "REVIVE Customer"
        )

        customer_email = (
            customer.email
            if customer
            else None
        )

        # -----------------------------------------
        # 1. POLICY ENGINE
        # -----------------------------------------

        policy_result = policy_engine.evaluate(
            action=request.action,
            amount=float(case.amount),
            risk_score=float(case.risk_score),
            retry_count=int(case.retry_count or 0),
        )

        case.policy_result = policy_result.get(
            "decision",
            "unknown",
        )

        # -----------------------------------------
        # 2. BLOCKED ACTION
        # -----------------------------------------

        if not policy_result.get("approved", False) and policy_result.get("action") != "human_escalation":
            case.status = "blocked"

            db.add(
                AuditLog(
                    case_id=case.case_id,
                    event_type="policy_block",
                    action=request.action,
                    actor="policy_engine",
                    status="blocked",
                    description=policy_result.get(
                        "reason",
                        "Recovery action blocked by policy.",
                    ),
                )
            )

            db.commit()

            return {
                "success": False,
                "status": "blocked",
                "policy": policy_result,
            }

        approved_action = policy_result.get(
            "action",
            request.action,
        )

        # -----------------------------------------
        # 3. HUMAN ESCALATION
        # -----------------------------------------

        if approved_action == "human_escalation":
            review = HumanReview(
                case_id=case.case_id,
                reason=policy_result.get(
                    "reason",
                    "Human review required.",
                ),
                recommendation=approved_action,
                status="pending",
            )

            case.status = "human_review"
            case.action = approved_action

            db.add(review)

            db.add(
                AuditLog(
                    case_id=case.case_id,
                    event_type="human_escalation",
                    action=approved_action,
                    actor="policy_engine",
                    status="pending",
                    description=policy_result.get(
                        "reason",
                        "Case escalated for human review.",
                    ),
                )
            )

            db.commit()

            return {
                "success": True,
                "status": "human_review",
                "action": approved_action,
                "policy": policy_result,
            }

        # -----------------------------------------
        # 4. EXECUTE RECOVERY
        # -----------------------------------------

        result = recovery_agent.execute(
            action=approved_action,
            amount=float(case.amount),
            customer_name=customer_name,
            customer_email=customer_email,
            scenario=case.scenario,
        )

        recovery_action = RecoveryAction(
            case_id=case.case_id,
            action=approved_action,
            status=(
                "success"
                if result.get("success")
                else "failed"
            ),
            amount=float(case.amount),
            provider_reference=result.get(
                "provider_reference"
            ),
            result=str(result),
        )

        db.add(recovery_action)

        case.action = approved_action

        # -----------------------------------------
        # 5. RETRY COUNT SAFETY
        # -----------------------------------------

        if approved_action == "retry_payment":
            case.retry_count = (
                int(case.retry_count or 0) + 1
            )

        # -----------------------------------------
        # 6. VERIFY RECOVERY
        # -----------------------------------------

        if result.get("success"):

            if approved_action in {
                "retry_payment",
                "payment_link",
            }:

                verification = (
                    verification_service.verify_recovery(
                        case=case,
                        recovery_result=result,
                    )
                )

                if verification.get("verified"):

                    case.status = "recovered"
                    case.payment_status = "paid"

                    db.add(
                        AuditLog(
                            case_id=case.case_id,
                            event_type="recovery_verified",
                            action=approved_action,
                            actor="verification_service",
                            status="success",
                            description=verification.get(
                                "message",
                                "Recovery successfully verified.",
                            ),
                        )
                    )

                else:

                    case.status = "pending_verification"

                    db.add(
                        AuditLog(
                            case_id=case.case_id,
                            event_type="recovery_pending",
                            action=approved_action,
                            actor="verification_service",
                            status="pending",
                            description=verification.get(
                                "message",
                                "Recovery requires verification.",
                            ),
                        )
                    )

            elif approved_action == "reminder":

                case.status = "recovery_sent"

            elif approved_action == "no_action":

                case.status = "no_action"

        else:

            case.status = "failed"

        # -----------------------------------------
        # 7. AUDIT TRAIL
        # -----------------------------------------

        db.add(
            AuditLog(
                case_id=case.case_id,
                event_type="recovery_execution",
                action=approved_action,
                actor="recovery_agent",
                status=(
                    "success"
                    if result.get("success")
                    else "failed"
                ),
                description=result.get(
                    "message",
                    "Recovery action executed.",
                ),
            )
        )

        db.commit()
        db.refresh(case)

        # -----------------------------------------
        # 8. RESPONSE
        # -----------------------------------------

        return {
            "success": result.get(
                "success",
                False,
            ),
            "case_id": case.case_id,
            "status": case.status,
            "action": approved_action,
            "policy": policy_result,
            "result": result,
        }

    finally:
        db.close()


# =================================================
# VERIFY EXISTING RAZORPAY PAYMENT LINK
# =================================================

@router.post("/{case_id}/verify-payment")
def verify_payment(
    case_id: str,
    request: PaymentVerificationRequest,
):
    db: Session = SessionLocal()

    try:
        # -----------------------------------------
        # 1. FIND CASE
        # -----------------------------------------

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

        # -----------------------------------------
        # 2. VERIFY PAYMENT DIRECTLY WITH RAZORPAY
        # -----------------------------------------

        verification_result = (
            verification_service.verify_recovery(
                case=case,
                recovery_result={
                    "success": True,
                    "action": "payment_link",
                    "provider_reference": request.payment_link_id,
                },
            )
        )

        # -----------------------------------------
        # 3. PAYMENT VERIFIED
        # -----------------------------------------

        if verification_result.get("verified"):

            case.status = "recovered"
            case.payment_status = "paid"

            db.add(
                AuditLog(
                    case_id=case.case_id,
                    event_type="recovery_verified",
                    action="payment_link",
                    actor="verification_service",
                    status="success",
                    description=verification_result.get(
                        "message",
                        "Payment successfully verified.",
                    ),
                )
            )

            db.commit()
            db.refresh(case)

            return {
                "success": True,
                "case_id": case.case_id,
                "status": case.status,
                "payment_status": case.payment_status,
                "amount_recovered": float(case.amount),
                "verification": verification_result,
            }

        # -----------------------------------------
        # 4. PAYMENT NOT YET VERIFIED
        # -----------------------------------------

        return {
            "success": False,
            "case_id": case.case_id,
            "status": case.status,
            "verification": verification_result,
        }

    finally:
        db.close()





