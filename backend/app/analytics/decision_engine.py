from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import math

from app.schemas.decision import DecisionReportResponse, PriceTargetScenario
from app.schemas.strategy import StrategyConsensusResult
from app.schemas.fundamental import FundamentalAnalysisResult

class DecisionIntelligenceEngine:
    """
    Deterministic Decision Intelligence and Risk Synthesis Engine.
    Combines technical posture, fundamental valuation (DCF), multi-strategy consensus,
    and market data validation to generate SEBI-compliant BUY/HOLD/SELL/INSUFFICIENT_EVIDENCE
    assessments with concrete entry bands, target scenarios, and stop-loss levels.
    """

    @classmethod
    def evaluate_investment_decision(
        cls,
        current_price: float,
        data_coverage_score: float,
        technical_data: Dict[str, Any],
        fundamental_data: Optional[FundamentalAnalysisResult],
        consensus_result: Optional[StrategyConsensusResult],
        horizon_days: int = 180,
        horizon_category: str = "medium_term",
        investment_amount_inr: float = 50000.0,
        risk_tolerance: str = "moderate"
    ) -> DecisionReportResponse:
        """
        Synthesizes complete decision intelligence report deterministically.
        Strictly prevents generating BUY/HOLD/SELL if underlying data is insufficient.
        """
        now = datetime.now(timezone.utc)

        # 1. Check data sufficiency boundary
        if data_coverage_score < 0.60 or current_price <= 0:
            return DecisionReportResponse(
                decision_rating="INSUFFICIENT_EVIDENCE",
                recommendation_summary=(
                    "Market data or corporate filings coverage is inadequate to form a verified "
                    "quantitative or fundamental thesis. No trade or investment recommendation is generated."
                ),
                current_price=max(0.0, current_price),
                price_timestamp=now,
                entry_range_min=0.0,
                entry_range_max=0.0,
                fair_value_min=0.0,
                fair_value_max=0.0,
                stop_loss_price=0.0,
                risk_reward_ratio=0.0,
                horizon_type=horizon_category,
                investment_amount_inr=investment_amount_inr,
                recommended_position_quantity=0,
                scenarios=[],
                strategy_consensus={},
                evidence_coverage_score=round(data_coverage_score, 2),
                confidence_level="INSUFFICIENT"
            )

        # 2. Extract technical levels
        indicators = technical_data.get("indicators", {})
        pivots = technical_data.get("pivot_levels", {})
        atr = float(indicators.get("atr_14") or (current_price * 0.025))
        s1 = float(pivots.get("s1") or (current_price - (1.5 * atr)))
        r1 = float(pivots.get("r1") or (current_price + (1.5 * atr)))
        r2 = float(pivots.get("r2") or (current_price + (2.5 * atr)))

        # 3. Extract fundamental fair value
        if fundamental_data and fundamental_data.dcf_valuation:
            dcf_val = fundamental_data.dcf_valuation.fair_value_per_share
            fair_min = round(min(dcf_val * 0.90, current_price * 0.95), 2)
            fair_max = round(max(dcf_val * 1.10, current_price * 1.05), 2)
            fund_score = fundamental_data.fundamental_score
        else:
            fair_min = round(current_price * 0.92, 2)
            fair_max = round(current_price * 1.08, 2)
            fund_score = 5.0

        # 4. Entry range & stop-loss calculations
        # Entry range: between support S1/EMA and CMP
        entry_min = round(max(s1, current_price - (0.75 * atr)), 2)
        entry_max = round(current_price * 1.01, 2)
        if entry_min >= entry_max:
            entry_min = round(current_price * 0.98, 2)

        # Stop-loss: based on ATR multiplier and risk tolerance
        risk_multipliers = {"conservative": 1.5, "moderate": 2.0, "aggressive": 2.5}
        mult = risk_multipliers.get(risk_tolerance.lower(), 2.0)
        stop_loss = round(current_price - (mult * atr), 2)
        if stop_loss >= current_price:
            stop_loss = round(current_price * 0.95, 2)

        # 5. Position sizing in INR
        # Conservative allocates 20%, Moderate 35%, Aggressive 50% max of portfolio to single name
        alloc_caps = {"conservative": 0.20, "moderate": 0.35, "aggressive": 0.50}
        cap_fraction = alloc_caps.get(risk_tolerance.lower(), 0.35)
        allocated_capital = investment_amount_inr * cap_fraction
        recommended_shares = max(1, int(allocated_capital // current_price))

        # 6. Scenarios (Bull, Base, Bear)
        # Horizon scaling
        horizon_factor = 1.0
        if horizon_days <= 30:
            horizon_factor = 0.4  # short term
        elif horizon_days >= 365:
            horizon_factor = 1.8  # long term

        bull_ret = round(min(45.0, max(12.0, 18.0 * horizon_factor)), 1)
        base_ret = round(min(25.0, max(5.0, 9.0 * horizon_factor)), 1)
        bear_ret = round(-max(8.0, 12.0 * min(1.0, horizon_factor)), 1)

        bull_target = round(current_price * (1.0 + (bull_ret / 100.0)), 2)
        base_target = round(current_price * (1.0 + (base_ret / 100.0)), 2)
        bear_target = round(current_price * (1.0 + (bear_ret / 100.0)), 2)

        scenarios = [
            PriceTargetScenario(
                scenario="BULL",
                probability=0.25,
                target_price=bull_target,
                expected_return_pct=bull_ret,
                rationale=f"Breakout past R2 (₹{r2}) driven by earnings acceleration and institutional inflows."
            ),
            PriceTargetScenario(
                scenario="BASE",
                probability=0.50,
                target_price=base_target,
                expected_return_pct=base_ret,
                rationale=f"Convergence toward intrinsic fair value (₹{fair_max}) supported by baseline business execution."
            ),
            PriceTargetScenario(
                scenario="BEAR",
                probability=0.25,
                target_price=bear_target,
                expected_return_pct=bear_ret,
                rationale=f"Loss of S1 (₹{s1}) support under sector macro headwinds or broader market contraction."
            )
        ]

        # 7. Risk / Reward calculation
        upside = max(0.01, base_target - current_price)
        downside = max(0.01, current_price - stop_loss)
        rr_ratio = round(upside / downside, 2)

        # 8. Decision Rating Synthesis
        tech_score = float(technical_data.get("technical_score", 5.0))
        consensus_rating = consensus_result.consensus_rating if consensus_result else "HOLD"
        consensus_pct = consensus_result.consensus_percentage if consensus_result else 50.0

        # Weighted decision matrix
        bullish_points = 0
        if tech_score >= 6.5:
            bullish_points += 2
        if fund_score >= 6.5:
            bullish_points += 2
        if consensus_rating == "BUY":
            bullish_points += 2
        if rr_ratio >= 1.5:
            bullish_points += 1

        bearish_points = 0
        if tech_score <= 4.0:
            bearish_points += 2
        if fund_score <= 4.0:
            bearish_points += 2
        if consensus_rating == "SELL":
            bearish_points += 2
        if rr_ratio < 1.0:
            bearish_points += 1

        if bullish_points >= 4 and bearish_points <= 1:
            rating = "BUY"
            summary = (
                f"Quantitative consensus ({consensus_pct}% agreement) and technical indicators align with an attractive "
                f"risk/reward ratio of {rr_ratio}:1. Potential entry is identified between ₹{entry_min} and ₹{entry_max} "
                f"with a Base Target of ₹{base_target} ({base_ret:+.1f}%) and disciplined stop loss at ₹{stop_loss}."
            )
            conf = "HIGH" if bullish_points >= 6 else "MODERATE"
        elif bearish_points >= 4:
            rating = "SELL"
            summary = (
                f"Technical trend deterioration and valuation headwinds suggest caution. Quantitative consensus "
                f"signals defensive repositioning. Downside risk toward ₹{bear_target} ({bear_ret:+.1f}%) exceeds upside potential."
            )
            conf = "HIGH" if bearish_points >= 5 else "MODERATE"
        else:
            rating = "HOLD"
            summary = (
                f"Mixed signals between valuation metrics and technical momentum indicate consolidation. "
                f"The stock trades within expected fair value range (₹{fair_min} to ₹{fair_max}). Maintain position or wait "
                f"for a decisive breakout above ₹{r1} before deploying new capital."
            )
            conf = "MODERATE"

        return DecisionReportResponse(
            decision_rating=rating,
            recommendation_summary=summary,
            current_price=round(current_price, 2),
            price_timestamp=now,
            entry_range_min=entry_min,
            entry_range_max=entry_max,
            fair_value_min=fair_min,
            fair_value_max=fair_max,
            stop_loss_price=stop_loss,
            risk_reward_ratio=rr_ratio,
            horizon_type=horizon_category,
            investment_amount_inr=investment_amount_inr,
            recommended_position_quantity=recommended_shares,
            scenarios=scenarios,
            strategy_consensus=consensus_result.model_dump() if hasattr(consensus_result, "model_dump") else (consensus_result.dict() if consensus_result else {}),
            evidence_coverage_score=round(data_coverage_score, 2),
            confidence_level=conf
        )
