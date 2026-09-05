from typing import Any

from ..services.ai_service import ai_service
from ..services.rag_service import rag_service


class DiagnosisAgent:
    """
    REVIVE AI Diagnosis Agent.

    Retrieves relevant customer, case, and recovery-history context
    through the RAG layer before asking the LLM to diagnose the
    revenue-loss event.
    """

    def diagnose(
        self,
        db: Any,
        event: dict[str, Any],
        case: Any | None = None,
    ) -> dict[str, Any]:

        # Retrieve relevant business context
        retrieved_context = rag_service.retrieve_context(
            db=db,
            case=case,
            customer_id=event.get(
                "customer_id"
            ),
        )

        # Combine the original event with retrieved RAG context
        enriched_event = {
            "event": event,
            "retrieved_context": retrieved_context,
        }

        # Send the enriched context to the LLM
        diagnosis = ai_service.diagnose(
            enriched_event
        )

        # Keep the retrieved context available for
        # auditability and downstream decision making.
        diagnosis["retrieved_context"] = (
            retrieved_context
        )

        return diagnosis


diagnosis_agent = DiagnosisAgent()