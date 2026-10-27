import pytest
from datetime import datetime, timezone, timedelta
from app.schemas.market_data import MarketBarSchema
from app.services.market_data_service import MarketDataService

def test_market_data_valid_series():
    service = MarketDataService()
    base_date = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
    bars = [
        MarketBarSchema(
            timestamp=base_date + timedelta(days=i),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=50000.0,
            provider="fixture"
        ) for i in range(10)
    ]
    val = service.validate_market_data(bars, "TEST_SYM")
    assert val.is_valid is True
    assert val.anomalies_detected == 0
    assert val.coverage_percentage == 100.0

def test_market_data_invalid_high_detected():
    service = MarketDataService()
    base_date = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
    # High is 90, but Open is 100 and Close is 102 (Invalid!)
    corrupt_bar = MarketBarSchema(
        timestamp=base_date,
        open=100.0,
        high=90.0,
        low=85.0,
        close=102.0,
        volume=50000.0,
        provider="fixture"
    )
    val = service.validate_market_data([corrupt_bar], "CORRUPT")
    assert val.is_valid is False
    assert val.anomalies_detected >= 1
    assert any("Invalid High" in issue for issue in val.issues)

def test_duplicate_timestamps_detected():
    service = MarketDataService()
    dt = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
    b1 = MarketBarSchema(timestamp=dt, open=10.0, high=12.0, low=9.0, close=11.0, volume=100.0)
    b2 = MarketBarSchema(timestamp=dt, open=10.0, high=12.0, low=9.0, close=11.0, volume=100.0)
    val = service.validate_market_data([b1, b2], "DUP_TEST")
    assert val.is_valid is False
    assert any("Duplicate observation" in issue for issue in val.issues)
