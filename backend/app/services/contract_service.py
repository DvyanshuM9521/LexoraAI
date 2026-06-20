import os
import json
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractAnalysis, ChatMessage
from app.utils.pdf_utils import extract_text_from_pdf, count_words, clean_text, get_file_size
from app.services.clause_extractor import extract_all_clauses
from app.services.risk_engine import calculate_risk
from app.services.summary_engine import generate_summary
from app.services.recommendation_engine import generate_recommendations

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOADS_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def save_uploaded_file(file_content: bytes, original_filename: str) -> str:
    """Save an uploaded file and return the stored file path."""
    ext = os.path.splitext(original_filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOADS_DIR, unique_name)
    with open(file_path, "wb") as f:
        f.write(file_content)
    return file_path, unique_name


def create_contract(db: Session, file_content: bytes, original_filename: str) -> Contract:
    """Create a new contract record from uploaded file."""
    file_path, stored_name = save_uploaded_file(file_content, original_filename)
    file_size = get_file_size(file_path)

    contract = Contract(
        filename=stored_name,
        original_name=original_filename,
        file_path=file_path,
        file_size=file_size,
        status="uploaded",
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


def analyze_contract(db: Session, contract_id: int) -> Optional[ContractAnalysis]:
    """Run full analysis pipeline on a contract."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        return None

    try:
        # Extract text
        text, page_count = extract_text_from_pdf(contract.file_path)
        text = clean_text(text)
        word_count = count_words(text)

        contract.text_content = text
        contract.page_count = page_count
        contract.word_count = word_count
        contract.status = "analyzed"
        db.commit()

        # Run analysis engines
        clauses = extract_all_clauses(text)
        risk = calculate_risk(text, clauses)
        summary = generate_summary(text, clauses, risk)
        recommendations = generate_recommendations(risk)
    except Exception as e:
        contract.status = "error"
        db.commit()
        raise RuntimeError(f"Analysis pipeline failed: {e}") from e

    # Persist analysis
    existing = db.query(ContractAnalysis).filter(ContractAnalysis.contract_id == contract_id).first()
    if existing:
        existing.clauses_json = json.dumps(clauses)
        existing.risk_score = risk["score"]
        existing.risk_level = risk["level"]
        existing.risk_factors_json = json.dumps(risk)
        existing.summary_json = json.dumps(summary)
        existing.recommendations_json = json.dumps(recommendations)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    analysis = ContractAnalysis(
        contract_id=contract_id,
        clauses_json=json.dumps(clauses),
        risk_score=risk["score"],
        risk_level=risk["level"],
        risk_factors_json=json.dumps(risk),
        summary_json=json.dumps(summary),
        recommendations_json=json.dumps(recommendations),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_contract(db: Session, contract_id: int) -> Optional[Contract]:
    return db.query(Contract).filter(Contract.id == contract_id).first()


def list_contracts(db: Session, skip: int = 0, limit: int = 100) -> List[Contract]:
    return db.query(Contract).order_by(Contract.upload_date.desc()).offset(skip).limit(limit).all()


def delete_contract(db: Session, contract_id: int) -> bool:
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        return False
    # Remove file
    if os.path.exists(contract.file_path):
        os.remove(contract.file_path)
    db.delete(contract)
    db.commit()
    return True


def get_analysis(db: Session, contract_id: int) -> Optional[ContractAnalysis]:
    return db.query(ContractAnalysis).filter(ContractAnalysis.contract_id == contract_id).first()


def get_chat_history(db: Session, contract_id: int) -> List[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.contract_id == contract_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def save_chat_message(db: Session, contract_id: int, role: str, content: str) -> ChatMessage:
    msg = ChatMessage(contract_id=contract_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
