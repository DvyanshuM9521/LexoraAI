import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services import contract_service
from app.services.comparison_engine import compare_contracts
from app.schemas.contract import ComparisonRequest, ComparisonReport

router = APIRouter(prefix="/comparison", tags=["comparison"])


@router.post("/", response_model=ComparisonReport)
def compare(request: ComparisonRequest, db: Session = Depends(get_db)):
    contract_a = contract_service.get_contract(db, request.contract_a_id)
    contract_b = contract_service.get_contract(db, request.contract_b_id)

    if not contract_a:
        raise HTTPException(status_code=404, detail=f"Contract A (id={request.contract_a_id}) not found.")
    if not contract_b:
        raise HTTPException(status_code=404, detail=f"Contract B (id={request.contract_b_id}) not found.")

    analysis_a = contract_service.get_analysis(db, request.contract_a_id)
    analysis_b = contract_service.get_analysis(db, request.contract_b_id)

    if not analysis_a:
        raise HTTPException(status_code=400, detail="Contract A has not been analyzed yet. Please analyze it first.")
    if not analysis_b:
        raise HTTPException(status_code=400, detail="Contract B has not been analyzed yet. Please analyze it first.")

    clauses_a = json.loads(analysis_a.clauses_json) if analysis_a.clauses_json else []
    clauses_b = json.loads(analysis_b.clauses_json) if analysis_b.clauses_json else []
    risk_a = json.loads(analysis_a.risk_factors_json) if analysis_a.risk_factors_json else {}
    risk_b = json.loads(analysis_b.risk_factors_json) if analysis_b.risk_factors_json else {}

    result = compare_contracts(
        contract_a={"original_name": contract_a.original_name},
        contract_b={"original_name": contract_b.original_name},
        clauses_a=clauses_a,
        clauses_b=clauses_b,
        risk_a=risk_a,
        risk_b=risk_b,
    )

    return ComparisonReport(
        contract_a=contract_a,
        contract_b=contract_b,
        overall_impact=result["overall_impact"],
        risk_delta=result["risk_delta"],
        changes=result["changes"],
        summary=result["summary"],
    )
