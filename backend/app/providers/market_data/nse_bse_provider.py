from typing import List, Optional
from datetime import datetime
import logging
from app.providers.market_data.base import BaseMarketDataProvider
from app.providers.market_data.yfinance_provider import MarketDataProviderError
from app.schemas.market_data import MarketBarSchema

logger = logging.getLogger("marketlab.provider.nse")


class NseBseMarketDataProvider(BaseMarketDataProvider):
    """
    Direct exchange market data provider adapter for Indian Equities (NSE/BSE).
    Requires authorized exchange API credentials or gateway configuration.
    Strictly forbids silent fallback to fixture data when live mode is selected.
    """

    def __init__(self, api_key: Optional[str] = None, api_endpoint: Optional[str] = None):
        self.api_key = api_key
        self.api_endpoint = api_endpoint

    def get_historical_bars(
        self,
        symbol: str,
        exchange: str = "NSE",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MarketBarSchema]:
        logger.info(f"Retrieving market data via direct exchange adapter for {exchange}:{symbol}")
        if not self.api_key or not self.api_endpoint:
            raise MarketDataProviderError(
                f"Direct {exchange} exchange API credentials/endpoint are not configured. "
                "Silent fallback to fixture data is disabled in live provider mode. "
                "Configure licensed exchange credentials or set MARKET_DATA_PROVIDER=yfinance for historical data."
            )
        # Direct gateway query logic when credentials are provided
        raise MarketDataProviderError(f"Direct connection to {exchange} gateway {self.api_endpoint} failed.")

    def get_latest_price(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        bars = self.get_historical_bars(symbol, exchange)
        return bars[-1].close if bars else None
