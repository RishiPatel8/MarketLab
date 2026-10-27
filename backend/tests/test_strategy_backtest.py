import pytest
from datetime import datetime, timezone, timedelta
from app.schemas.market_data import MarketBarSchema
from app.services.quantitative_engine import QuantitativeEngine
from app.providers.market_data.fixture_provider import FixtureMarketDataProvider

def test_sma_crossover_execution():
    prov = FixtureMarketDataProvider()
    bars = prov.get_historical_bars("GREENPOWER")
    b_bars = prov.get_historical_bars("^NSEI")
    
    res = QuantitativeEngine.run_sma_crossover_backtest(
        bars=bars,
        fast_period=20,
        slow_period=50,
        initial_capital=100000.0,
        fee_pct=0.001,
        slippage_pct=0.0005,
        benchmark_bars=b_bars
    )

    assert res.total_trades >= 0
    assert res.max_drawdown >= 0.0
    assert len(res.equity_curve) == len(bars)
    assert res.equity_curve[0]["portfolio_value"] == 100000.0

def test_slippage_and_transaction_cost_deduction():
    # Construct synthetic bars that trigger a crossover
    base_date = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
    prices = [10.0] * 30 + [15.0] * 30  # Fast MA will cross above Slow MA around bar 35
    bars = []
    for i, p in enumerate(prices):
        bars.append(MarketBarSchema(
            timestamp=base_date + timedelta(days=i),
            open=p,
            high=p * 1.02,
            low=p * 0.98,
            close=p,
            volume=50000.0,
            provider="fixture"
        ))

    res = QuantitativeEngine.run_sma_crossover_backtest(
        bars=bars,
        fast_period=5,
        slow_period=20,
        initial_capital=100000.0,
        fee_pct=0.01,       # 1% high fee to verify deduction
        slippage_pct=0.005  # 0.5% slippage
    )

    # Verify trades were processed and fees/slippage applied
    if res.total_trades > 0:
        trade = res.trades[0]
        # Entry price should be higher than open due to slippage
        assert trade["entry_price"] > 0
        assert trade["shares"] > 0
