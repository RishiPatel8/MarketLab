import pytest
from app.analytics.fundamental_engine import FundamentalEngine
from app.analytics.technical_engine import TechnicalEngine
from app.providers.market_data.fixture_provider import FixtureMarketDataProvider

def test_dcf_valuation_calculation():
    """Verify DCF valuation and sensitivity matrix output."""
    dcf = FundamentalEngine.compute_dcf_valuation(
        free_cash_flow_cr=100.0,
        current_market_price=1000.0,
        shares_outstanding_cr=1.0,
        projected_growth_rate=12.0,
        terminal_growth_rate=4.5,
        wacc=11.0,
        projection_years=5
    )
    assert dcf.fair_value_per_share > 0
    assert dcf.valuation_status in ("UNDERVALUED", "FAIRLY_VALUED", "OVERVALUED")
    assert len(dcf.sensitivity_matrix) == 5  # 5 WACC levels
    for wacc_key, g_dict in dcf.sensitivity_matrix.items():
        assert len(g_dict) == 3  # 3 growth levels

def test_dupont_roe_decomposition():
    """Verify DuPont 3-stage ROE decomposition calculation."""
    dupont = FundamentalEngine.compute_dupont_analysis(
        net_profit=150.0,
        revenue=1000.0,
        total_assets=1200.0,
        total_equity=600.0
    )
    assert dupont.roe == 25.0
    assert dupont.net_profit_margin == 15.0
    assert dupont.asset_turnover == 0.83
    assert dupont.equity_multiplier == 2.0
    assert len(dupont.interpretation) > 10

def test_fundamental_analysis_synthesis():
    """Verify fundamental analysis score and summary generation."""
    raw = {
        "current_price": 2800.0,
        "revenue": 90000.0,
        "net_profit": 15000.0,
        "free_cash_flow": 12000.0,
        "pe_ratio": 22.5,
        "debt_to_equity": 0.35,
        "equity": 80000.0
    }
    res = FundamentalEngine.analyze_fundamentals(raw, "RELIANCE", "Reliance Industries")
    assert 1.0 <= res.fundamental_score <= 10.0
    assert res.dcf_valuation is not None
    assert res.dupont is not None
    assert "Reliance Industries" in res.summary

def test_technical_engine_full_suite():
    """Verify calculation of full technical suite (SMAs, EMAs, RSI, MACD, Bollinger, ATR, ADX, VWAP, Pivots)."""
    provider = FixtureMarketDataProvider()
    bars = provider.get_historical_bars("RELIANCE", "NSE")
    assert len(bars) >= 200

    tech = TechnicalEngine.calculate_full_technical_suite(bars)
    ind = tech["indicators"]
    piv = tech["pivot_levels"]
    mtf = tech["multi_timeframe"]

    # Assert indicators populated
    assert ind["sma_20"] is not None
    assert ind["sma_50"] is not None
    assert ind["ema_9"] is not None
    assert ind["ema_21"] is not None
    assert 0 <= ind["rsi_14"] <= 100
    assert ind["macd_line"] is not None
    assert ind["macd_histogram"] is not None
    assert ind["bb_upper"] > ind["bb_middle"] > ind["bb_lower"]
    assert ind["atr_14"] > 0
    assert ind["adx_14"] > 0
    assert ind["vwap"] > 0

    # Assert pivot levels
    assert piv["r1"] > piv["pivot"] > piv["s1"]
    assert piv["r2"] > piv["r1"]
    assert piv["s2"] < piv["s1"]

    # Assert multi-timeframe alignment
    assert mtf["short_term"] in ("BULLISH", "BEARISH")
    assert mtf["alignment"] in ("STRONG_BULLISH", "MODERATE_BULLISH", "NEUTRAL", "MODERATE_BEARISH", "STRONG_BEARISH")
    assert 1.0 <= tech["technical_score"] <= 10.0
    assert len(tech["summary"]) > 20
