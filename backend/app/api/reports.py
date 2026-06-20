import json
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services import contract_service
from app.services.report_service import generate_pdf_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/{contract_id}/generate")
def generate_report(contract_id: int, db: Session = Depends(get_db)):
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")

    analysis = contract_service.get_analysis(db, contract_id)
    if not analysis:
        raise HTTPException(
            status_code=400,
            detail="Contract has not been analyzed. Please analyze the contract first."
        )

    clauses = json.loads(analysis.clauses_json) if analysis.clauses_json else []
    risk = json.loads(analysis.risk_factors_json) if analysis.risk_factors_json else {}
    summary = json.loads(analysis.summary_json) if analysis.summary_json else {}
    recommendations = json.loads(analysis.recommendations_json) if analysis.recommendations_json else []

    output_filename = f"lexora_report_{contract_id}_{contract.filename.replace('.pdf', '')}.pdf"
    output_path = os.path.join(REPORTS_DIR, output_filename)

    contract_dict = {
        "original_name": contract.original_name,
        "upload_date": contract.upload_date.isoformat() if contract.upload_date else "",
        "page_count": contract.page_count,
        "word_count": contract.word_count,
    }

    generate_pdf_report(
        contract=contract_dict,
        clauses=clauses,
        risk=risk,
        summary=summary,
        recommendations=recommendations,
        output_path=output_path,
    )

    return {"report_url": f"/api/reports/{contract_id}/download", "filename": output_filename}


@router.get("/{contract_id}/download")
def download_report(contract_id: int, db: Session = Depends(get_db)):
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")

    # Find latest report
    for fname in sorted(os.listdir(REPORTS_DIR), reverse=True):
        if fname.startswith(f"lexora_report_{contract_id}_"):
            fpath = os.path.join(REPORTS_DIR, fname)
            return FileResponse(
                fpath,
                media_type="application/pdf",
                filename=f"Lexora_Report_{contract.original_name}",
                headers={"Content-Disposition": f'attachment; filename="Lexora_Report_{contract.original_name}"'},
            )

    raise HTTPException(status_code=404, detail="Report not generated yet. Please generate the report first.")
