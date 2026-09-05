from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier


class RevenueRiskEngine:
    """
    Deterministic revenue-risk scoring engine.

    Uses a scikit-learn Random Forest trained on synthetic revenue-risk
    examples and combines the model output with deterministic business
    rules.
    """

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=5,
        )

        self._train_model()

    def _train_model(self):
        """
        Train the model using synthetic revenue-risk examples.

        Features:
        0 = amount
        1 = failure count
        2 = days overdue
        3 = previous successful payments
        4 = customer lifetime value
        5 = hours since checkout abandonment
        """

        training_data = np.array(
            [
                [500, 0, 0, 20, 50000, 1],
                [1000, 0, 0, 15, 30000, 2],
                [2500, 1, 0, 10, 25000, 1],
                [5000, 1, 1, 8, 20000, 3],
                [10000, 2, 3, 5, 15000, 5],
                [25000, 2, 5, 4, 50000, 8],
                [48000, 0, 5, 15, 100000, 0],
                [75000, 3, 10, 2, 90000, 0],
                [150000, 4, 20, 1, 150000, 0],
                [2000, 0, 0, 25, 40000, 1],
                [3000, 1, 0, 18, 35000, 2],
                [8000, 3, 2, 3, 10000, 4],
                [12000, 4, 7, 2, 18000, 6],
                [50000, 5, 15, 1, 60000, 0],
            ],
            dtype=float,
        )

        labels = np.array(
            [
                0,
                0,
                0,
                0,
                1,
                1,
                0,
                1,
                1,
                0,
                0,
                1,
                1,
                1,
            ]
        )

        self.model.fit(
            training_data,
            labels,
        )

    def calculate_score(
        self,
        amount: float = 0,
        failure_count: int = 0,
        days_overdue: int = 0,
        previous_successful_payments: int = 0,
        customer_lifetime_value: float = 0,
        hours_since_abandonment: float = 0,
    ) -> float:

        features = np.array(
            [
                [
                    amount,
                    failure_count,
                    days_overdue,
                    previous_successful_payments,
                    customer_lifetime_value,
                    hours_since_abandonment,
                ]
            ],
            dtype=float,
        )

        probabilities = self.model.predict_proba(features)[0]

        risk_probability = float(probabilities[1])

        score = risk_probability * 100

        # Deterministic business-risk adjustments.
        if failure_count >= 2:
            score += 15

        if days_overdue >= 7:
            score += 10

        if amount >= 50000:
            score += 5

        if (
            hours_since_abandonment > 24
            and hours_since_abandonment > 0
        ):
            score += 5

        # Strong customer history reduces risk slightly.
        if previous_successful_payments >= 10:
            score -= 5

        score = max(
            0,
            min(
                100,
                score,
            ),
        )

        return round(score, 2)

    def classify_risk(
        self,
        score: float,
    ) -> str:

        if score >= 75:
            return "HIGH"

        if score >= 45:
            return "MEDIUM"

        return "LOW"

    def assess(
        self,
        event: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Assess revenue risk from either an event dictionary or
        explicit keyword arguments.
        """

        event = event or {}

        # Support both direct fields and nested Razorpay-style payloads.
        amount = event.get("amount", kwargs.get("amount", 0))

        failure_count = event.get(
            "failure_count",
            kwargs.get("failure_count", 0),
        )

        days_overdue = event.get(
            "days_overdue",
            kwargs.get("days_overdue", 0),
        )

        previous_successful_payments = event.get(
            "previous_successful_payments",
            kwargs.get("previous_successful_payments", 0),
        )

        customer_lifetime_value = event.get(
            "customer_lifetime_value",
            kwargs.get("customer_lifetime_value", 0),
        )

        hours_since_abandonment = event.get(
            "hours_since_abandonment",
            kwargs.get("hours_since_abandonment", 0),
        )

        # Convert Razorpay paise to rupees when needed.
        if amount and amount > 100000:
            amount = amount / 100

        # Failed-payment events represent at least one failure.
        event_type = str(
            event.get(
                "event_type",
                event.get("event", ""),
            )
        ).lower()

        if (
            "failed" in event_type
            and failure_count == 0
        ):
            failure_count = 1

        score = self.calculate_score(
            amount=float(amount or 0),
            failure_count=int(failure_count or 0),
            days_overdue=int(days_overdue or 0),
            previous_successful_payments=int(
                previous_successful_payments or 0
            ),
            customer_lifetime_value=float(
                customer_lifetime_value or 0
            ),
            hours_since_abandonment=float(
                hours_since_abandonment or 0
            ),
        )

        return {
            "risk_score": score,
            "risk_level": self.classify_risk(score),
        }


risk_engine = RevenueRiskEngine()