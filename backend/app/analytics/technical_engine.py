from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from app.schemas.market_data import MarketBarSchema

class TechnicalEngine:
    """
    Deterministic Technical Analysis Engine.
    Computes moving averages, oscillators, volatility bands, directional movement,
    VWAP, and support/resistance pivot levels using NumPy and pandas.
    """

    @classmethod
    def calculate_full_technical_suite(cls, bars: List[MarketBarSchema]) -> Dict[str, Any]:
        """
        Executes comprehensive multi-indicator technical calculation across historical candles.
        """
        if not bars or len(bars) < 15:
            latest_c = bars[-1].close if bars else 0.0
            return {
                "latest_close": latest_c,
                "indicators": {},
                "pivot_levels": {},
                "multi_timeframe": {"short_term": "NEUTRAL", "medium_term": "NEUTRAL", "long_term": "NEUTRAL", "alignment": "INCONCLUSIVE"},
                "technical_score": 5.0,
                "summary": "Insufficient historical candles for comprehensive technical analysis."
            }

        df = pd.DataFrame([b.model_dump() if hasattr(b, "model_dump") else b.dict() for b in bars])
        df = df.sort_values("timestamp").reset_index(drop=True)
        close = df["close"]
        high = df["high"]
        low = df["low"]
        vol = df["volume"]

        # 1. SMAs (20, 50, 200)
        df["sma_20"] = close.rolling(window=20).mean()
        df["sma_50"] = close.rolling(window=50).mean() if len(df) >= 50 else None
        df["sma_200"] = close.rolling(window=200).mean() if len(df) >= 200 else None

        # 2. EMAs (9, 21, 50, 200)
        df["ema_9"] = close.ewm(span=9, adjust=False).mean()
        df["ema_21"] = close.ewm(span=21, adjust=False).mean()
        df["ema_50"] = close.ewm(span=50, adjust=False).mean() if len(df) >= 50 else None
        df["ema_200"] = close.ewm(span=200, adjust=False).mean() if len(df) >= 200 else None

        # 3. RSI (14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100.0 - (100.0 / (1.0 + rs))
        df["rsi_14"] = rsi.fillna(pd.Series(np.where(loss == 0, 100.0, np.where(gain == 0, 0.0, 50.0)), index=df.index))

        # 4. MACD (12, 26, 9)
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        df["macd_line"] = ema_12 - ema_26
        df["macd_signal"] = df["macd_line"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd_line"] - df["macd_signal"]

        # 5. Bollinger Bands (20, 2 std)
        bb_middle = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        df["bb_upper"] = bb_middle + (2.0 * bb_std)
        df["bb_middle"] = bb_middle
        df["bb_lower"] = bb_middle - (2.0 * bb_std)
        df["bb_bandwidth"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"] * 100.0
        df["bb_pct_b"] = (close - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"]).replace(0, np.nan)

        # 6. ATR (14)
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df["atr_14"] = tr.rolling(window=14).mean()

        # 7. ADX (14)
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        atr_adx = tr.rolling(window=14).mean().replace(0, np.nan)
        plus_di = 100.0 * (pd.Series(plus_dm, index=df.index).rolling(window=14).mean() / atr_adx)
        minus_di = 100.0 * (pd.Series(minus_dm, index=df.index).rolling(window=14).mean() / atr_adx)
        dx = 100.0 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan))
        df["adx_14"] = dx.rolling(window=14).mean()
        df["plus_di"] = plus_di
        df["minus_di"] = minus_di

        # 8. VWAP (Cumulative Volume-Weighted Average Price)
        typical_price = (high + low + close) / 3.0
        cum_vol = vol.cumsum().replace(0, np.nan)
        cum_vp = (typical_price * vol).cumsum()
        df["vwap"] = cum_vp / cum_vol

        # 9. Support & Resistance (Standard Classical Pivot Points)
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2] if len(df) > 1 else last_row

        p_high = float(prev_row["high"])
        p_low = float(prev_row["low"])
        p_close = float(prev_row["close"])

        pivot_point = (p_high + p_low + p_close) / 3.0
        r1 = (2.0 * pivot_point) - p_low
        s1 = (2.0 * pivot_point) - p_high
        r2 = pivot_point + (p_high - p_low)
        s2 = pivot_point - (p_high - p_low)
        r3 = p_high + 2.0 * (pivot_point - p_low)
        s3 = p_low - 2.0 * (p_high - pivot_point)

        swing_high_20 = float(high.tail(20).max())
        swing_low_20 = float(low.tail(20).min())

        pivot_levels = {
            "pivot": round(pivot_point, 2),
            "r1": round(r1, 2),
            "r2": round(r2, 2),
            "r3": round(r3, 2),
            "s1": round(s1, 2),
            "s2": round(s2, 2),
            "s3": round(s3, 2),
            "swing_high_20": round(swing_high_20, 2),
            "swing_low_20": round(swing_low_20, 2)
        }

        # 10. Multi-Timeframe Alignment
        c_val = float(last_row["close"])
        ema9 = float(last_row["ema_9"])
        ema21 = float(last_row["ema_21"])
        sma20 = float(last_row["sma_20"]) if pd.notnull(last_row.get("sma_20")) else None
        sma50 = float(last_row["sma_50"]) if pd.notnull(last_row.get("sma_50")) else None
        sma200 = float(last_row["sma_200"]) if pd.notnull(last_row.get("sma_200")) else None

        # Short-term (EMA 9 vs EMA 21)
        short_trend = "BULLISH" if ema9 > ema21 else "BEARISH"
        # Medium-term (SMA 20 vs SMA 50)
        medium_trend = "BULLISH" if (sma20 and sma50 and sma20 > sma50) else ("BEARISH" if (sma20 and sma50 and sma20 < sma50) else "NEUTRAL")
        # Long-term (Price vs SMA 200 or SMA 50)
        ref_long = sma200 or sma50
        long_trend = "BULLISH" if (ref_long and c_val > ref_long) else ("BEARISH" if (ref_long and c_val < ref_long) else "NEUTRAL")

        # Alignment
        bull_count = [short_trend, medium_trend, long_trend].count("BULLISH")
        bear_count = [short_trend, medium_trend, long_trend].count("BEARISH")
        if bull_count >= 2:
            alignment = "STRONG_BULLISH" if bull_count == 3 else "MODERATE_BULLISH"
        elif bear_count >= 2:
            alignment = "STRONG_BEARISH" if bear_count == 3 else "MODERATE_BEARISH"
        else:
            alignment = "NEUTRAL"

        # Technical Score (0 to 10)
        tech_score = 5.0
        rsi_val = float(last_row["rsi_14"]) if pd.notnull(last_row.get("rsi_14")) else 50.0
        if 40 <= rsi_val <= 65:
            tech_score += 1.0
        elif rsi_val > 70:
            tech_score -= 1.0  # Overbought
        elif rsi_val < 30:
            tech_score += 0.5  # Oversold bounce potential

        macd_hist = float(last_row["macd_hist"]) if pd.notnull(last_row.get("macd_hist")) else 0.0
        if macd_hist > 0:
            tech_score += 1.5
        else:
            tech_score -= 1.0

        if alignment in ("STRONG_BULLISH", "MODERATE_BULLISH"):
            tech_score += 1.5
        elif alignment in ("STRONG_BEARISH", "MODERATE_BEARISH"):
            tech_score -= 1.5

        tech_score = max(1.0, min(10.0, round(tech_score, 1)))

        indicators_summary = {
            "latest_close": round(c_val, 2),
            "sma_20": round(sma20, 2) if sma20 else None,
            "sma_50": round(sma50, 2) if sma50 else None,
            "sma_200": round(sma200, 2) if sma200 else None,
            "ema_9": round(ema9, 2),
            "ema_21": round(ema21, 2),
            "ema_50": round(float(last_row["ema_50"]), 2) if pd.notnull(last_row.get("ema_50")) else None,
            "rsi_14": round(rsi_val, 2),
            "macd_line": round(float(last_row["macd_line"]), 2),
            "macd_signal": round(float(last_row["macd_signal"]), 2),
            "macd_histogram": round(macd_hist, 2),
            "bb_upper": round(float(last_row["bb_upper"]), 2) if pd.notnull(last_row.get("bb_upper")) else None,
            "bb_middle": round(float(last_row["bb_middle"]), 2) if pd.notnull(last_row.get("bb_middle")) else None,
            "bb_lower": round(float(last_row["bb_lower"]), 2) if pd.notnull(last_row.get("bb_lower")) else None,
            "bb_bandwidth": round(float(last_row["bb_bandwidth"]), 2) if pd.notnull(last_row.get("bb_bandwidth")) else None,
            "atr_14": round(float(last_row["atr_14"]), 2) if pd.notnull(last_row.get("atr_14")) else None,
            "adx_14": round(float(last_row["adx_14"]), 2) if pd.notnull(last_row.get("adx_14")) else None,
            "vwap": round(float(last_row["vwap"]), 2) if pd.notnull(last_row.get("vwap")) else None
        }

        summary = (
            f"Technical analysis indicates an overall {alignment.replace('_', ' ')} posture with a score of {tech_score}/10. "
            f"RSI(14) is {round(rsi_val, 1)}, MACD histogram is {round(macd_hist, 2)}. "
            f"Nearest key resistance is R1 at ₹{round(r1, 2)} (Swing high: ₹{round(swing_high_20, 2)}), "
            f"and primary support is S1 at ₹{round(s1, 2)} (Swing low: ₹{round(swing_low_20, 2)})."
        )

        return {
            "latest_close": round(c_val, 2),
            "indicators": indicators_summary,
            "pivot_levels": pivot_levels,
            "multi_timeframe": {
                "short_term": short_trend,
                "medium_term": medium_trend,
                "long_term": long_trend,
                "alignment": alignment
            },
            "technical_score": tech_score,
            "summary": summary
        }
