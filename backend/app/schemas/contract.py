from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ContractBase(BaseModel):
    original_name: str


class ContractResponse(BaseModel):
    id: int
    filename: str
    original_name: str
    file_size: int
    upload_date: datetime
    status: str
    page_count: int
    word_count: int

    model_config = {"from_attributes": True}


class ClauseItem(BaseModel):
    type: str
    title: str
    content: str
    found: bool
    confidence: float


class RiskFactor(BaseModel):
    factor: str
    severity: str
    explanation: str
    present: bool


class RiskAnalysis(BaseModel):
    score: float
    level: str
    factors: List[RiskFactor]
    summary: str


class SummaryResponse(BaseModel):
    purpose: str
    parties: List[str]
    duration: str
    key_obligations: List[str]
    key_risks: List[str]
    recommendations_preview: List[str]


class Recommendation(BaseModel):
    id: int
    issue: str
    business_impact: str
    suggested_action: str
    severity: str
    category: str


class ComparisonRequest(BaseModel):
    contract_a_id: int
    contract_b_id: int


class ClauseChange(BaseModel):
    clause_type: str
    title: str
    contract_a: str
    contract_b: str
    change_type: str  # added | removed | modified | unchanged
    impact: str
    impact_level: str  # high | medium | low | none


class ComparisonReport(BaseModel):
    contract_a: ContractResponse
    contract_b: ContractResponse
    overall_impact: str
    risk_delta: float
    changes: List[ClauseChange]
    summary: str


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisResponse(BaseModel):
    contract_id: int
    clauses: List[ClauseItem]
    risk: RiskAnalysis
    summary: SummaryResponse
    recommendations: List[Recommendation]


class DashboardStats(BaseModel):
    total_contracts: int
    high_risk: int
    medium_risk: int
    low_risk: int
    analyzed: int
    pending: int


class ContractListItem(BaseModel):
    id: int
    original_name: str
    upload_date: datetime
    status: str
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    page_count: int
    word_count: int

    model_config = {"from_attributes": True}
