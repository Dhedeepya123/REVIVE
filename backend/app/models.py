from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from .database import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    event_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    event_type = Column(
        String(255),
        nullable=False,
    )

    payload = Column(
        Text,
        nullable=False,
    )

    received_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class Customer(Base):
    __tablename__ = "customers"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    customer_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    email = Column(
        String(255),
        nullable=True,
    )

    payment_history = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class RevenueCase(Base):
    __tablename__ = "revenue_cases"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    customer_id = Column(
        String(255),
        nullable=True,
        index=True,
    )

    scenario = Column(
        String(100),
        nullable=False,
    )

    event_type = Column(
        String(255),
        nullable=True,
    )

    amount = Column(
        Float,
        nullable=False,
        default=0,
    )

    risk_score = Column(
        Float,
        nullable=False,
        default=0,
    )

    diagnosis = Column(
        Text,
        nullable=True,
    )

    decision = Column(
        String(255),
        nullable=True,
    )

    policy_result = Column(
        String(255),
        nullable=True,
    )

    action = Column(
        String(255),
        nullable=True,
    )

    status = Column(
        String(100),
        nullable=False,
        default="PENDING",
    )

    payment_status = Column(
        String(100),
        nullable=True,
    )

    failure_reason = Column(
        Text,
        nullable=True,
    )

    retry_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_id = Column(
        String(255),
        nullable=False,
        index=True,
    )

    action = Column(
        String(255),
        nullable=False,
    )

    status = Column(
        String(100),
        nullable=False,
        default="PENDING",
    )

    amount = Column(
        Float,
        nullable=False,
        default=0,
    )

    provider_reference = Column(
        String(255),
        nullable=True,
    )

    result = Column(
        Text,
        nullable=True,
    )

    executed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_id = Column(
        String(255),
        nullable=True,
        index=True,
    )

    event_type = Column(
        String(255),
        nullable=False,
    )

    action = Column(
        String(255),
        nullable=True,
    )

    actor = Column(
        String(100),
        nullable=False,
        default="REVIVE",
    )

    status = Column(
        String(100),
        nullable=False,
        default="RECORDED",
    )

    description = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    reason = Column(
        Text,
        nullable=False,
    )

    recommendation = Column(
        String(255),
        nullable=True,
    )

    status = Column(
        String(100),
        nullable=False,
        default="PENDING",
    )

    reviewer = Column(
        String(255),
        nullable=True,
    )

    review_reason = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    reviewed_at = Column(
        DateTime,
        nullable=True,
    )