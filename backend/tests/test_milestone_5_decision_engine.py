import pytest
from app.analytics.decision_engine import DecisionIntelligenceEngine
from app.schemas.strategy import StrategyConsensusResult, StrategySignal
from app.schemas.fundamental import FundamentalAnalysisResult, DCFValuationResult, DuPontAnalysisResult

def test_decision_insufficient_evidence_boundary():
    """Verify INSUFFICIENT_EVIDENCE is triggered when data coverage is inadequate (< 60%)."""
    res = DecisionIntelligenceEngine.evaluate_investment_decision(
        current_price=2500.0,
        data_coverage_score=0.45,  # Low coverage
        technical_data={},
        fundamental_data=None,
        consensus_result=None
    )
    assert res.decision_rating == "INSUFFICIENT_EVIDENCE"
    assert res.confidence_level == "INSUFFICIENT"
    assert len(res.scenarios) == 0
    assert "inadequate" in res.recommendation_summary.lower()
    assert "SEBI Non-Advisory Notice" in res.sebi_non_advisory_notice

def test_decision_buy_scenario_generation():
    """Verify BUY rating and scenario targets when signals and valuation are positive."""
    tech_data = {
        "technical_score": 8.0,
        "indicators": {"atr_14": 45.0},
        "pivot_levels": {"s1": 2400.0, "r1": 2600.0, "r2": 2750.0}
    }
    dcf = DCFValuationResult(
        fair_value_per_share=2900.0,
        current_market_price=2500.0,
        margin_of_safety_pct=13.79,
        projected_growth_rate=12.0,
        terminal_growth_rate=4.5,
        wacc=10.5,
        valuation_status="UNDERVALUED"
    )
    dupont = DuPontAnalysisResult(roe=18.5, net_profit_margin=16.0, asset_turnover=0.9, equity_multiplier=1.3, interpretation="Strong")
    fund_res = FundamentalAnalysisResult(
        symbol="RELIANCE",
        company_name="Reliance Industries",
        fiscal_period="FY2025",
        fundamental_score=8.0,
        dcf_valuation=dcf,
        dupont=dupont,
        summary="Strong fundamentals"
    )
    consensus = StrategyConsensusResult(
        total_strategies=8,
        buy_signals=6,
        hold_signals=2,
        sell_signals=0,
        consensus_rating="BUY",
        consensus_percentage=75.0,
        signals=[]
    )

    res = DecisionIntelligenceEngine.evaluate_investment_decision(
        current_price=2500.0,
        data_coverage_score=0.95,
        technical_data=tech_data,
        fundamental_data=fund_res,
        consensus_result=consensus,
        horizon_days=180,
        investment_amount_inr=50000.0,
        risk_tolerance="moderate"
    )

    assert res.decision_rating == "BUY"
    assert res.confidence_level in ("HIGH", "MODERATE")
    assert res.entry_range_min < res.entry_range_max
    assert res.stop_loss_price < res.current_price
    assert res.risk_reward_ratio >= 1.0
    assert len(res.scenarios) == 3
    scen_names = {s.scenario for s in res.scenarios}
    assert scen_names == {"BULL", "BASE", "BEAR"}
    assert res.recommended_position_quantity > 0
    assert "SEBI" in res.sebi_non_advisory_notice

def test_decision_hold_scenario():
    """Verify HOLD rating when signals are mixed."""
    tech_data = {
        "technical_score": 5.0,
        "indicators": {"atr_14": 40.0},
        "pivot_levels": {"s1": 2420.0, "r1": 2580.0}
    }
    consensus = StrategyConsensusResult(
        total_strategies=8,
        buy_signals=3,
        hold_signals=4,
        sell_signals=1,
        consensus_rating="HOLD",
        consensus_percentage=50.0,
        signals=[]
    )
    res = DecisionIntelligenceEngine.evaluate_investment_decision(
        current_price=2500.0,
        data_coverage_score=0.90,
        technical_data=tech_data,
        fundamental_data=None,
        consensus_result=consensus
    )
    assert res.decision_rating == "HOLD"
    assert "consolidation" in res.recommendation_summary.lower() or "fair value" in res.recommendation_summary.lower()
