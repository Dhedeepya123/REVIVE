from typing import Any

from ..services.razorpay import razorpay_service


class RecoveryAgent:
    """
    REVIVE Recovery Agent.

    Executes an action only after the Policy Engine has approved it.
    """

    def execute(
        self,
        action: str,
        amount: float,
        customer_name: str = "REVIVE Customer",
        customer_email: str | None = None,
        scenario: str | None = None,
    ) -> dict[str, Any]:

        if action == "payment_link":
            return razorpay_service.create_payment_link(
                amount=amount,
                customer_name=customer_name,
                customer_email=customer_email,
            )

        if action == "retry_payment":
            # -----------------------------------------
            # REPEATED FAILURE SAFETY SCENARIO
            # -----------------------------------------
            # This scenario intentionally simulates
            # another failed retry so REVIVE can prove
            # that it stops after the retry limit.
            if scenario == "repeated_failure":
                return {
                    "success": False,
                    "mode": "simulation",
                    "action": "retry_payment",
                    "message": (
                        "Payment retry failed in REVIVE "
                        "simulation mode."
                    ),
                }

            # Normal failed-payment scenario
            return {
                "success": True,
                "mode": "simulation",
                "action": "retry_payment",
                "message": (
                    "Payment retry executed in REVIVE "
                    "simulation mode."
                ),
            }

        if action == "reminder":
            return {
                "success": True,
                "mode": "simulation",
                "action": "reminder",
                "message": (
                    "Recovery reminder generated successfully."
                ),
            }

        if action == "human_escalation":
            return {
                "success": True,
                "mode": "human_review",
                "action": "human_escalation",
                "message": (
                    "Case escalated to human review."
                ),
            }

        if action == "no_action":
            return {
                "success": True,
                "mode": "no_action",
                "action": "no_action",
                "message": (
                    "No recovery action was required."
                ),
            }

        return {
            "success": False,
            "action": action,
            "message": (
                "Unsupported recovery action."
            ),
        }


recovery_agent = RecoveryAgent()
