from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.providers.market_data.fixture_provider import FixtureMarketDataProvider
from app.providers.market_data.nse_bse_provider import NseBseMarketDataProvider
from app.db.repositories.market_data_repo import MarketDataRepository
from app.schemas.market_data import MarketBarSchema, MarketDataValidationResult

class MarketDataService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.repo = MarketDataRepository(db) if db else None
        
        if settings.MARKET_DATA_PROVIDER == "nse_bse":
            self.provider = NseBseMarketDataProvider()
        else:
            self.provider = FixtureMarketDataProvider()

    def get_and_validate_bars(
        self,
        symbol: str,
        exchange: str = "NSE",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        instrument_id: Optional[str] = None
    ) -> Tuple[List[MarketBarSchema], MarketDataValidationResult]:
        # 1. Retrieve bars from provider
        bars = self.provider.get_historical_bars(symbol, exchange, start_date, end_date)
        
        # 2. Perform rigorous deterministic validation
        validation = self.validate_market_data(bars, symbol)
        
        # 3. Persist if database is connected and instrument_id provided
        if self.repo and instrument_id and validation.is_valid:
            self.repo.save_bars(instrument_id, bars, provider=validation.provider_attribution)

        return bars, validation

    def validate_market_data(self, bars: List[MarketBarSchema], symbol: str) -> MarketDataValidationResult:
        if not bars:
            return MarketDataValidationResult(
                is_valid=False,
                total_bars=0,
                anomalies_detected=1,
                issues=[f"No market data available for {symbol}"],
                coverage_percentage=0.0,
                provider_attribution=settings.MARKET_DATA_PROVIDER,
                latency_type="end_of_day"
            )

        issues: List[str] = []
        anomalies = 0
        seen_timestamps = set()

        for idx, bar in enumerate(bars):
            # Check duplicate timestamps
            if bar.timestamp in seen_timestamps:
                issues.append(f"Duplicate observation at {bar.timestamp}")
                anomalies += 1
            seen_timestamps.add(bar.timestamp)

            # Check prices positive
            if bar.open <= 0 or bar.high <= 0 or bar.low <= 0 or bar.close <= 0:
                issues.append(f"Non-positive price at bar {idx} ({bar.timestamp})")
                anomalies += 1

            # Check High >= max(Open, Close)
            max_body = max(bar.open, bar.close)
            if bar.high < max_body:
                issues.append(f"Invalid High ({bar.high}) < max(Open, Close) ({max_body}) at {bar.timestamp}")
                anomalies += 1

            # Check Low <= min(Open, Close)
            min_body = min(bar.open, bar.close)
            if bar.low > min_body:
                issues.append(f"Invalid Low ({bar.low}) > min(Open, Close) ({min_body}) at {bar.timestamp}")
                anomalies += 1

            # Volume non-negative
            if bar.volume < 0:
                issues.append(f"Negative volume ({bar.volume}) at {bar.timestamp}")
                anomalies += 1

        is_valid = (anomalies == 0)
        coverage_pct = round(max(0.0, 100.0 - (anomalies / len(bars) * 100)), 2)

        return MarketDataValidationResult(
            is_valid=is_valid,
            total_bars=len(bars),
            start_date=bars[0].timestamp if bars else None,
            end_date=bars[-1].timestamp if bars else None,
            anomalies_detected=anomalies,
            issues=issues[:10],  # cap reported issues
            coverage_percentage=coverage_pct,
            provider_attribution=bars[0].provider if bars else settings.MARKET_DATA_PROVIDER,
            latency_type="end_of_day"
        )
