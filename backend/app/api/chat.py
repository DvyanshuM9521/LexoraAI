import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.services import contract_service
from app.services.chat_service import generate_chat_response
from app.schemas.contract import ChatMessageRequest, ChatMessageResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{contract_id}/message", response_model=ChatMessageResponse)
def send_message(
    contract_id: int,
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")

    if not contract.text_content:
        raise HTTPException(
            status_code=400,
            detail="Contract has not been analyzed yet. Please analyze the contract first to enable the AI assistant."
        )

    analysis = contract_service.get_analysis(db, contract_id)
    clauses = json.loads(analysis.clauses_json) if analysis and analysis.clauses_json else []
    risk = json.loads(analysis.risk_factors_json) if analysis and analysis.risk_factors_json else {}

    # Get chat history
    history = contract_service.get_chat_history(db, contract_id)
    history_dicts = [{"role": m.role, "content": m.content} for m in history[-10:]]

    # Save user message
    contract_service.save_chat_message(db, contract_id, "user", request.message.strip())

    # Generate response
    response_text = generate_chat_response(
        question=request.message.strip(),
        text=contract.text_content,
        clauses=clauses,
        risk_data=risk,
        history=history_dicts,
    )

    # Save assistant response
    saved = contract_service.save_chat_message(db, contract_id, "assistant", response_text)
    return saved


@router.get("/{contract_id}/history", response_model=List[ChatMessageResponse])
def get_history(contract_id: int, db: Session = Depends(get_db)):
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")
    return contract_service.get_chat_history(db, contract_id)


@router.delete("/{contract_id}/history")
def clear_history(contract_id: int, db: Session = Depends(get_db)):
    from app.models.contract import ChatMessage as ChatMessageModel
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")
    db.query(ChatMessageModel).filter(ChatMessageModel.contract_id == contract_id).delete()
    db.commit()
    return {"message": "Chat history cleared."}
