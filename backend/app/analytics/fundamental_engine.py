from typing import Dict, Any, List, Optional
import math
from app.schemas.fundamental import (
    DCFValuationResult,
    DuPontAnalysisResult,
    PeerComparisonItem,
    FundamentalAnalysisResult
)

class FundamentalEngine:
    """
    Deterministic Fundamental Research and Valuation Engine.
    Executes DCF models, DuPont 3-stage ROE breakdowns, and financial ratio synthesis
    in pure Python and NumPy — strictly isolated from probabilistic LLM operations.
    """

    @staticmethod
    def compute_dcf_valuation(
        free_cash_flow_cr: float,
        current_market_price: float,
        shares_outstanding_cr: float = 1.0,
        projected_growth_rate: float = 10.0,  # e.g., 10%
        terminal_growth_rate: float = 4.5,     # e.g., 4.5% long-term Indian GDP growth rate
        wacc: float = 11.0,                    # e.g., 11% cost of capital in India
        projection_years: int = 5
    ) -> DCFValuationResult:
        """
        Calculates DCF intrinsic value per share and constructs a WACC vs Terminal Growth sensitivity matrix.
        """
        if free_cash_flow_cr <= 0:
            # For companies with negative FCF, apply normalized floor or return conservative valuation
            free_cash_flow_cr = max(1.0, free_cash_flow_cr)

        g_proj = projected_growth_rate / 100.0
        g_term = terminal_growth_rate / 100.0
        r_wacc = wacc / 100.0

        # Protect against denominator <= 0
        if r_wacc <= g_term:
            r_wacc = g_term + 0.02

        # 1. Project cash flows for projection_years
        pv_cf = 0.0
        cf_t = free_cash_flow_cr
        for t in range(1, projection_years + 1):
            cf_t = cf_t * (1.0 + g_proj)
            pv_cf += cf_t / ((1.0 + r_wacc) ** t)

        # 2. Terminal Value (Gordon Growth)
        terminal_cf = cf_t * (1.0 + g_term)
        tv = terminal_cf / (r_wacc - g_term)
        pv_tv = tv / ((1.0 + r_wacc) ** projection_years)

        # 3. Total Intrinsic Equity Value
        total_equity_value_cr = pv_cf + pv_tv
        intrinsic_value_per_share = round(total_equity_value_cr / max(shares_outstanding_cr, 0.01), 2)

        # Margin of safety: (Intrinsic - CMP) / Intrinsic * 100
        if intrinsic_value_per_share > 0:
            margin_of_safety = round(((intrinsic_value_per_share - current_market_price) / intrinsic_value_per_share) * 100.0, 2)
        else:
            margin_of_safety = 0.0

        if margin_of_safety >= 15.0:
            status = "UNDERVALUED"
        elif margin_of_safety <= -15.0:
            status = "OVERVALUED"
        else:
            status = "FAIRLY_VALUED"

        # 4. Generate Sensitivity Matrix (WACC 9% to 13%, Terminal Growth 3% to 6%)
        sensitivity: Dict[str, Dict[str, float]] = {}
        for test_wacc in [9.0, 10.0, 11.0, 12.0, 13.0]:
            wacc_key = f"{test_wacc}%"
            sensitivity[wacc_key] = {}
            for test_g in [3.5, 4.5, 5.5]:
                g_key = f"{test_g}%"
                rw = test_wacc / 100.0
                rg = test_g / 100.0
                if rw <= rg:
                    rw = rg + 0.01
                
                pv_test = 0.0
                c_test = free_cash_flow_cr
                for t in range(1, projection_years + 1):
                    c_test = c_test * (1.0 + g_proj)
                    pv_test += c_test / ((1.0 + rw) ** t)
                tv_test = (c_test * (1.0 + rg)) / (rw - rg)
                pv_tv_test = tv_test / ((1.0 + rw) ** projection_years)
                val_per_share = round((pv_test + pv_tv_test) / max(shares_outstanding_cr, 0.01), 2)
                sensitivity[wacc_key][g_key] = val_per_share

        return DCFValuationResult(
            fair_value_per_share=intrinsic_value_per_share,
            current_market_price=round(current_market_price, 2),
            margin_of_safety_pct=margin_of_safety,
            projected_growth_rate=projected_growth_rate,
            terminal_growth_rate=terminal_growth_rate,
            wacc=wacc,
            valuation_status=status,
            sensitivity_matrix=sensitivity
        )

    @staticmethod
    def compute_dupont_analysis(
        net_profit: float,
        revenue: float,
        total_assets: float,
        total_equity: float
    ) -> DuPontAnalysisResult:
        """
        3-Stage DuPont ROE Decomposition:
        ROE = (Net Profit / Revenue) * (Revenue / Assets) * (Assets / Equity)
            = Net Margin * Asset Turnover * Financial Leverage
        """
        if revenue <= 0 or total_assets <= 0 or total_equity <= 0:
            return DuPontAnalysisResult(
                roe=0.0,
                net_profit_margin=0.0,
                asset_turnover=0.0,
                equity_multiplier=1.0,
                interpretation="Insufficient balance sheet data for complete DuPont decomposition."
            )

        npm = (net_profit / revenue) * 100.0
        asset_turnover = revenue / total_assets
        leverage = total_assets / total_equity
        roe = (net_profit / total_equity) * 100.0

        if npm > 15 and leverage < 2.5:
            interp = "High quality ROE driven by superior profit margins and prudent capital structure."
        elif leverage >= 3.0:
            interp = "ROE is heavily augmented by financial leverage. Scrutinize debt serviceability."
        elif asset_turnover > 1.5:
            interp = "ROE driven by high operational asset efficiency and inventory turnover."
        else:
            interp = "Balanced ROE components across operations and capital structure."

        return DuPontAnalysisResult(
            roe=round(roe, 2),
            net_profit_margin=round(npm, 2),
            asset_turnover=round(asset_turnover, 2),
            equity_multiplier=round(leverage, 2),
            interpretation=interp
        )

    @classmethod
    def analyze_fundamentals(
        cls,
        raw_data: Dict[str, Any],
        symbol: str,
        company_name: str = "",
        peers: Optional[List[PeerComparisonItem]] = None
    ) -> FundamentalAnalysisResult:
        """
        Synthesizes fundamental metrics, valuations, and scores into a typed FundamentalAnalysisResult.
        """
        curr_price = float(raw_data.get("current_price") or raw_data.get("latest_close") or 100.0)
        fcf = float(raw_data.get("free_cash_flow") or 0.0)
        # Normalize FCF to Crores if in absolute rupees
        if fcf > 10000000:
            fcf = fcf / 10000000.0
        elif fcf == 0.0:
            # Estimate FCF as 65% of net profit if FCF is unpopulated
            np_est = float(raw_data.get("net_profit") or 100.0)
            fcf = np_est * 0.65

        shares_est = float(raw_data.get("shares_outstanding") or 1.0)
        if shares_est > 10000000:
            shares_est = shares_est / 10000000.0

        # DCF valuation
        dcf_result = cls.compute_dcf_valuation(
            free_cash_flow_cr=fcf,
            current_market_price=curr_price,
            shares_outstanding_cr=max(1.0, shares_est)
        )

        # DuPont
        rev = float(raw_data.get("revenue") or 1000.0)
        np_val = float(raw_data.get("net_profit") or 150.0)
        eq_val = float(raw_data.get("equity") or 800.0)
        assets_val = eq_val * 1.5
        dupont_res = cls.compute_dupont_analysis(np_val, rev, assets_val, eq_val)

        # Fundamental Score (0 to 10)
        score = 5.0
        pe = raw_data.get("pe_ratio")
        if pe and 0 < float(pe) < 25:
            score += 1.5
        elif pe and float(pe) > 40:
            score -= 1.0

        roe = raw_data.get("roe") or dupont_res.roe
        if roe and float(roe) > 15:
            score += 1.5
        elif roe and float(roe) < 5:
            score -= 1.0

        de = raw_data.get("debt_to_equity")
        if de and float(de) < 0.5:
            score += 1.0
        elif de and float(de) > 2.0:
            score -= 1.5

        if dcf_result.valuation_status == "UNDERVALUED":
            score += 1.0
        elif dcf_result.valuation_status == "OVERVALUED":
            score -= 1.0

        score = max(1.0, min(10.0, round(score, 1)))

        summary_parts = [
            f"Fundamental analysis for {company_name or symbol} yields a score of {score}/10.",
            f"DCF valuation indicates an intrinsic fair value of ₹{dcf_result.fair_value_per_share} vs current price of ₹{curr_price} ({dcf_result.valuation_status}, margin of safety: {dcf_result.margin_of_safety_pct}%).",
            f"DuPont ROE is {dupont_res.roe}% with operating net margin of {dupont_res.net_profit_margin}%."
        ]

        return FundamentalAnalysisResult(
            symbol=symbol,
            company_name=company_name or symbol,
            fiscal_period=str(raw_data.get("fiscal_period") or "FY2025 (TTM)"),
            revenue_cr=round(rev, 2),
            operating_profit_cr=round(float(raw_data.get("operating_profit") or (rev * 0.2)), 2),
            net_profit_cr=round(np_val, 2),
            eps=round(float(raw_data.get("eps") or (np_val / max(1.0, shares_est))), 2),
            roe=round(float(roe), 2),
            roce=round(float(raw_data.get("roce") or (float(roe) * 1.1)), 2),
            operating_margin=round(float(raw_data.get("operating_margin") or 20.0), 2),
            net_margin=round(dupont_res.net_profit_margin, 2),
            debt_to_equity=round(float(de or 0.4), 2),
            free_cash_flow_cr=round(fcf, 2),
            dcf_valuation=dcf_result,
            dupont=dupont_res,
            peers=peers or [],
            fundamental_score=score,
            summary=" ".join(summary_parts)
        )
