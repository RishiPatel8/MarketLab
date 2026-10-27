import pytest
from datetime import datetime, timezone, timedelta
from app.schemas.market_data import MarketBarSchema
from app.services.quantitative_engine import QuantitativeEngine

def generate_synthetic_bars(prices):
    base_date = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
    bars = []
    for i, p in enumerate(prices):
        bars.append(MarketBarSchema(
            timestamp=base_date + timedelta(days=i),
            open=p,
            high=p * 1.01,
            low=p * 0.99,
            close=p,
            volume=100000.0,
            provider="fixture"
        ))
    return bars

def test_sma_calculation():
    # 25 constant prices of 100.0
    prices = [100.0] * 25
    bars = generate_synthetic_bars(prices)
    tech = QuantitativeEngine.calculate_technical_indicators(bars)
    assert tech["sma_20"] == 100.0
    assert tech["latest_close"] == 100.0

def test_rsi_bounds():
    # Upward trending prices
    prices = [10.0 + i * 0.5 for i in range(30)]
    bars = generate_synthetic_bars(prices)
    tech = QuantitativeEngine.calculate_technical_indicators(bars)
    assert tech["rsi_14"] is not None
    assert 0.0 <= tech["rsi_14"] <= 100.0
    # Consistently increasing series has high RSI
    assert tech["rsi_14"] > 70.0

def test_volatility_calculation():
    prices = [50.0 + (i % 2) * 5.0 for i in range(40)]
    bars = generate_synthetic_bars(prices)
    tech = QuantitativeEngine.calculate_technical_indicators(bars)
    assert tech["annualized_volatility"] is not None
    assert tech["annualized_volatility"] > 0.0
