from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import RevenueCase


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def get_dashboard(
    db: Session = Depends(get_db),
):
    cases = (
        db.query(RevenueCase)
        .order_by(RevenueCase.created_at.desc())
        .all()
    )

    total_cases = len(cases)

    recovered_cases = [
        case
        for case in cases
        if str(case.status).lower() == "recovered"
    ]

    revenue_recovered = sum(
        float(case.amount or 0)
        for case in recovered_cases
    )

    revenue_at_risk = sum(
        float(case.amount or 0)
        for case in cases
        if str(case.status).lower()
        not in {"recovered", "closed"}
    )

    recovery_rate = (
        (len(recovered_cases) / total_cases) * 100
        if total_cases > 0
        else 0
    )

    recent_cases = []

    for case in cases[:10]:
        recent_cases.append(
            {
                "id": case.case_id,
                "case_id": case.case_id,
                "scenario": case.scenario,
                "event_type": case.event_type,
                "customer_id": case.customer_id,
                "amount": float(case.amount or 0),
                "risk_score": float(case.risk_score or 0),
                "decision": case.decision,
                "action": case.action,
                "status": case.status,
                "payment_status": case.payment_status,
                "created_at": (
                    case.created_at.isoformat()
                    if case.created_at
                    else None
                ),
            }
        )

    return {
        "stats": {
            "revenue_recovered": revenue_recovered,
            "recovery_rate": round(recovery_rate, 2),
            "revenue_at_risk": revenue_at_risk,
            "cases_processed": total_cases,
        },
        "recent_cases": recent_cases,
    }


@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
):
    cases = (
        db.query(RevenueCase)
        .order_by(RevenueCase.created_at.asc())
        .all()
    )

    total_cases = len(cases)

    recovered_cases = [
        case
        for case in cases
        if str(case.status).lower() == "recovered"
    ]

    revenue_recovered = sum(
        float(case.amount or 0)
        for case in recovered_cases
    )

    revenue_at_risk = sum(
        float(case.amount or 0)
        for case in cases
        if str(case.status).lower()
        not in {"recovered", "closed"}
    )

    scenario_map = {}

    for case in cases:
        scenario = case.scenario or "Unknown"

        if scenario not in scenario_map:
            scenario_map[scenario] = {
                "scenario": scenario,
                "cases": 0,
                "recovered": 0,
                "revenue_recovered": 0,
            }

        scenario_map[scenario]["cases"] += 1

        if str(case.status).lower() == "recovered":
            scenario_map[scenario]["recovered"] += 1
            scenario_map[scenario]["revenue_recovered"] += float(
                case.amount or 0
            )

    scenario_breakdown = list(scenario_map.values())

    for item in scenario_breakdown:
        item["recovery_rate"] = (
            item["recovered"] / item["cases"] * 100
            if item["cases"] > 0
            else 0
        )

    trend_map = defaultdict(float)

    for case in recovered_cases:
        if case.created_at:
            date_key = case.created_at.strftime("%Y-%m-%d")
            trend_map[date_key] += float(case.amount or 0)

    trend = [
        {
            "date": date_key,
            "recovered": amount,
        }
        for date_key, amount in sorted(trend_map.items())
    ]

    return {
        "summary": {
            "total_cases": total_cases,
            "recovered_cases": len(recovered_cases),
            "revenue_recovered": revenue_recovered,
            "revenue_at_risk": revenue_at_risk,
        },
        "scenario_breakdown": scenario_breakdown,
        "trend": trend,
    }
