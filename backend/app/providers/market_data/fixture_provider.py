from typing import List, Optional, Dict
from datetime import datetime, timedelta, timezone
import numpy as np
from app.providers.market_data.base import BaseMarketDataProvider
from app.schemas.market_data import MarketBarSchema

class FixtureMarketDataProvider(BaseMarketDataProvider):
    """
    Deterministic historical market data provider for development, testing,
    and fallback validation of Indian Equities.
    Clearly marks all observations with provider='fixture'.
    """

    def __init__(self):
        self._cached_series: Dict[str, List[MarketBarSchema]] = {}
        self._generate_baseline_fixtures()

    def _generate_baseline_fixtures(self):
        # We generate 365 days of deterministic trading data ending on 2026-10-25
        base_date = datetime(2025, 10, 25, 15, 30, tzinfo=timezone.utc)
        
        configs = {
            "GREENPOWER": {"base_price": 18.5, "drift": 0.0004, "vol": 0.022, "vol_base": 1500000},
            "RELIANCE": {"base_price": 2750.0, "drift": 0.0003, "vol": 0.012, "vol_base": 4500000},
            "TATAMOTORS": {"base_price": 820.0, "drift": 0.0005, "vol": 0.018, "vol_base": 3200000},
            "INFY": {"base_price": 1650.0, "drift": 0.0002, "vol": 0.014, "vol_base": 2800000},
            "^NSEI": {"base_price": 23500.0, "drift": 0.0003, "vol": 0.008, "vol_base": 85000000},
            "NIFTY50": {"base_price": 23500.0, "drift": 0.0003, "vol": 0.008, "vol_base": 85000000},
        }

        for symbol, cfg in configs.items():
            bars: List[MarketBarSchema] = []
            # Use deterministic seed for reproducibility
            seed_val = sum(ord(c) for c in symbol) + 42
            rng = np.random.RandomState(seed_val)
            
            current_close = cfg["base_price"]
            # Generate 260 trading days
            days_count = 260
            dates = []
            cur_dt = base_date - timedelta(days=380)
            while len(dates) < days_count:
                # Skip weekends
                if cur_dt.weekday() < 5:
                    dates.append(cur_dt)
                cur_dt += timedelta(days=1)

            for dt in dates:
                ret = rng.normal(cfg["drift"], cfg["vol"])
                # Calculate prices
                open_price = round(current_close * (1 + rng.normal(0, cfg["vol"] * 0.3)), 2)
                close_price = round(open_price * (1 + ret), 2)
                
                # Enforce High >= max(Open, Close) and Low <= min(Open, Close)
                high_delta = abs(rng.normal(0, cfg["vol"] * 0.5)) * open_price
                low_delta = abs(rng.normal(0, cfg["vol"] * 0.5)) * open_price
                
                high_price = round(max(open_price, close_price) + high_delta, 2)
                low_price = round(min(open_price, close_price) - low_delta, 2)
                if low_price <= 0:
                    low_price = round(min(open_price, close_price) * 0.9, 2)

                vol = round(cfg["vol_base"] * (1 + rng.uniform(-0.3, 0.5)), 0)

                bars.append(MarketBarSchema(
                    timestamp=dt,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    adjusted_close=close_price,
                    volume=float(vol),
                    provider="fixture"
                ))
                current_close = close_price

            self._cached_series[symbol.upper()] = bars

    def get_historical_bars(
        self,
        symbol: str,
        exchange: str = "NSE",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MarketBarSchema]:
        sym = symbol.upper()
        bars = self._cached_series.get(sym)
        if not bars:
            # Fallback for unknown ticker: generate dynamic deterministic series
            rng = np.random.RandomState(sum(ord(c) for c in sym))
            base_p = float(rng.randint(50, 500))
            bars = []
            cur_dt = datetime.now(timezone.utc) - timedelta(days=180)
            for i in range(120):
                if cur_dt.weekday() < 5:
                    op = round(base_p * (1 + rng.normal(0, 0.01)), 2)
                    cp = round(op * (1 + rng.normal(0.0003, 0.015)), 2)
                    hp = round(max(op, cp) * (1 + abs(rng.normal(0, 0.005))), 2)
                    lp = round(min(op, cp) * (1 - abs(rng.normal(0, 0.005))), 2)
                    bars.append(MarketBarSchema(
                        timestamp=cur_dt,
                        open=op,
                        high=hp,
                        low=lp,
                        close=cp,
                        adjusted_close=cp,
                        volume=500000.0,
                        provider="fixture"
                    ))
                    base_p = cp
                cur_dt += timedelta(days=1)
            self._cached_series[sym] = bars

        # Filter by date if provided
        filtered = bars
        if start_date:
            filtered = [b for b in filtered if b.timestamp >= start_date]
        if end_date:
            filtered = [b for b in filtered if b.timestamp <= end_date]
        return filtered

    def get_latest_price(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        bars = self.get_historical_bars(symbol, exchange)
        if bars:
            return bars[-1].close
        return None
