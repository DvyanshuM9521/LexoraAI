import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services import contract_service
from app.schemas.contract import AnalysisResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/{contract_id}/analyze", response_model=AnalysisResponse)
def analyze_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")

    try:
        analysis = contract_service.analyze_contract(db, contract_id)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not analysis:
        raise HTTPException(status_code=500, detail="Analysis failed.")

    return _build_response(contract_id, analysis)


@router.get("/{contract_id}", response_model=AnalysisResponse)
def get_analysis(contract_id: int, db: Session = Depends(get_db)):
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")

    analysis = contract_service.get_analysis(db, contract_id)
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found. Please run analysis first."
        )

    return _build_response(contract_id, analysis)


def _build_response(contract_id: int, analysis) -> AnalysisResponse:
    clauses = json.loads(analysis.clauses_json) if analysis.clauses_json else []
    risk = json.loads(analysis.risk_factors_json) if analysis.risk_factors_json else {}
    summary = json.loads(analysis.summary_json) if analysis.summary_json else {}
    recommendations = json.loads(analysis.recommendations_json) if analysis.recommendations_json else []

    return AnalysisResponse(
        contract_id=contract_id,
        clauses=clauses,
        risk=risk,
        summary=summary,
        recommendations=recommendations,
    )
