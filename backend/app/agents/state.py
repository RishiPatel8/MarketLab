from typing import TypedDict, Optional, List, Dict, Any

class ResearchWorkflowState(TypedDict):
    run_id: str
    user_id: Optional[str]
    original_question: str
    investment_amount_inr: Optional[float]
    horizon_days: Optional[int]
    horizon_category: Optional[str]
    risk_tolerance: Optional[str]
    instrument_candidates: List[Dict[str, Any]]
    resolved_instrument: Optional[Dict[str, Any]]
    research_spec: Optional[Dict[str, Any]]
    market_data_reference: Optional[Dict[str, Any]]
    data_validation: Optional[Dict[str, Any]]
    financial_facts: Optional[Dict[str, Any]]
    fundamental_analysis: Optional[Dict[str, Any]]
    retrieved_evidence: List[Dict[str, Any]]
    quantitative_results: Optional[Dict[str, Any]]
    technical_analysis: Optional[Dict[str, Any]]
    strategy_consensus: Optional[Dict[str, Any]]
    verification_findings: Optional[Dict[str, Any]]
    decision_result: Optional[Dict[str, Any]]
    retry_count: int
    run_status: str
    # queued, running, completed, completed_with_limitations, needs_clarification, failed
    current_step: str
    error_message: Optional[str]
    final_report: Optional[Dict[str, Any]]
