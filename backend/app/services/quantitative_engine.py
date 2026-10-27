from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime
from app.schemas.market_data import MarketBarSchema
from app.schemas.experiment import ExperimentMetricResponse

class QuantitativeEngine:
    """
    Deterministic quantitative analysis and strategy backtesting engine.
    Calculates technical indicators, risk ratios, and backtest results using pure Python,
    NumPy, and pandas — strictly isolated from LLM probabilistic operations.
    """
    ENGINE_VERSION = "1.0.0"

    @staticmethod
    def calculate_technical_indicators(bars: List[MarketBarSchema]) -> Dict[str, Any]:
        """Calculates standard technical indicators for a given OHLCV series."""
        if not bars or len(bars) < 20:
            return {
                "sma_20": None,
                "sma_50": None,
                "rsi_14": None,
                "macd": None,
                "macd_signal": None,
                "annualized_volatility": None,
                "latest_close": bars[-1].close if bars else None
            }

        df = pd.DataFrame([b.model_dump() if hasattr(b, "model_dump") else b.dict() for b in bars])
        df = df.sort_values("timestamp").reset_index(drop=True)
        close = df["close"]

        # SMAs
        df["sma_20"] = close.rolling(window=20).mean()
        df["sma_50"] = close.rolling(window=50).mean() if len(df) >= 50 else None

        # RSI (14)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi_series = 100.0 - (100.0 / (1.0 + rs))
        # Handle boundary cases: zero loss -> 100.0, zero gain -> 0.0
        rsi_series = rsi_series.fillna(pd.Series(np.where(loss == 0, 100.0, np.where(gain == 0, 0.0, 50.0)), index=df.index))
        df["rsi_14"] = rsi_series

        # MACD (12, 26, 9)
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        df["macd"] = ema_12 - ema_26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        # Volatility (annualized, 252 days)
        log_ret = np.log(close / close.shift(1))
        ann_vol = float(log_ret.std() * np.sqrt(252)) if len(log_ret.dropna()) > 10 else 0.0

        latest = df.iloc[-1]
        return {
            "latest_close": round(float(latest["close"]), 2),
            "sma_20": round(float(latest["sma_20"]), 2) if pd.notnull(latest.get("sma_20")) else None,
            "sma_50": round(float(latest["sma_50"]), 2) if pd.notnull(latest.get("sma_50")) else None,
            "rsi_14": round(float(latest["rsi_14"]), 2) if pd.notnull(latest.get("rsi_14")) else None,
            "macd": round(float(latest["macd"]), 2) if pd.notnull(latest.get("macd")) else None,
            "macd_signal": round(float(latest["macd_signal"]), 2) if pd.notnull(latest.get("macd_signal")) else None,
            "annualized_volatility": round(ann_vol, 4)
        }

    @classmethod
    def run_sma_crossover_backtest(
        cls,
        bars: List[MarketBarSchema],
        fast_period: int = 20,
        slow_period: int = 50,
        initial_capital: float = 100000.0,
        fee_pct: float = 0.001,      # 0.1% per transaction
        slippage_pct: float = 0.0005, # 0.05% slippage
        benchmark_bars: Optional[List[MarketBarSchema]] = None,
        train_split: float = 0.7
    ) -> ExperimentMetricResponse:
        """
        Executes a deterministic moving average crossover backtest.
        LOOK-AHEAD BIAS PREVENTION:
        - Signals are generated at close of bar t based strictly on information up to t.
        - Execution occurs at Open of bar t+1.
        - Slippage and transaction costs are applied to execution price.
        """
        if len(bars) <= slow_period + 5:
            raise ValueError(f"Insufficient historical data: {len(bars)} bars. Minimum required: {slow_period + 5}")

        df = pd.DataFrame([b.model_dump() if hasattr(b, 'model_dump') else b.dict() for b in bars]).sort_values("timestamp").reset_index(drop=True)
        df["fast_ma"] = df["close"].rolling(window=fast_period).mean()
        df["slow_ma"] = df["close"].rolling(window=slow_period).mean()

        # Signal generated at close of bar: 1 if fast > slow else 0
        df["signal"] = 0
        df.loc[df["fast_ma"] > df["slow_ma"], "signal"] = 1
        
        # Position change happens on NEXT bar: shift(1)
        df["target_position"] = df["signal"].shift(1).fillna(0)

        # Event-driven execution loop
        capital = initial_capital
        position_shares = 0
        trades = []
        equity_curve = []
        in_trade = False
        entry_price = 0.0
        entry_date = None

        for i in range(len(df)):
            row = df.iloc[i]
            target_pos = row["target_position"]
            open_p = row["open"]
            close_p = row["close"]
            dt_str = row["timestamp"].strftime("%Y-%m-%d")

            # Check if order execution is triggered at bar Open
            if target_pos == 1 and not in_trade:
                # BUY execution
                exec_price = open_p * (1.0 + slippage_pct)
                fee = (capital * fee_pct)
                investable = capital - fee
                position_shares = investable / exec_price
                capital = 0.0
                in_trade = True
                entry_price = exec_price
                entry_date = dt_str

            elif target_pos == 0 and in_trade:
                # SELL execution
                exec_price = open_p * (1.0 - slippage_pct)
                proceeds = position_shares * exec_price
                fee = proceeds * fee_pct
                capital = proceeds - fee
                pnl = capital - initial_capital
                pnl_pct = (exec_price - entry_price) / entry_price
                trades.append({
                    "entry_date": entry_date,
                    "exit_date": dt_str,
                    "entry_price": round(entry_price, 2),
                    "exit_price": round(exec_price, 2),
                    "shares": round(position_shares, 2),
                    "pnl": round(proceeds - fee - (position_shares * entry_price), 2),
                    "return_pct": round(pnl_pct * 100, 2)
                })
                position_shares = 0
                in_trade = False

            # Mark to Market Portfolio Value at bar Close
            current_portfolio_value = capital + (position_shares * close_p)
            equity_curve.append({
                "date": dt_str,
                "portfolio_value": round(current_portfolio_value, 2),
                "close_price": round(close_p, 2)
            })

        # Calculate performance metrics
        eq_series = pd.Series([e["portfolio_value"] for e in equity_curve])
        daily_returns = eq_series.pct_change().dropna()

        total_days = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).days
        years = max(total_days / 365.25, 0.2)
        end_val = eq_series.iloc[-1]
        cagr = (end_val / initial_capital) ** (1.0 / years) - 1.0

        # Max Drawdown
        cum_max = eq_series.cummax()
        drawdowns = (eq_series - cum_max) / cum_max
        max_dd = abs(float(drawdowns.min()))

        # Sharpe & Sortino (assuming 6% annual risk-free rate)
        rf_daily = 0.06 / 252
        excess_returns = daily_returns - rf_daily
        ann_std = daily_returns.std() * np.sqrt(252)
        sharpe = float((excess_returns.mean() * 252) / (ann_std + 1e-9)) if ann_std > 0 else 0.0

        downside_returns = daily_returns[daily_returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        sortino = float((excess_returns.mean() * 252) / (downside_std + 1e-9)) if downside_std > 0 else 0.0

        # Win rate & Profit factor
        winning_trades = [t for t in trades if t["return_pct"] > 0]
        losing_trades = [t for t in trades if t["return_pct"] <= 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0.0

        total_gain = sum(t["pnl"] for t in winning_trades)
        total_loss = abs(sum(t["pnl"] for t in losing_trades))
        profit_factor = round(total_gain / (total_loss + 1e-9), 2) if total_loss > 0 else (1.0 if not trades else 10.0)

        # Benchmark comparison
        benchmark_cagr = None
        benchmark_max_dd = None
        if benchmark_bars and len(benchmark_bars) > 10:
            b_df = pd.DataFrame([b.model_dump() if hasattr(b, 'model_dump') else b.dict() for b in benchmark_bars]).sort_values("timestamp")
            b_start = b_df["close"].iloc[0]
            b_end = b_df["close"].iloc[-1]
            benchmark_cagr = round(((b_end / b_start) ** (1.0 / years) - 1.0) * 100, 2)
            b_cum_max = b_df["close"].cummax()
            b_dd = (b_df["close"] - b_cum_max) / b_cum_max
            benchmark_max_dd = round(abs(float(b_dd.min())) * 100, 2)

        return ExperimentMetricResponse(
            cagr=round(cagr * 100, 2),
            sharpe_ratio=round(sharpe, 2),
            sortino_ratio=round(sortino, 2),
            max_drawdown=round(max_dd * 100, 2),
            calmar_ratio=round(abs(cagr / (max_dd + 1e-9)), 2),
            annualized_volatility=round(ann_std * 100, 2),
            win_rate=round(win_rate * 100, 2),
            profit_factor=profit_factor,
            total_trades=len(trades),
            benchmark_cagr=benchmark_cagr,
            benchmark_max_drawdown=benchmark_max_dd,
            equity_curve=equity_curve,
            trades=trades
        )
