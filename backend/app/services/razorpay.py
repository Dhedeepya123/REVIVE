from typing import Any, Optional

import razorpay

from ..config import settings


class RazorpayService:
    """
    Wrapper around the Razorpay API.

    The service is intentionally isolated from the rest of REVIVE so that
    payment execution can be controlled by the Policy Engine.
    """

    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET

        self.client: Optional[razorpay.Client] = None

        if self.key_id and self.key_secret:
            self.client = razorpay.Client(
                auth=(
                    self.key_id,
                    self.key_secret,
                )
            )

    @property
    def configured(self) -> bool:
        return self.client is not None

    def create_payment_link(
        self,
        amount: float,
        customer_name: str,
        customer_email: Optional[str] = None,
        description: str = "REVIVE revenue recovery payment",
    ) -> dict[str, Any]:

        if not self.client:
            return {
                "success": False,
                "mode": "simulation",
                "message": (
                    "Razorpay credentials are not configured. "
                    "Payment link was simulated."
                ),
                "payment_link": None,
            }

        amount_paise = int(round(amount * 100))

        customer = {
            "name": customer_name,
        }

        if customer_email:
            customer["email"] = customer_email

        try:
            payment_link = self.client.payment_link.create(
                {
                    "amount": amount_paise,
                    "currency": "INR",
                    "accept_partial": False,
                    "description": description,
                    "customer": customer,
                    "notify": {
                        "sms": False,
                        "email": bool(customer_email),
                    },
                    "reminder_enable": True,
                }
            )

            return {
                "success": True,
                "mode": "razorpay",
                "payment_link": payment_link.get("short_url"),
                "provider_reference": payment_link.get("id"),
                "raw_response": payment_link,
            }

        except Exception as exc:
            return {
                "success": False,
                "mode": "razorpay",
                "message": str(exc),
                "payment_link": None,
            }

    def fetch_payment_link(
        self,
        payment_link_id: str,
    ) -> dict[str, Any]:

        if not self.client:
            return {
                "success": False,
                "mode": "simulation",
                "message": (
                    "Razorpay credentials are not configured."
                ),
            }

        try:
            payment_link = self.client.payment_link.fetch(
                payment_link_id
            )

            return {
                "success": True,
                "payment_link": payment_link,
            }

        except Exception as exc:
            return {
                "success": False,
                "message": str(exc),
            }

    def fetch_payment(
        self,
        payment_id: str,
    ) -> dict[str, Any]:

        if not self.client:
            return {
                "success": False,
                "mode": "simulation",
                "message": (
                    "Razorpay credentials are not configured."
                ),
            }

        try:
            payment = self.client.payment.fetch(
                payment_id
            )

            return {
                "success": True,
                "payment": payment,
            }

        except Exception as exc:
            return {
                "success": False,
                "message": str(exc),
            }

    def fetch_order(
        self,
        order_id: str,
    ) -> dict[str, Any]:

        if not self.client:
            return {
                "success": False,
                "mode": "simulation",
                "message": (
                    "Razorpay credentials are not configured."
                ),
            }

        try:
            order = self.client.order.fetch(
                order_id
            )

            return {
                "success": True,
                "order": order,
            }

        except Exception as exc:
            return {
                "success": False,
                "message": str(exc),
            }


razorpay_service = RazorpayService()