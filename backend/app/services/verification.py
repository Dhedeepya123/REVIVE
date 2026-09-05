from typing import Any

from .razorpay import razorpay_service


class VerificationService:
    """
    Verifies whether a recovery action resulted in a successful payment.

    REVIVE must never treat payment-link creation as payment recovery.
    A payment link is considered recovered only after Razorpay reports
    that the payment link has been paid.
    """

    def verify_recovery(
        self,
        case: Any,
        recovery_result: dict[str, Any],
    ) -> dict[str, Any]:

        if not recovery_result.get("success"):
            return {
                "verified": False,
                "message": "Recovery execution was not successful.",
            }

        action = recovery_result.get("action")

        # Retry is currently executed through REVIVE's controlled
        # simulation layer.
        if action == "retry_payment":
            return {
                "verified": True,
                "method": "simulation",
                "message": (
                    "Payment retry succeeded and recovery was verified."
                ),
            }

        # A payment link is NOT recovered merely because it was created.
        # We now ask Razorpay for the actual Payment Link status.
        if action == "payment_link":
            provider_reference = recovery_result.get(
                "provider_reference"
            )

            if not provider_reference:
                return {
                    "verified": False,
                    "method": "payment_link",
                    "message": (
                        "Payment link was created but no Razorpay "
                        "provider reference was returned."
                    ),
                }

            payment_link_result = razorpay_service.fetch_payment_link(
                provider_reference
            )

            if not payment_link_result.get("success"):
                return {
                    "verified": False,
                    "method": "razorpay_payment_link",
                    "provider_reference": provider_reference,
                    "message": (
                        "Unable to verify the Razorpay Payment Link: "
                        + payment_link_result.get(
                            "message",
                            "Unknown Razorpay error.",
                        )
                    ),
                }

            payment_link = payment_link_result.get(
                "payment_link",
                {}
            )

            status = payment_link.get("status")
            amount_paid_paise = payment_link.get(
                "amount_paid",
                0,
            )

            expected_amount_paise = int(
                round(float(case.amount) * 100)
            )

            # Payment is verified only when Razorpay reports the link
            # as paid and the received amount matches the case amount.
            if (
                status == "paid"
                and amount_paid_paise >= expected_amount_paise
            ):
                return {
                    "verified": True,
                    "method": "razorpay_payment_link",
                    "provider_reference": provider_reference,
                    "razorpay_status": status,
                    "amount_paid": amount_paid_paise / 100,
                    "message": (
                        "Razorpay confirms that the Payment Link "
                        "has been paid successfully."
                    ),
                }

            return {
                "verified": False,
                "method": "razorpay_payment_link",
                "provider_reference": provider_reference,
                "razorpay_status": status,
                "amount_paid": amount_paid_paise / 100,
                "message": (
                    "Payment Link exists, but Razorpay has not "
                    "yet confirmed the required payment."
                ),
            }

        if action == "reminder":
            return {
                "verified": False,
                "method": "reminder",
                "message": (
                    "Reminder was sent. Payment has not yet "
                    "been verified."
                ),
            }

        return {
            "verified": False,
            "method": "none",
            "message": (
                "No payment verification is applicable "
                "for this action."
            ),
        }


verification_service = VerificationService()