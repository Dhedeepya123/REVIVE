from typing import Any

from sqlalchemy.orm import Session

from ..agents.diagnosis import DiagnosisAgent
from ..agents.decision import DecisionAgent
from ..models import RevenueCase
from ..policy.rules import policy_engine
from .risk_engine import risk_engine


class RevenueOrchestrator:
    """
    Coordinates the complete REVIVE revenue-risk workflow:

    Event
      -> ML Risk
      -> Revenue Case
      -> RAG + AI Diagnosis
      -> AI Decision
      -> Policy Engine
      -> Bounded Action
    """

    def __init__(self):
        self.diagnosis_agent = DiagnosisAgent()
        self.decision_agent = DecisionAgent()

    def process_event(
        self,
        db: Session,
        event: dict[str, Any],
    ) -> dict[str, Any]:

        # ---------------------------------------------------------
        # 0. NORMALIZE REVENUE-RISK SCENARIO
        # ---------------------------------------------------------
        event_type = event.get(
            "event_type",
            event.get("event", "unknown"),
        )

        # Checkout abandonment is a revenue-risk event even though
        # no payment failure has occurred.
        if event_type == "checkout.abandoned":
            event["scenario"] = "checkout_abandonment"

            if not event.get("payment_status"):
                event["payment_status"] = "pending"

        # ---------------------------------------------------------
        # 1. ML RISK ENGINE
        # ---------------------------------------------------------
        risk_result = risk_engine.assess(event)

        risk_score = float(
            risk_result.get(
                "risk_score",
                0,
            )
        )

        # ---------------------------------------------------------
        # 2. CREATE REVENUE CASE
        # ---------------------------------------------------------
        case_id = event.get("case_id")

        if not case_id:
            case_id = (
                f"REVIVE-{event.get('event_id', 'LOCAL')}"
            )

        existing_case = (
            db.query(RevenueCase)
            .filter(
                RevenueCase.case_id == case_id
            )
            .first()
        )

        if existing_case:
            return {
                "success": True,
                "status": "already_processed",
                "case_id": existing_case.case_id,
            }

        amount = float(
            event.get(
                "amount",
                0,
            )
            or 0
        )

        # Razorpay normally sends amounts in paise.
        # Our test events can also contain amount in rupees.
        if amount > 100000:
            amount = amount / 100

        retry_count = int(
            event.get(
                "retry_count",
                0,
            )
            or 0
        )

        # Failed payments should be marked failed.
        # Checkout abandonment should remain pending.
        payment_status = event.get(
            "payment_status",
            "pending"
            if event.get("scenario") == "checkout_abandonment"
            else "failed",
        )

        case = RevenueCase(
            case_id=case_id,
            customer_id=event.get(
                "customer_id",
                "unknown",
            ),
            scenario=event.get(
                "scenario",
                "failed_payment",
            ),
            event_type=event.get(
                "event_type",
                event.get(
                    "event",
                    "unknown",
                ),
            ),
            amount=amount,
            risk_score=risk_score,
            status="risk_detected",
            payment_status=payment_status,
            failure_reason=event.get(
                "failure_reason"
            ),
            retry_count=retry_count,
        )

        db.add(case)
        db.commit()
        db.refresh(case)

        # ---------------------------------------------------------
        # 3. AI DIAGNOSIS + RAG
        # ---------------------------------------------------------
        diagnosis_result = (
            self.diagnosis_agent.diagnose(
                db=db,
                event=event,
                case=case,
            )
        )

        diagnosis_text = diagnosis_result.get(
            "diagnosis",
            "Revenue risk detected.",
        )

        case.diagnosis = diagnosis_text
        case.status = "diagnosed"

        db.commit()
        db.refresh(case)

        # ---------------------------------------------------------
        # 4. AI DECISION
        # ---------------------------------------------------------
        decision_result = (
            self.decision_agent.decide(
                risk_score=risk_score,
                diagnosis=diagnosis_result,
                event=event,
                retrieved_context=diagnosis_result.get(
                    "retrieved_context",
                    {},
                ),
                case=case,
            )
        )

        # DecisionAgent returns "decision".
        proposed_action = decision_result.get(
            "decision",
            "no_action",
        )

        case.decision = proposed_action

        # ---------------------------------------------------------
        # 5. POLICY ENGINE
        # ---------------------------------------------------------
        policy_result = policy_engine.evaluate(
            action=proposed_action,
            amount=float(case.amount),
            risk_score=float(case.risk_score),
            retry_count=int(
                case.retry_count or 0
            ),
        )

        case.policy_result = policy_result.get(
            "decision",
            policy_result.get(
                "status",
                "unknown",
            ),
        )

        approved_action = policy_result.get(
            "action",
            proposed_action,
        )

        case.action = approved_action

        # ---------------------------------------------------------
        # 6. DETERMINE NEXT STATE
        # ---------------------------------------------------------
        if not policy_result.get(
            "approved",
            False,
        ):
            case.status = "blocked"

        elif approved_action == "human_escalation":
            case.status = "human_review"

        elif approved_action == "no_action":
            case.status = "no_action"

        else:
            case.status = "action_ready"

        db.commit()
        db.refresh(case)

        # ---------------------------------------------------------
        # 7. RETURN COMPLETE PIPELINE RESULT
        # ---------------------------------------------------------
        return {
            "success": True,
            "case_id": case.case_id,
            "risk": risk_result,
            "diagnosis": diagnosis_result,
            "decision": decision_result,
            "policy": policy_result,
            "action": approved_action,
            "status": case.status,
        }


revenue_orchestrator = RevenueOrchestrator()