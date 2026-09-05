from typing import Any

from sqlalchemy.orm import Session

from ..models import Customer, RecoveryAction, RevenueCase


class RAGService:
    """
    Retrieval-Augmented Generation service for REVIVE.

    Retrieves relevant customer, case, and recovery-history
    information from PostgreSQL and provides it as structured
    context to the AI agents.
    """

    def build_customer_context(
        self,
        customer: Customer | None,
    ) -> dict[str, Any]:

        if customer is None:
            return {
                "customer_id": None,
                "name": "Unknown customer",
                "email": None,
                "payment_history": None,
            }

        return {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "email": customer.email,
            "payment_history": customer.payment_history,
        }

    def retrieve_context(
        self,
        db: Session,
        case: RevenueCase | None = None,
        customer_id: str | None = None,
    ) -> dict[str, Any]:

        if case is not None:
            customer_id = case.customer_id

        customer = None

        if customer_id:
            customer = (
                db.query(Customer)
                .filter(
                    Customer.customer_id == customer_id
                )
                .first()
            )

        customer_context = (
            self.build_customer_context(customer)
        )

        recovery_history = []

        if customer_id:
            case_ids = [
                row.case_id
                for row in (
                    db.query(RevenueCase)
                    .filter(
                        RevenueCase.customer_id
                        == customer_id
                    )
                    .all()
                )
            ]

            if case_ids:
                actions = (
                    db.query(RecoveryAction)
                    .filter(
                        RecoveryAction.case_id.in_(
                            case_ids
                        )
                    )
                    .order_by(
                        RecoveryAction.executed_at.desc()
                    )
                    .limit(10)
                    .all()
                )

                recovery_history = [
                    {
                        "case_id": action.case_id,
                        "action": action.action,
                        "status": action.status,
                        "amount": action.amount,
                        "provider_reference": (
                            action.provider_reference
                        ),
                        "result": action.result,
                        "executed_at": (
                            action.executed_at.isoformat()
                            if action.executed_at
                            else None
                        ),
                    }
                    for action in actions
                ]

        case_context = None

        if case is not None:
            case_context = {
                "case_id": case.case_id,
                "scenario": case.scenario,
                "event_type": case.event_type,
                "amount": case.amount,
                "risk_score": case.risk_score,
                "failure_reason": (
                    case.failure_reason
                ),
                "retry_count": case.retry_count,
                "status": case.status,
            }

        return {
            "customer": customer_context,
            "case": case_context,
            "recovery_history": recovery_history,
        }


rag_service = RAGService()