from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.schemas.market_data import MarketBarSchema

class BaseMarketDataProvider(ABC):
    @abstractmethod
    def get_historical_bars(
        self,
        symbol: str,
        exchange: str = "NSE",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MarketBarSchema]:
        """Retrieve historical OHLCV bars for the specified instrument."""
        pass

    @abstractmethod
    def get_latest_price(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        """Retrieve the latest observed price."""
        pass
