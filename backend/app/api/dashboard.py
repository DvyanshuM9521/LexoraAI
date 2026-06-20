from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime, timedelta

from app.database.db import get_db
from app.models.contract import Contract, ContractAnalysis
from app.schemas.contract import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Contract).count()
    analyzed = db.query(Contract).filter(Contract.status == "analyzed").count()
    pending = total - analyzed

    high_risk = db.query(ContractAnalysis).filter(ContractAnalysis.risk_level == "High").count()
    medium_risk = db.query(ContractAnalysis).filter(ContractAnalysis.risk_level == "Medium").count()
    low_risk = db.query(ContractAnalysis).filter(ContractAnalysis.risk_level == "Low").count()

    return DashboardStats(
        total_contracts=total,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        analyzed=analyzed,
        pending=pending,
    )


@router.get("/contracts-over-time")
def contracts_over_time(db: Session = Depends(get_db)):
    """Return contract upload counts for the last 30 days."""
    cutoff = datetime.utcnow() - timedelta(days=30)
    contracts = (
        db.query(Contract)
        .filter(Contract.upload_date >= cutoff)
        .all()
    )

    # Aggregate by date
    by_date: Dict[str, int] = {}
    for c in contracts:
        date_str = c.upload_date.strftime("%Y-%m-%d")
        by_date[date_str] = by_date.get(date_str, 0) + 1

    # Fill in missing dates
    result = []
    for i in range(30):
        day = (datetime.utcnow() - timedelta(days=29 - i)).strftime("%Y-%m-%d")
        result.append({"date": day, "count": by_date.get(day, 0)})

    return result


@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    """Return risk level distribution."""
    rows = (
        db.query(ContractAnalysis.risk_level, func.count(ContractAnalysis.id))
        .group_by(ContractAnalysis.risk_level)
        .all()
    )
    distribution = {row[0]: row[1] for row in rows if row[0]}
    return [
        {"name": "High Risk", "value": distribution.get("High", 0), "color": "#EF4444"},
        {"name": "Medium Risk", "value": distribution.get("Medium", 0), "color": "#F59E0B"},
        {"name": "Low Risk", "value": distribution.get("Low", 0), "color": "#10B981"},
    ]


@router.get("/clause-coverage")
def clause_coverage(db: Session = Depends(get_db)):
    """Return average clause coverage across analyzed contracts."""
    import json

    analyses = db.query(ContractAnalysis).filter(ContractAnalysis.clauses_json != None).all()
    if not analyses:
        return []

    clause_totals: Dict[str, int] = {}
    clause_found: Dict[str, int] = {}

    for analysis in analyses:
        try:
            clauses = json.loads(analysis.clauses_json)
            for clause in clauses:
                ctype = clause.get("title", clause.get("type", "Unknown"))
                clause_totals[ctype] = clause_totals.get(ctype, 0) + 1
                if clause.get("found"):
                    clause_found[ctype] = clause_found.get(ctype, 0) + 1
        except (json.JSONDecodeError, TypeError):
            continue

    result = []
    for clause_name, total in clause_totals.items():
        found = clause_found.get(clause_name, 0)
        coverage = round((found / total) * 100) if total > 0 else 0
        result.append({"clause": clause_name, "coverage": coverage})

    return sorted(result, key=lambda x: x["coverage"], reverse=True)


@router.get("/recent-contracts")
def recent_contracts(limit: int = 5, db: Session = Depends(get_db)):
    """Return most recently uploaded contracts with risk data."""
    contracts = (
        db.query(Contract)
        .order_by(Contract.upload_date.desc())
        .limit(limit)
        .all()
    )
    result = []
    for c in contracts:
        result.append({
            "id": c.id,
            "name": c.original_name,
            "upload_date": c.upload_date.isoformat(),
            "status": c.status,
            "risk_score": c.analysis.risk_score if c.analysis else None,
            "risk_level": c.analysis.risk_level if c.analysis else None,
        })
    return result
