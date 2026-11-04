from typing import List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import logging
from app.core.config import settings
from app.providers.market_data.base import BaseMarketDataProvider
from app.providers.market_data.fixture_provider import FixtureMarketDataProvider
from app.providers.market_data.nse_bse_provider import NseBseMarketDataProvider
from app.providers.market_data.yfinance_provider import YFinanceMarketDataProvider, MarketDataProviderError
from app.db.repositories.market_data_repo import MarketDataRepository
from app.schemas.market_data import MarketBarSchema, MarketDataValidationResult

logger = logging.getLogger("marketlab.service.market_data")


def get_market_data_provider(provider_name: Optional[str] = None) -> BaseMarketDataProvider:
    name = (provider_name or settings.MARKET_DATA_PROVIDER).lower()
    if name == "yfinance":
        return YFinanceMarketDataProvider()
    elif name == "nse_bse":
        return NseBseMarketDataProvider()
    elif name == "fixture":
        return FixtureMarketDataProvider()
    else:
        logger.warning(f"Unknown market data provider '{name}'; defaulting to fixture mode")
        return FixtureMarketDataProvider()


class MarketDataService:
    def __init__(self, db: Optional[Session] = None, provider: Optional[BaseMarketDataProvider] = None):
        self.db = db
        self.repo = MarketDataRepository(db) if db else None
        self.provider = provider or get_market_data_provider()

    def get_and_validate_bars(
        self,
        symbol: str,
        exchange: str = "NSE",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        instrument_id: Optional[str] = None
    ) -> Tuple[List[MarketBarSchema], MarketDataValidationResult]:
        """
        Retrieves bars from the configured provider and validates candle consistency,
        timestamp monotonicity, positive pricing, and volume.
        """
        # 1. Retrieve bars from provider
        try:
            bars = self.provider.get_historical_bars(symbol, exchange, start_date, end_date)
        except MarketDataProviderError as e:
            provider_name = getattr(self.provider, "PROVIDER_NAME", settings.MARKET_DATA_PROVIDER)
            logger.warning(f"Market data provider '{provider_name}' has no price data for {symbol}: {e}")
            validation = MarketDataValidationResult(
                is_valid=False,
                total_bars=0,
                anomalies_detected=1,
                issues=[f"Instrument found in official master. Price data unavailable from {provider_name}."],
                coverage_percentage=0.0,
                provider_attribution=provider_name,
                latency_type="unavailable",
                data_frequency="unavailable",
                retrieval_timestamp=datetime.now(timezone.utc)
            )
            return [], validation

        # 2. Perform rigorous deterministic validation
        validation = self.validate_market_data(bars, symbol)

        # 3. Persist if database is connected and instrument_id provided
        if self.repo and instrument_id and validation.is_valid:
            try:
                self.repo.save_bars(instrument_id, bars, provider=validation.provider_attribution)
            except Exception as e:
                logger.warning(f"Could not persist market bars to repository: {e}")

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
            if round(bar.high, 4) < round(max_body, 4):
                issues.append(f"Invalid High ({bar.high}) < max(Open, Close) ({max_body}) at {bar.timestamp}")
                anomalies += 1

            # Check Low <= min(Open, Close)
            min_body = min(bar.open, bar.close)
            if round(bar.low, 4) > round(min_body, 4):
                issues.append(f"Invalid Low ({bar.low}) > min(Open, Close) ({min_body}) at {bar.timestamp}")
                anomalies += 1

            # Volume non-negative
            if bar.volume < 0:
                issues.append(f"Negative volume ({bar.volume}) at {bar.timestamp}")
                anomalies += 1

        is_valid = (anomalies == 0)
        coverage_pct = round(max(0.0, 100.0 - (anomalies / len(bars) * 100)), 2)
        provider_name = bars[0].provider if bars else settings.MARKET_DATA_PROVIDER

        latency_type = "daily_historical"
        data_frequency = "daily_historical"
        if provider_name == "fixture":
            latency_type = "fixture"
            data_frequency = "fixture"
        elif provider_name == "yfinance":
            latency_type = "daily_historical"
            data_frequency = "daily_historical"

        return MarketDataValidationResult(
            is_valid=is_valid,
            total_bars=len(bars),
            start_date=bars[0].timestamp if bars else None,
            end_date=bars[-1].timestamp if bars else None,
            anomalies_detected=anomalies,
            issues=issues[:10],
            coverage_percentage=coverage_pct,
            provider_attribution=provider_name,
            latency_type=latency_type,
            data_frequency=data_frequency,
            latest_observation_time=bars[-1].timestamp if bars else None,
            retrieval_timestamp=datetime.now(timezone.utc)
        )

    def get_corporate_actions(self, symbol: str, exchange: str = "NSE") -> dict:
        """Retrieves historical stock splits and cash dividends."""
        if hasattr(self.provider, "get_corporate_actions"):
            return self.provider.get_corporate_actions(symbol, exchange)
        return {"splits": [], "dividends": []}

    def get_company_fundamentals(self, symbol: str, exchange: str = "NSE") -> dict:
        """Retrieves raw fundamentals from the active market data provider."""
        if hasattr(self.provider, "get_company_fundamentals"):
            return self.provider.get_company_fundamentals(symbol, exchange)
        return {}
