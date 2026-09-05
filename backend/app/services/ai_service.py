import json
import os
from typing import Any

from openai import OpenAI


class AIService:
    """
    AI service for REVIVE.

    Uses structured JSON responses from the LLM when an API key is
    available. If the API key is unavailable, REVIVE falls back to a
    deterministic response so the application can still run locally.
    """

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

    def _fallback_diagnosis(
        self,
        event: dict[str, Any],
    ) -> dict[str, Any]:

        scenario = str(
            event.get("scenario", "")
        ).lower()

        failure_reason = str(
            event.get("failure_reason", "")
        ).lower()

        if "failed" in scenario or failure_reason:
            if any(
                word in failure_reason
                for word in [
                    "timeout",
                    "network",
                    "temporary",
                    "transient",
                ]
            ):
                diagnosis = "Transient payment failure"
                confidence = 0.92
            else:
                diagnosis = "Payment failure requires recovery assessment"
                confidence = 0.78

        elif "abandon" in scenario:
            diagnosis = "Checkout abandonment"
            confidence = 0.90

        elif "subscription" in scenario:
            diagnosis = "Subscription payment failure"
            confidence = 0.88

        elif "overdue" in scenario:
            diagnosis = "Overdue receivable"
            confidence = 0.91

        else:
            diagnosis = "Revenue risk detected"
            confidence = 0.75

        return {
            "diagnosis": diagnosis,
            "confidence": confidence,
            "reasoning": (
                "Fallback deterministic diagnosis generated "
                "from the available revenue-risk signals."
            ),
        }

    def diagnose(
        self,
        event: dict[str, Any],
    ) -> dict[str, Any]:

        if not self.client:
            return self._fallback_diagnosis(
                event
            )

        system_prompt = """
You are the Diagnosis Engine of REVIVE,
an autonomous AI revenue recovery agent.

Analyze the revenue-risk event and return ONLY valid JSON.

Required JSON structure:
{
  "diagnosis": "short diagnosis",
  "confidence": 0.0,
  "reasoning": "brief explanation"
}

Do not execute any action.
Do not invent facts.
Confidence must be between 0 and 1.
"""

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
                            event,
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

            return {
                "diagnosis": result.get(
                    "diagnosis",
                    "Revenue risk detected",
                ),
                "confidence": float(
                    result.get(
                        "confidence",
                        0.5,
                    )
                ),
                "reasoning": result.get(
                    "reasoning",
                    "",
                ),
            }

        except Exception as exc:
            fallback = self._fallback_diagnosis(
                event
            )

            fallback["llm_error"] = str(exc)

            return fallback


ai_service = AIService()