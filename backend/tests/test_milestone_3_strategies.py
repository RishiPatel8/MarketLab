import pytest
from app.analytics.strategy_engine import StrategyRegistry
from app.providers.market_data.fixture_provider import FixtureMarketDataProvider

def test_strategy_registry_ten_strategies_available():
    """Verify all 10 required strategies are registered and discoverable."""
    strategies = StrategyRegistry.list_strategies()
    assert len(strategies) >= 10
    keys = {s.strategy_key for s in strategies}
    required_keys = {
        "sma_crossover", "ema_crossover", "rsi_threshold", "macd_momentum",
        "bollinger_bands", "mean_reversion", "momentum_breakout", "volume_breakout",
        "fundamental_value", "risk_parity"
    }
    assert required_keys.issubset(keys)

def test_individual_strategy_execution_and_metrics():
    """Verify execution of multiple strategies on historical bars."""
    provider = FixtureMarketDataProvider()
    bars = provider.get_historical_bars("RELIANCE", "NSE")
    bench = provider.get_historical_bars("^NSEI", "NSE")

    test_keys = ["sma_crossover", "ema_crossover", "rsi_threshold", "macd_momentum", "bollinger_bands"]
    for k in test_keys:
        res = StrategyRegistry.run_strategy(
            key=k,
            bars=bars,
            initial_capital=100000.0,
            fee_pct=0.001,
            slippage_pct=0.0005,
            benchmark_bars=bench
        )
        assert res.cagr is not None
        assert res.sharpe_ratio is not None
        assert res.max_drawdown >= 0.0
        assert 0.0 <= res.win_rate <= 1.0
        assert len(res.equity_curve) > 0
        assert res.out_of_sample_metrics is not None
        assert "out_of_sample_bars" in res.out_of_sample_metrics

def test_multi_strategy_consensus_engine():
    """Verify multi-strategy ensemble voting and consensus score calculation."""
    provider = FixtureMarketDataProvider()
    bars = provider.get_historical_bars("RELIANCE", "NSE")
    bench = provider.get_historical_bars("^NSEI", "NSE")

    consensus = StrategyRegistry.run_multi_strategy_consensus(
        bars=bars,
        benchmark_bars=bench
    )
    assert consensus.total_strategies >= 8
    assert consensus.consensus_rating in ("BUY", "HOLD", "SELL", "INSUFFICIENT_EVIDENCE")
    assert 0.0 <= consensus.consensus_percentage <= 100.0
    assert len(consensus.signals) == consensus.total_strategies
    for s in consensus.signals:
        assert s.signal in ("BUY", "HOLD", "SELL", "NEUTRAL")
        assert len(s.summary) > 5
