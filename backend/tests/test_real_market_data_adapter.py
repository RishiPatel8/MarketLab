import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd
from app.providers.market_data.yfinance_provider import YFinanceMarketDataProvider, MarketDataProviderError
from app.providers.market_data.nse_bse_provider import NseBseMarketDataProvider
from app.providers.market_data.fixture_provider import FixtureMarketDataProvider
from app.services.market_data_service import get_market_data_provider, MarketDataService
from app.schemas.market_data import MarketBarSchema


def test_yfinance_symbol_resolution():
    provider = YFinanceMarketDataProvider()
    assert provider.resolve_provider_symbol("GREENPOWER", "NSE") == "GREENPOWER.NS"
    assert provider.resolve_provider_symbol("RELIANCE", "NSE") == "RELIANCE.NS"
    assert provider.resolve_provider_symbol("INFY", "NSE") == "INFY.NS"
    assert provider.resolve_provider_symbol("^NSEI", "NSE") == "^NSEI"
    assert provider.resolve_provider_symbol("NIFTY50", "NSE") == "^NSEI"
    assert provider.resolve_provider_symbol("TATASTEEL", "BSE") == "TATASTEEL.BO"


def test_yfinance_data_normalization_offline():
    provider = YFinanceMarketDataProvider()
    
    # Create synthetic raw dataframe simulating yfinance output
    dates = pd.date_range(start="2026-01-01", periods=3, tz="Asia/Kolkata")
    mock_df = pd.DataFrame({
        "Open": [10.0, 11.0, 12.0],
        "High": [12.0, 13.0, 14.0],
        "Low": [9.5, 10.5, 11.5],
        "Close": [11.5, 12.5, 13.5],
        "Adj Close": [11.5, 12.5, 13.5],
        "Volume": [100000, 150000, 200000]
    }, index=dates)

    with patch("yfinance.Ticker") as mock_ticker_class:
        mock_instance = MagicMock()
        mock_instance.history.return_value = mock_df
        mock_ticker_class.return_value = mock_instance

        bars = provider.get_historical_bars("GREENPOWER", "NSE")
        assert len(bars) == 3
        assert bars[0].timestamp.tzinfo == timezone.utc
        assert bars[0].open == 10.0
        assert bars[0].high == 12.0
        assert bars[0].low == 9.5
        assert bars[0].close == 11.5
        assert bars[0].volume == 100000
        assert bars[0].provider == "yfinance"


def test_yfinance_empty_response_raises_provider_error():
    provider = YFinanceMarketDataProvider(max_retries=1)
    with patch("yfinance.Ticker") as mock_ticker_class:
        mock_instance = MagicMock()
        mock_instance.history.return_value = pd.DataFrame()
        mock_ticker_class.return_value = mock_instance

        with pytest.raises(MarketDataProviderError) as exc_info:
            provider.get_historical_bars("INVALID_SYMBOL", "NSE")
        assert "No historical market data returned" in str(exc_info.value)


def test_nse_bse_provider_fails_without_credentials_no_silent_fallback():
    provider = NseBseMarketDataProvider(api_key=None, api_endpoint=None)
    with pytest.raises(MarketDataProviderError) as exc_info:
        provider.get_historical_bars("GREENPOWER", "NSE")
    assert "Direct NSE exchange API credentials/endpoint are not configured" in str(exc_info.value)
    assert "Silent fallback to fixture data is disabled" in str(exc_info.value)


def test_fixture_market_data_provider_explicit_fixture_mode():
    provider = FixtureMarketDataProvider()
    bars = provider.get_historical_bars("GREENPOWER", "NSE")
    assert len(bars) > 0
    assert bars[0].provider == "fixture"


def test_provider_factory_selection():
    p_fix = get_market_data_provider("fixture")
    assert isinstance(p_fix, FixtureMarketDataProvider)

    p_yf = get_market_data_provider("yfinance")
    assert isinstance(p_yf, YFinanceMarketDataProvider)

    p_nse = get_market_data_provider("nse_bse")
    assert isinstance(p_nse, NseBseMarketDataProvider)
