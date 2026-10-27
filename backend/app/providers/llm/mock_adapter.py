from typing import Dict, Any, Optional
import json
from app.providers.llm.base import BaseLLMAdapter

class MockLLMAdapter(BaseLLMAdapter):
    """
    Deterministic LLM adapter for testing and offline development.
    Produces schema-compliant structured outputs grounded in evidence.
    """

    def generate_json_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        prompt_lower = user_prompt.lower()
        
        # Check if this is the verifier node
        if "critic" in system_prompt.lower() or "verifier" in system_prompt.lower():
            return {
                "verification_passed": True,
                "evidence_coverage_score": 0.95,
                "data_freshness_status": "fresh",
                "contradictions_detected": [],
                "unsupported_claims_flagged": [],
                "calculation_consistency": True,
                "look_ahead_bias_audit": "passed",
                "recommendations": ["Report conforms to rigorous empirical standards."]
            }

        # Check if this is planner node
        if "planner" in system_prompt.lower() or "research plan" in prompt_lower:
            return {
                "requested_analyses": ["market_data", "financial_facts", "technical_indicators", "rag_evidence", "risk_factors"],
                "horizon_days": 180,
                "benchmark_symbol": "^NSEI",
                "reasoning": "Standard equity evaluation with technical indicators and filings evidence."
            }

        # Default structured fallback
        return {
            "status": "success",
            "message": "Deterministic structured response generated."
        }

    def generate_text_response(self, system_prompt: str, user_prompt: str) -> str:
        return (
            "MarketLab AI Executive Analysis: Based on retrieved regulatory disclosures and "
            "deterministic quantitative indicators, the instrument exhibits stable operating metrics "
            "with notable debt reduction progress, balanced against seasonal volume cyclicality."
        )
