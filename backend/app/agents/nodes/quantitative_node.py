from typing import Dict, Any
import logging
from app.agents.state import ResearchWorkflowState
from app.services.quantitative_engine import QuantitativeEngine
from app.services.market_data_service import get_market_data_provider

logger = logging.getLogger("marketlab.agent.quantitative")


from app.analytics.technical_engine import TechnicalEngine
from app.analytics.strategy_engine import StrategyRegistry

def quantitative_node(state: ResearchWorkflowState) -> Dict[str, Any]:
    """
    Quantitative Toolchain Node:
    Executes deterministic calculations for technical indicators, full technical suite,
    individual backtests, and multi-strategy consensus evaluation.
    Strictly isolated from LLM probabilistic operations. Uses configured market data provider.
    """
    resolved = state.get("resolved_instrument")
    if not resolved:
        return {"current_step": "verification"}

    symbol = resolved["symbol"]
    exchange = resolved.get("exchange", "NSE")

    provider = get_market_data_provider()
    try:
        bars = provider.get_historical_bars(symbol, exchange)
    except Exception as e:
        logger.error(f"Failed to fetch bars for quantitative engine: {e}")
        bars = []

    try:
        benchmark_bars = provider.get_historical_bars("^NSEI", "NSE")
    except Exception as e:
        logger.warning(f"Failed to fetch benchmark bars (^NSEI): {e}")
        benchmark_bars = []

    # 1. Technical Indicators (Legacy + Full Suite)
    tech_indicators = QuantitativeEngine.calculate_technical_indicators(bars) if bars else {}
    tech_suite = TechnicalEngine.calculate_full_technical_suite(bars) if bars else {}

    # 2. Backtest moving-average crossover (20 / 50 day)
    backtest_metrics = None
    if len(bars) >= 50:
        try:
            backtest_metrics = QuantitativeEngine.run_sma_crossover_backtest(
                bars=bars,
                fast_period=20,
                slow_period=50,
                initial_capital=100000.0,
                fee_pct=0.001,
                slippage_pct=0.0005,
                benchmark_bars=benchmark_bars if benchmark_bars else None
            ).model_dump()
        except Exception as e:
            backtest_metrics = {"error": str(e)}
    else:
        backtest_metrics = {
            "error": f"Insufficient bars ({len(bars)}) for 50-day SMA backtest."
        }

    # 3. Multi-Strategy Consensus
    try:
        consensus_res = StrategyRegistry.run_multi_strategy_consensus(
            bars=bars,
            benchmark_bars=benchmark_bars if benchmark_bars else None
        )
        consensus_data = consensus_res.model_dump() if hasattr(consensus_res, "model_dump") else consensus_res.dict()
    except Exception as e:
        logger.warning(f"Consensus execution failed: {e}")
        consensus_data = {"error": str(e)}

    quant_res = {
        "technical_indicators": tech_indicators,
        "technical_suite": tech_suite,
        "backtest_experiment": backtest_metrics,
        "strategy_consensus": consensus_data,
        "engine_version": QuantitativeEngine.ENGINE_VERSION,
        "methodology": "Next-bar execution at Open with 0.1% fees and 0.05% slippage",
        "provider": getattr(provider, "PROVIDER_NAME", type(provider).__name__)
    }

    return {
        "quantitative_results": quant_res,
        "technical_analysis": tech_suite,
        "strategy_consensus": consensus_data,
        "current_step": "verification"
    }
