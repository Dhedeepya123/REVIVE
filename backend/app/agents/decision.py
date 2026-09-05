import json
import os
from typing import Any

from openai import OpenAI


class DecisionAgent:
    """
    REVIVE AI Decision Agent.

    Uses ML risk, AI diagnosis, customer/case context and RAG
    context to recommend one bounded recovery action.

    The agent only recommends an action.
    The Policy Engine decides whether that action is permitted.
    """

    ALLOWED_ACTIONS = {
        "retry_payment",
        "payment_link",
        "reminder",
        "human_escalation",
        "no_action",
    }

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")

        self.client = (
            OpenAI(api_key=self.api_key)
            if self.api_key
            else None
        )

        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-4.1-mini",
        )

    def _fallback_decision(
        self,
        risk_score: float,
        diagnosis: dict[str, Any],
        event: dict[str, Any],
    ) -> dict[str, Any]:

        scenario = str(
            event.get("scenario", "")
        ).lower()

        retry_count = int(
            event.get("retry_count", 0) or 0
        )

        if retry_count >= 2:
            action = "human_escalation"

        elif (
            "failed_payment" in scenario
            or "failed payment" in scenario
            or event.get("event_type") == "payment.failed"
            or event.get("event") == "payment.failed"
        ):
            action = "retry_payment"

        elif "checkout" in scenario:
            action = "payment_link"

        elif "subscription" in scenario:
            action = "payment_link"

        elif "overdue" in scenario:
            if risk_score >= 75:
                action = "human_escalation"
            else:
                action = "payment_link"

        elif risk_score >= 75:
            action = "human_escalation"

        elif risk_score >= 45:
            action = "payment_link"

        else:
            action = "retry_payment"

        return {
            "decision": action,
            "confidence": 0.80,
            "reasoning": (
                "Decision generated using ML risk score, "
                "AI diagnosis, scenario context and "
                "bounded retry safety rules."
            ),
        }

    def decide(
        self,
        risk_score: float,
        diagnosis: dict[str, Any],
        event: dict[str, Any],
        retrieved_context: dict[str, Any] | None = None,
        case: Any | None = None,
    ) -> dict[str, Any]:

        context = retrieved_context or {}

        # Include case information when supplied by the orchestrator.
        case_context = {}

        if case is not None:
            case_context = {
                "case_id": getattr(case, "case_id", None),
                "scenario": getattr(case, "scenario", None),
                "amount": getattr(case, "amount", None),
                "risk_score": getattr(case, "risk_score", None),
                "retry_count": getattr(case, "retry_count", 0),
                "status": getattr(case, "status", None),
                "payment_status": getattr(
                    case,
                    "payment_status",
                    None,
                ),
                "failure_reason": getattr(
                    case,
                    "failure_reason",
                    None,
                ),
            }

        # Ensure retry_count is available to the AI safety guard.
        if "retry_count" not in event:
            event = {
                **event,
                "retry_count": case_context.get(
                    "retry_count",
                    0,
                ),
            }

        # Safe deterministic fallback when no OpenAI key is configured.
        if not self.client:
            result = self._fallback_decision(
                risk_score=risk_score,
                diagnosis=diagnosis,
                event=event,
            )

            result["retrieved_context"] = context
            result["case_context"] = case_context

            return result

        system_prompt = """
You are the Decision Engine of REVIVE,
an autonomous AI revenue recovery agent.

Your job is to recommend ONE bounded recovery action.

Possible actions:
- retry_payment
- payment_link
- reminder
- human_escalation
- no_action

Safety rules:
- Never recommend unlimited retries.
- If retry_count is 2 or greater, recommend human_escalation.
- Do not execute the action.
- Do not invent customer information.
- Use the supplied RAG context.
- Consider the ML risk score and AI diagnosis.
- Return ONLY valid JSON.

Required JSON:
{
  "decision": "one allowed action",
  "confidence": 0.0,
  "reasoning": "brief explanation"
}

Confidence must be between 0 and 1.
"""

        prompt_data = {
            "risk_score": risk_score,
            "diagnosis": diagnosis,
            "event": event,
            "case": case_context,
            "retrieved_context": context,
        }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={
                    "type": "json_object"
                },
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            prompt_data,
                            default=str,
                        ),
                    },
                ],
            )

            content = (
                response.choices[0]
                .message
                .content
            )

            result = json.loads(
                content or "{}"
            )

            decision = result.get(
                "decision",
                "human_escalation",
            )

            if decision not in self.ALLOWED_ACTIONS:
                decision = "human_escalation"

            # Final hard safety guard.
            retry_count = int(
                event.get("retry_count", 0) or 0
            )

            if retry_count >= 2:
                decision = "human_escalation"

            confidence = float(
                result.get(
                    "confidence",
                    0.5,
                )
            )

            confidence = max(
                0.0,
                min(
                    1.0,
                    confidence,
                ),
            )

            return {
                "decision": decision,
                "confidence": confidence,
                "reasoning": result.get(
                    "reasoning",
                    "",
                ),
                "retrieved_context": context,
                "case_context": case_context,
            }

        except Exception as exc:
            fallback = self._fallback_decision(
                risk_score=risk_score,
                diagnosis=diagnosis,
                event=event,
            )

            fallback["llm_error"] = str(exc)
            fallback["retrieved_context"] = context
            fallback["case_context"] = case_context

            return fallback


decision_agent = DecisionAgent()