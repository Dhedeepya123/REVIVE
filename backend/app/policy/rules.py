from typing import Any


MAX_AUTOMATIC_RETRIES = 2
MAX_AUTOMATIC_RECOVERY_AMOUNT = 100000.0
MIN_RISK_FOR_AUTOMATIC_RECOVERY = 25.0

ALLOWED_ACTIONS = {
    "retry_payment",
    "payment_link",
    "reminder",
    "human_escalation",
    "no_action",
}


class PolicyEngine:
    """
    Deterministic safety layer for REVIVE.

    The AI may recommend an action, but the Policy Engine
    is the final authority on whether that action is allowed.
    """

    def evaluate(
        self,
        proposed_action: str = "no_action",
        amount: float = 0.0,
        risk_score: float = 0.0,
        retry_count: int = 0,
        **kwargs: Any,
    ) -> dict[str, Any]:

        action = kwargs.get("action", proposed_action)

        if not action:
            action = "no_action"

        amount = float(amount or 0)
        risk_score = float(risk_score or 0)
        retry_count = int(retry_count or 0)

        # ---------------------------------------------------------
        # 1. Invalid action
        # ---------------------------------------------------------
        if action not in ALLOWED_ACTIONS:
            return {
                "approved": False,
                "decision": "blocked",
                "action": "no_action",
                "reason": f"Unsupported action: {action}",
            }

        # ---------------------------------------------------------
        # 2. No action
        # ---------------------------------------------------------
        if action == "no_action":
            return {
                "approved": True,
                "decision": "approved",
                "action": "no_action",
                "reason": "No automated recovery action required.",
            }

        # ---------------------------------------------------------
        # 3. Human escalation
        # ---------------------------------------------------------
        if action == "human_escalation":
            return {
                "approved": True,
                "decision": "human_review",
                "action": "human_escalation",
                "reason": "Case requires human review.",
            }

        # ---------------------------------------------------------
        # 4. Maximum automatic recovery amount
        # ---------------------------------------------------------
        if amount > MAX_AUTOMATIC_RECOVERY_AMOUNT:
            return {
                "approved": False,
                "decision": "blocked",
                "action": "human_escalation",
                "reason": (
                    f"Amount ₹{amount:.2f} exceeds the automatic "
                    f"recovery limit of ₹{MAX_AUTOMATIC_RECOVERY_AMOUNT:.2f}."
                ),
            }

        # ---------------------------------------------------------
        # 5. Retry protection
        # ---------------------------------------------------------
        if action == "retry_payment":
            if retry_count >= MAX_AUTOMATIC_RETRIES:
                return {
                    "approved": False,
                    "decision": "blocked",
                    "action": "human_escalation",
                    "reason": (
                        "Maximum automatic retry limit reached. "
                        "Escalating to human review."
                    ),
                }

        # ---------------------------------------------------------
        # 6. Minimum risk protection
        # ---------------------------------------------------------
        if (
            action in {"retry_payment", "payment_link"}
            and risk_score < MIN_RISK_FOR_AUTOMATIC_RECOVERY
        ):
            return {
                "approved": False,
                "decision": "blocked",
                "action": "no_action",
                "reason": (
                    "Risk score is below the minimum threshold "
                    "for automatic recovery."
                ),
            }

        # ---------------------------------------------------------
        # 7. Approve bounded recovery action
        #
        # IMPORTANT:
        # Do NOT convert payment_link into reminder.
        # Checkout abandonment specifically requires:
        #
        # checkout abandoned
        # -> payment link
        # -> recovery message
        # ---------------------------------------------------------
        return {
            "approved": True,
            "decision": "approved",
            "action": action,
            "reason": "Action passed all REVIVE policy checks.",
        }


policy_engine = PolicyEngine()