from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="uploaded")  # uploaded | analyzed | error
    text_content = Column(Text, nullable=True)
    page_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)

    analysis = relationship("ContractAnalysis", back_populates="contract", uselist=False, cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="contract", cascade="all, delete-orphan")


class ContractAnalysis(Base):
    __tablename__ = "contract_analyses"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Clause data (JSON stored as text)
    clauses_json = Column(Text, nullable=True)

    # Risk data
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="Unknown")
    risk_factors_json = Column(Text, nullable=True)

    # Summary data
    summary_json = Column(Text, nullable=True)

    # Recommendations
    recommendations_json = Column(Text, nullable=True)

    contract = relationship("Contract", back_populates="analysis")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="chat_messages")
