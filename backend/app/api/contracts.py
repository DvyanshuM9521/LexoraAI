import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.services import contract_service
from app.schemas.contract import ContractResponse, ContractListItem

router = APIRouter(prefix="/contracts", tags=["contracts"])

ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/upload", response_model=ContractResponse)
async def upload_contract(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds the 50MB size limit.")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    contract = contract_service.create_contract(db, content, file.filename)
    return contract


@router.get("/", response_model=List[ContractListItem])
def list_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contracts = contract_service.list_contracts(db, skip=skip, limit=limit)
    result = []
    for c in contracts:
        item = ContractListItem(
            id=c.id,
            original_name=c.original_name,
            upload_date=c.upload_date,
            status=c.status,
            page_count=c.page_count,
            word_count=c.word_count,
            risk_score=c.analysis.risk_score if c.analysis else None,
            risk_level=c.analysis.risk_level if c.analysis else None,
        )
        result.append(item)
    return result


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")
    return contract


@router.delete("/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    deleted = contract_service.delete_contract(db, contract_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contract not found.")
    return {"message": "Contract deleted successfully."}


@router.get("/{contract_id}/file")
def serve_contract_file(contract_id: int, db: Session = Depends(get_db)):
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")
    if not os.path.exists(contract.file_path):
        raise HTTPException(status_code=404, detail="Contract file not found on disk.")
    return FileResponse(
        contract.file_path,
        media_type="application/pdf",
        filename=contract.original_name,
        headers={"Content-Disposition": f'inline; filename="{contract.original_name}"'},
    )
