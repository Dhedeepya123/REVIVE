import hashlib
import hmac
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import WebhookEvent
from .services.orchestrator import revenue_orchestrator
from .config import settings

# API routers
from .api.dashboard import router as dashboard_router
from .api.cases import router as cases_router
from .api.recovery import router as recovery_router
from .api.audit import router as audit_router
from .api.review import router as review_router


# Import all SQLAlchemy models so metadata is registered.
from . import models  # noqa: F401


# Create database tables.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="REVIVE",
    description="Autonomous AI Revenue Recovery Agent",
    version="1.0.0",
)


# Allow the React/Vite frontend to communicate with the FastAPI backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RazorpayWebhook(BaseModel):
    event: str
    payload: dict


def verify_webhook_signature(
    body: bytes,
    signature: str,
    secret: str,
) -> bool:
    """
    Verify Razorpay webhook signature using HMAC SHA256.

    During local development, if no webhook secret is configured,
    verification is skipped.
    """
    if not secret:
        return True

    expected_signature = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature or "",
    )


@app.get("/")
def root():
    return {
        "name": "REVIVE",
        "status": "online",
        "message": "Revenue Recovery Agent backend is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "REVIVE",
    }


@app.post("/webhooks/razorpay")
async def razorpay_webhook(
    webhook: RazorpayWebhook,
    request: Request,
):
    body = await request.body()

    event_id = request.headers.get("x-razorpay-event-id")
    signature = request.headers.get("x-razorpay-signature", "")

    if not verify_webhook_signature(
        body,
        signature,
        settings.RAZORPAY_WEBHOOK_SECRET,
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay webhook signature",
        )

    db: Session = SessionLocal()

    try:
        # If Razorpay supplies an event ID, use it.
        # Otherwise generate a deterministic local ID from the body.
        if not event_id:
            event_id = (
                "local-"
                + hashlib.sha256(body).hexdigest()
            )

        # Idempotency check.
        existing_event = (
            db.query(WebhookEvent)
            .filter(
                WebhookEvent.event_id == event_id
            )
            .first()
        )

        if existing_event:
            return {
                "status": "duplicate",
                "message": "Event already processed",
                "event_id": event_id,
            }

        # Store the raw webhook event.
        event_record = WebhookEvent(
            event_id=event_id,
            event_type=webhook.event,
            payload=json.dumps(webhook.payload),
        )

        db.add(event_record)
        db.commit()
        db.refresh(event_record)

        # Normalize the incoming event for the REVIVE pipeline.
        event = {
            "event_id": event_id,
            "event_type": webhook.event,
            "event": webhook.event,
            **webhook.payload,
        }

        # Send event through:
        # Risk Engine → Diagnosis → Decision → Policy
        pipeline_result = revenue_orchestrator.process_event(
            db,
            event,
        )

        return {
            "status": "received",
            "event_id": event_id,
            "event_type": webhook.event,
            "pipeline": pipeline_result,
        }

    finally:
        db.close()


# Register REVIVE API routers.
app.include_router(dashboard_router)
app.include_router(cases_router)
app.include_router(recovery_router)
app.include_router(audit_router)
app.include_router(review_router)