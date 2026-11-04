from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
import logging
import time
import math
import pandas as pd
from app.providers.market_data.base import BaseMarketDataProvider
from app.schemas.market_data import MarketBarSchema

logger = logging.getLogger("marketlab.provider.yfinance")


class MarketDataProviderError(Exception):
    """Raised when external market data retrieval fails."""
    pass


class YFinanceMarketDataProvider(BaseMarketDataProvider):
    """
    Historical and delayed market data provider for Indian equities using yfinance.
    Note: yfinance provides delayed/historical data and is an unofficial interface.
    """

    PROVIDER_NAME = "yfinance"
    SYMBOL_MAP = {
        "GREENPOWER": "GREENPOWER.NS",
        "RELIANCE": "RELIANCE.NS",
        "TATAMOTORS": "TATAMOTORS.NS",
        "INFY": "INFY.NS",
        "TATASTEEL": "TATASTEEL.NS",
        "TATAPOWER": "TATAPOWER.NS",
        "^NSEI": "^NSEI",
        "NIFTY50": "^NSEI",
    }

    def __init__(self, max_retries: int = 3, retry_backoff_sec: float = 1.0):
        self.max_retries = max_retries
        self.retry_backoff_sec = retry_backoff_sec

    def resolve_provider_symbol(self, symbol: str, exchange: str = "NSE") -> str:
        sym_clean = symbol.strip().upper()
        if sym_clean.startswith("^"):
            return sym_clean
        if sym_clean in ("NIFTY50", "NIFTY"):
            return "^NSEI"
        if sym_clean in ("SENSEX", "BSESENSEX"):
            return "^BSESN"

        if exchange.upper() == "BSE":
            base = sym_clean.replace(".NS", "").replace(".BO", "")
            return f"{base}.BO"

        if sym_clean in self.SYMBOL_MAP:
            return self.SYMBOL_MAP[sym_clean]

        # If already formatted with suffix
        if sym_clean.endswith(".NS") or sym_clean.endswith(".BO"):
            return sym_clean

        return f"{sym_clean}.NS"

    def get_historical_bars(
        self,
        symbol: str,
        exchange: str = "NSE",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MarketBarSchema]:
        import yfinance as yf

        provider_symbol = self.resolve_provider_symbol(symbol, exchange)
        logger.info(f"Fetching historical bars from yfinance for {provider_symbol}")

        # Set default date range if not provided (last 365 days)
        now = datetime.now(timezone.utc)
        if not end_date:
            end_date = now
        if not start_date:
            start_date = end_date - timedelta(days=365)

        start_str = start_date.strftime("%Y-%m-%d")
        # Add 1 day to end_date because yfinance end date is exclusive
        end_str = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")

        last_error = None
        df = None

        for attempt in range(1, self.max_retries + 1):
            try:
                ticker = yf.Ticker(provider_symbol)
                df = ticker.history(start=start_str, end=end_str, auto_adjust=False)
                if df is not None and not df.empty:
                    break
                logger.warning(f"Empty dataframe returned for {provider_symbol} on attempt {attempt}")
            except Exception as e:
                last_error = e
                logger.warning(f"yfinance attempt {attempt}/{self.max_retries} failed for {provider_symbol}: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_backoff_sec * (2 ** (attempt - 1)))

        if df is None or df.empty:
            err_msg = f"No historical market data returned from yfinance for {provider_symbol} ({start_str} to {end_str})."
            if last_error:
                err_msg += f" Error details: {str(last_error)}"
            raise MarketDataProviderError(err_msg)

        # Normalize and validate dataframe into MarketBarSchema
        bars: List[MarketBarSchema] = []
        seen_timestamps = set()

        # Ensure index is datetime and sorted
        df = df.sort_index()

        for raw_ts, row in df.iterrows():
            # Timezone normalization
            if hasattr(raw_ts, "to_pydatetime"):
                ts = raw_ts.to_pydatetime()
            elif isinstance(raw_ts, datetime):
                ts = raw_ts
            else:
                ts = pd.to_datetime(raw_ts).to_pydatetime()

            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            else:
                ts = ts.astimezone(timezone.utc)

            # Prevent duplicate observations
            if ts in seen_timestamps:
                continue
            seen_timestamps.add(ts)

            # Extract OHLCV
            try:
                open_val = float(row.get("Open", 0))
                high_val = float(row.get("High", 0))
                low_val = float(row.get("Low", 0))
                close_val = float(row.get("Close", 0))
                adj_close = float(row.get("Adj Close", close_val)) if "Adj Close" in row and not math.isnan(row.get("Adj Close")) else close_val
                volume_val = float(row.get("Volume", 0))
            except (ValueError, TypeError):
                continue

            # Drop invalid / NaN candles
            if any(math.isnan(v) for v in [open_val, high_val, low_val, close_val]):
                continue

            # Check positive prices and candle boundaries
            if open_val <= 0 or high_val <= 0 or low_val <= 0 or close_val <= 0:
                continue

            # Enforce candle consistency
            high_val = max(high_val, open_val, close_val)
            low_val = min(low_val, open_val, close_val)
            volume_val = max(0.0, volume_val if not math.isnan(volume_val) else 0.0)

            bars.append(MarketBarSchema(
                timestamp=ts,
                open=round(open_val, 4),
                high=round(high_val, 4),
                low=round(low_val, 4),
                close=round(close_val, 4),
                adjusted_close=round(adj_close, 4),
                volume=round(volume_val, 2),
                provider="yfinance"
            ))

        if not bars:
            raise MarketDataProviderError(f"Market data retrieved for {provider_symbol} contained no valid candles.")

        return bars

    def get_latest_price(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        try:
            bars = self.get_historical_bars(symbol, exchange)
            if bars:
                return bars[-1].close
        except Exception as e:
            logger.error(f"Failed to fetch latest price for {symbol}: {e}")
            raise MarketDataProviderError(f"Unable to retrieve latest price for {symbol}: {e}")
        return None

    def get_corporate_actions(self, symbol: str, exchange: str = "NSE") -> dict:
        import yfinance as yf
        provider_symbol = self.resolve_provider_symbol(symbol, exchange)
        try:
            ticker = yf.Ticker(provider_symbol)
            splits = ticker.splits
            dividends = ticker.dividends
            splits_list = []
            if splits is not None and not splits.empty:
                for date, ratio in splits.items():
                    splits_list.append({"date": str(date), "ratio": float(ratio)})
            dividends_list = []
            if dividends is not None and not dividends.empty:
                for date, amount in dividends.items():
                    dividends_list.append({"date": str(date), "amount": float(amount)})
            return {"splits": splits_list, "dividends": dividends_list}
        except Exception as e:
            logger.warning(f"Could not retrieve corporate actions for {provider_symbol}: {e}")
            return {"splits": [], "dividends": []}

    def get_company_fundamentals(self, symbol: str, exchange: str = "NSE") -> dict:
        import yfinance as yf
        provider_symbol = self.resolve_provider_symbol(symbol, exchange)
        try:
            ticker = yf.Ticker(provider_symbol)
            info = ticker.info or {}
            return {
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield"),
                "debt_to_equity": info.get("debtToEquity"),
                "return_on_equity": info.get("returnOnEquity"),
                "operating_margins": info.get("operatingMargins"),
                "profit_margins": info.get("profitMargins"),
                "free_cash_flow": info.get("freeCashflow"),
                "revenue": info.get("totalRevenue"),
                "net_income": info.get("netIncomeToCommon"),
                "eps": info.get("trailingEps"),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow")
            }
        except Exception as e:
            logger.warning(f"Could not retrieve live fundamentals for {provider_symbol}: {e}")
            return {}
