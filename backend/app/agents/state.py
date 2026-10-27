from typing import TypedDict, Optional, List, Dict, Any

class ResearchWorkflowState(TypedDict):
    run_id: str
    user_id: Optional[str]
    original_question: str
    instrument_candidates: List[Dict[str, Any]]
    resolved_instrument: Optional[Dict[str, Any]]
    research_spec: Optional[Dict[str, Any]]
    market_data_reference: Optional[Dict[str, Any]]
    data_validation: Optional[Dict[str, Any]]
    financial_facts: Optional[Dict[str, Any]]
    retrieved_evidence: List[Dict[str, Any]]
    quantitative_results: Optional[Dict[str, Any]]
    verification_findings: Optional[Dict[str, Any]]
    retry_count: int
    run_status: str
    # queued, running, completed, completed_with_limitations, needs_clarification, failed
    current_step: str
    error_message: Optional[str]
    final_report: Optional[Dict[str, Any]]
