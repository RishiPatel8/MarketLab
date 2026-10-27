from typing import Dict, Any
from app.agents.state import ResearchWorkflowState
from app.services.quantitative_engine import QuantitativeEngine
from app.providers.market_data.fixture_provider import FixtureMarketDataProvider

def quantitative_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    """
    Quantitative Toolchain Node:
    Executes deterministic calculations for technical indicators and strategy backtesting.
    Strictly isolated from LLM probabilistic operations.
    """
    resolved = state.get("resolved_instrument")
    if not resolved:
        return {"current_step": "verification"}

    symbol = resolved["symbol"]
    exchange = resolved.get("exchange", "NSE")

    provider = FixtureMarketDataProvider()
    bars = provider.get_historical_bars(symbol, exchange)
    benchmark_bars = provider.get_historical_bars("^NSEI", "NSE")

    # 1. Technical Indicators
    tech_indicators = QuantitativeEngine.calculate_technical_indicators(bars)

    # 2. Backtest moving-average crossover (20 / 50 day)
    backtest_metrics = None
    try:
        backtest_metrics = QuantitativeEngine.run_sma_crossover_backtest(
            bars=bars,
            fast_period=20,
            slow_period=50,
            initial_capital=100000.0,
            fee_pct=0.001,
            slippage_pct=0.0005,
            benchmark_bars=benchmark_bars
        ).model_dump()
    except Exception as e:
        backtest_metrics = {"error": str(e)}

    quant_res = {
        "technical_indicators": tech_indicators,
        "backtest_experiment": backtest_metrics,
        "engine_version": QuantitativeEngine.ENGINE_VERSION,
        "methodology": "Next-bar execution at Open with 0.1% fees and 0.05% slippage"
    }

    return {
        "quantitative_results": quant_res,
        "current_step": "verification"
    }
