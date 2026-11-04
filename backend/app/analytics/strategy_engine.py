from typing import Dict, Any, List, Optional, Tuple, Type
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from datetime import datetime
from app.schemas.market_data import MarketBarSchema
from app.schemas.experiment import ExperimentMetricResponse
from app.schemas.strategy import StrategyDefinitionSchema, StrategySignal, StrategyConsensusResult

class BaseStrategy(ABC):
    """
    Abstract base class for all deterministic quantitative strategies.
    Ensures strict next-bar execution, transaction cost accounting, and bias prevention.
    """
    KEY: str = "base"
    NAME: str = "Base Strategy"
    CATEGORY: str = "technical"  # technical, fundamental, momentum, risk
    DESCRIPTION: str = ""
    VERSION: str = "1.0.0"
    DEFAULT_PARAMETERS: Dict[str, Any] = {}

    @abstractmethod
    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        """
        Generates target position series: 1.0 (invested) or 0.0 (cash).
        Must be based strictly on information available at or before close of bar t.
        """
        pass

    @classmethod
    def get_definition(cls) -> StrategyDefinitionSchema:
        return StrategyDefinitionSchema(
            id=cls.KEY,
            strategy_key=cls.KEY,
            name=cls.NAME,
            category=cls.CATEGORY,
            description=cls.DESCRIPTION,
            default_parameters=cls.DEFAULT_PARAMETERS,
            supported_timeframes=["1D"],
            version=cls.VERSION,
            is_active=True
        )

    @classmethod
    def backtest(
        cls,
        bars: List[MarketBarSchema],
        parameters: Optional[Dict[str, Any]] = None,
        initial_capital: float = 100000.0,
        fee_pct: float = 0.001,       # 0.1% per trade
        slippage_pct: float = 0.0005,  # 0.05% slippage
        benchmark_bars: Optional[List[MarketBarSchema]] = None,
        train_split: float = 0.7
    ) -> ExperimentMetricResponse:
        """
        Executes a deterministic historical replay backtest with train/test separation.
        Execution occurs on the NEXT bar's Open price:
        Execution Price = Open_{t+1} * (1 + slippage) for BUY, Open_{t+1} * (1 - slippage) for SELL.
        """
        if not bars or len(bars) < 30:
            raise ValueError(f"Insufficient historical data ({len(bars)} bars) for strategy {cls.KEY}")

        params = cls.DEFAULT_PARAMETERS.copy()
        if parameters:
            params.update(parameters)

        strategy_inst = cls()
        df = pd.DataFrame([b.model_dump() if hasattr(b, "model_dump") else b.dict() for b in bars])
        df = df.sort_values("timestamp").reset_index(drop=True)

        # 1. Compute target position from strategy rules (0.0 or 1.0)
        target_pos = strategy_inst.generate_positions(df, params)
        # Shift target positions by 1 bar to guarantee next-bar open execution (prevents look-ahead bias)
        exec_pos = target_pos.shift(1).fillna(0.0)

        # 2. Simulate portfolio cash, positions, and trades
        cash = float(initial_capital)
        shares = 0.0
        equity_curve = []
        trades = []
        trade_returns = []
        last_buy_price = 0.0
        last_buy_date = ""

        for i in range(len(df)):
            row = df.iloc[i]
            open_price = float(row["open"])
            close_price = float(row["close"])
            ts_str = str(row["timestamp"])
            desired = float(exec_pos.iloc[i])

            # Transition from Cash to Long (BUY)
            if desired > 0.0 and shares == 0.0:
                cost_per_share = open_price * (1.0 + slippage_pct)
                investable = cash * 0.999  # reserve small buffer for fees
                buy_shares = np.floor(investable / cost_per_share)
                if buy_shares > 0:
                    fee = buy_shares * cost_per_share * fee_pct
                    total_outlay = (buy_shares * cost_per_share) + fee
                    cash -= total_outlay
                    shares = buy_shares
                    last_buy_price = cost_per_share
                    last_buy_date = ts_str

            # Transition from Long to Cash (SELL)
            elif desired == 0.0 and shares > 0.0:
                sale_price = open_price * (1.0 - slippage_pct)
                gross_proceeds = shares * sale_price
                fee = gross_proceeds * fee_pct
                net_proceeds = gross_proceeds - fee
                cash += net_proceeds
                ret_pct = ((sale_price - last_buy_price) / max(last_buy_price, 0.01)) * 100.0
                trade_pnl = net_proceeds - (shares * last_buy_price)
                trade_returns.append(ret_pct)
                trades.append({
                    "entry_date": last_buy_date[:10] if last_buy_date else ts_str[:10],
                    "exit_date": ts_str[:10],
                    "entry_price": round(last_buy_price, 2),
                    "exit_price": round(sale_price, 2),
                    "shares": round(shares, 1),
                    "pnl": round(trade_pnl, 2),
                    "return_pct": round(ret_pct, 2),
                    "timestamp": ts_str,
                    "action": "SELL",
                    "price": round(sale_price, 2),
                    "fee": round(fee, 2),
                    "reason": f"{cls.NAME} Exit Rule"
                })
                shares = 0.0

            # Mark to market equity
            total_equity = cash + (shares * close_price)
            equity_curve.append({
                "date": ts_str[:10] if len(ts_str) >= 10 else ts_str,
                "timestamp": ts_str,
                "portfolio_value": round(total_equity, 2),
                "equity": round(total_equity, 2),
                "close_price": round(close_price, 2),
                "close": round(close_price, 2)
            })

        # 3. Calculate deterministic performance metrics
        eq_series = pd.Series([e["equity"] for e in equity_curve])
        returns = eq_series.pct_change().dropna()

        # Cumulative CAGR
        total_days = max(1, (df.iloc[-1]["timestamp"] - df.iloc[0]["timestamp"]).days) if hasattr(df.iloc[-1]["timestamp"], "days") else len(df)
        years = max(total_days / 365.25, 0.1)
        final_equity = float(eq_series.iloc[-1])
        total_return_pct = ((final_equity - initial_capital) / initial_capital) * 100.0
        cagr = (float(final_equity / initial_capital) ** (1.0 / years)) - 1.0 if final_equity > 0 else -1.0

        # Annualized Volatility (252 trading days)
        ann_vol = float(returns.std() * np.sqrt(252)) if len(returns) > 5 else 0.0

        # Sharpe Ratio (assumes 6.5% risk-free rate for Indian G-Secs)
        rf_daily = 0.065 / 252.0
        excess_daily_returns = returns - rf_daily
        sharpe = float(np.sqrt(252) * (excess_daily_returns.mean() / excess_daily_returns.std())) if excess_daily_returns.std() > 0 else 0.0

        # Sortino Ratio (downside deviation only)
        downside = returns[returns < 0]
        downside_std = float(downside.std() * np.sqrt(252)) if len(downside) > 2 else ann_vol
        sortino = float((cagr - 0.065) / downside_std) if downside_std > 0 else 0.0

        # Max Drawdown
        cum_max = eq_series.cummax()
        drawdown = (eq_series - cum_max) / cum_max
        max_dd = float(abs(drawdown.min())) if len(drawdown) > 0 else 0.0

        # Calmar Ratio
        calmar = round(float(cagr / max_dd), 2) if max_dd > 0 else 0.0

        # Trade metrics
        total_trades = len(trade_returns)
        winning_trades = [r for r in trade_returns if r > 0]
        win_rate = float(len(winning_trades) / total_trades) if total_trades > 0 else 0.0
        gross_profit = sum(winning_trades)
        gross_loss = abs(sum([r for r in trade_returns if r < 0]))
        profit_factor = round(float(gross_profit / gross_loss), 2) if gross_loss > 0 else (round(gross_profit, 2) if gross_profit > 0 else 1.0)

        # Benchmark CAGR
        bench_cagr = None
        bench_dd = None
        if benchmark_bars and len(benchmark_bars) >= 20:
            b_df = pd.DataFrame([b.model_dump() if hasattr(b, "model_dump") else b.dict() for b in benchmark_bars])
            b_df = b_df.sort_values("timestamp").reset_index(drop=True)
            b_first = float(b_df.iloc[0]["close"])
            b_last = float(b_df.iloc[-1]["close"])
            bench_cagr = round(float((b_last / b_first) ** (1.0 / years) - 1.0), 4)
            b_cum_max = b_df["close"].cummax()
            b_dd = (b_df["close"] - b_cum_max) / b_cum_max
            bench_dd = round(float(abs(b_dd.min())), 4)

        # Train / Test out-of-sample partition
        split_idx = int(len(df) * train_split)
        oos_equity = eq_series.iloc[split_idx:]
        oos_cagr = None
        oos_sharpe = None
        if len(oos_equity) > 10:
            oos_ret = oos_equity.pct_change().dropna()
            oos_years = max((len(oos_equity) / 252.0), 0.1)
            oos_cagr = round(float((oos_equity.iloc[-1] / oos_equity.iloc[0]) ** (1.0 / oos_years) - 1.0), 4)
            oos_std = float(oos_ret.std() * np.sqrt(252))
            oos_sharpe = round(float((oos_ret.mean() * np.sqrt(252)) / oos_std), 2) if oos_std > 0 else 0.0

        out_of_sample = {
            "in_sample_bars": split_idx,
            "out_of_sample_bars": len(df) - split_idx,
            "out_of_sample_cagr": oos_cagr,
            "out_of_sample_sharpe": oos_sharpe
        }

        # Alpha over benchmark
        benchmark_alpha = round(float(cagr - (bench_cagr or 0.12)), 4)

        return ExperimentMetricResponse(
            cagr=round(float(cagr), 4),
            sharpe_ratio=round(float(sharpe), 2),
            sortino_ratio=round(float(sortino), 2),
            max_drawdown=round(float(max_dd), 4),
            calmar_ratio=calmar,
            annualized_volatility=round(float(ann_vol), 4),
            win_rate=round(float(win_rate), 4),
            profit_factor=profit_factor,
            total_trades=total_trades,
            benchmark_cagr=bench_cagr,
            benchmark_max_drawdown=bench_dd,
            out_of_sample_metrics=out_of_sample,
            equity_curve=equity_curve[::max(1, len(equity_curve) // 100)],
            trades=trades
        )


# =====================================================================
# 10 Concrete Strategy Implementations
# =====================================================================

class SMACrossoverStrategy(BaseStrategy):
    KEY = "sma_crossover"
    NAME = "SMA Golden / Death Cross"
    CATEGORY = "technical"
    DESCRIPTION = "Enters long when Fast SMA crosses above Slow SMA; exits on downward cross."
    DEFAULT_PARAMETERS = {"fast_period": 20, "slow_period": 50}

    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        fast_p = int(params.get("fast_period", 20))
        slow_p = int(params.get("slow_period", 50))
        close = df["close"]
        sma_fast = close.rolling(window=fast_p).mean()
        sma_slow = close.rolling(window=slow_p).mean()
        pos = (sma_fast > sma_slow).astype(float)
        return pos.fillna(0.0)


class EMACrossoverStrategy(BaseStrategy):
    KEY = "ema_crossover"
    NAME = "EMA Fast / Slow Ribbon"
    CATEGORY = "technical"
    DESCRIPTION = "Captures rapid trend initiation using 9 EMA crossing above 21 EMA."
    DEFAULT_PARAMETERS = {"fast_period": 9, "slow_period": 21}

    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        fast_p = int(params.get("fast_period", 9))
        slow_p = int(params.get("slow_period", 21))
        close = df["close"]
        ema_fast = close.ewm(span=fast_p, adjust=False).mean()
        ema_slow = close.ewm(span=slow_p, adjust=False).mean()
        pos = (ema_fast > ema_slow).astype(float)
        return pos.fillna(0.0)


class RSIThresholdStrategy(BaseStrategy):
    KEY = "rsi_threshold"
    NAME = "RSI Oversold / Overbought"
    CATEGORY = "technical"
    DESCRIPTION = "Buys when RSI dips into oversold territory (<35); exits when RSI exceeds overbought (>65)."
    DEFAULT_PARAMETERS = {"period": 14, "oversold": 35, "overbought": 65}

    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        period = int(params.get("period", 14))
        oversold = float(params.get("oversold", 35))
        overbought = float(params.get("overbought", 65))
        close = df["close"]
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100.0 - (100.0 / (1.0 + rs))

        pos = pd.Series(0.0, index=df.index)
        is_in = False
        for i in range(len(df)):
            r = rsi.iloc[i]
            if not is_in and pd.notnull(r) and r <= oversold:
                is_in = True
            elif is_in and pd.notnull(r) and r >= overbought:
                is_in = False
            pos.iloc[i] = 1.0 if is_in else 0.0
        return pos


class MACDMomentumStrategy(BaseStrategy):
    KEY = "macd_momentum"
    NAME = "MACD Histogram Momentum"
    CATEGORY = "momentum"
    DESCRIPTION = "Trades when MACD line crosses above Signal line and histogram turns positive."
    DEFAULT_PARAMETERS = {"fast": 12, "slow": 26, "signal": 9}

    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        f = int(params.get("fast", 12))
        s = int(params.get("slow", 26))
        sig = int(params.get("signal", 9))
        close = df["close"]
        macd = close.ewm(span=f, adjust=False).mean() - close.ewm(span=s, adjust=False).mean()
        signal = macd.ewm(span=sig, adjust=False).mean()
        pos = (macd > signal).astype(float)
        return pos.fillna(0.0)


class BollingerBandsStrategy(BaseStrategy):
    KEY = "bollinger_bands"
    NAME = "Bollinger Band Mean Reversion"
    CATEGORY = "technical"
    DESCRIPTION = "Buys when price touches or pierces Lower Bollinger Band; exits at Upper Band."
    DEFAULT_PARAMETERS = {"period": 20, "std_dev": 2.0}

    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        period = int(params.get("period", 20))
        num_std = float(params.get("std_dev", 2.0))
        close = df["close"]
        mid = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        lower = mid - (num_std * std)
        upper = mid + (num_std * std)

        pos = pd.Series(0.0, index=df.index)
        is_in = False
        for i in range(len(df)):
            c = close.iloc[i]
            low_b = lower.iloc[i]
            up_b = upper.iloc[i]
            if not is_in and pd.notnull(low_b) and c <= low_b:
                is_in = True
            elif is_in and pd.notnull(up_b) and c >= up_b:
                is_in = False
            pos.iloc[i] = 1.0 if is_in else 0.0
        return pos


class MeanReversionStrategy(BaseStrategy):
    KEY = "mean_reversion"
    NAME = "Statistical Z-Score Mean Reversion"
    CATEGORY = "technical"
    DESCRIPTION = "Enters long when price Z-Score drops below -1.75; exits when Z-Score reverts above 0.5."
    DEFAULT_PARAMETERS = {"period": 20, "entry_z": -1.75, "exit_z": 0.5}

    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        p = int(params.get("period", 20))
        e_z = float(params.get("entry_z", -1.75))
        x_z = float(params.get("exit_z", 0.5))
        close = df["close"]
        mean = close.rolling(window=p).mean()
        std = close.rolling(window=p).std().replace(0, np.nan)
        z_score = (close - mean) / std

        pos = pd.Series(0.0, index=df.index)
        is_in = False
        for i in range(len(df)):
            z = z_score.iloc[i]
            if not is_in and pd.notnull(z) and z <= e_z:
                is_in = True
            elif is_in and pd.notnull(z) and z >= x_z:
                is_in = False
            pos.iloc[i] = 1.0 if is_in else 0.0
        return pos


class MomentumBreakoutStrategy(BaseStrategy):
    KEY = "momentum_breakout"
    NAME = "Donchian 20-Day High Breakout"
    CATEGORY = "momentum"
    DESCRIPTION = "Buys on a new 20-day high with trailing 10-day low stop."
    DEFAULT_PARAMETERS = {"lookback_high": 20, "lookback_low": 10}

    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        lb_h = int(params.get("lookback_high", 20))
        lb_l = int(params.get("lookback_low", 10))
        high = df["high"]
        low = df["low"]
        close = df["close"]
        highest_high = high.shift(1).rolling(window=lb_h).max()
        lowest_low = low.shift(1).rolling(window=lb_l).min()

        pos = pd.Series(0.0, index=df.index)
        is_in = False
        for i in range(len(df)):
            c = close.iloc[i]
            hh = highest_high.iloc[i]
            ll = lowest_low.iloc[i]
            if not is_in and pd.notnull(hh) and c > hh:
                is_in = True
            elif is_in and pd.notnull(ll) and c < ll:
                is_in = False
            pos.iloc[i] = 1.0 if is_in else 0.0
        return pos


class VolumeBreakoutStrategy(BaseStrategy):
    KEY = "volume_breakout"
    NAME = "Volume Supported Breakout"
    CATEGORY = "momentum"
    DESCRIPTION = "Buys when volume is 1.8x 20-day average and price breaks above 20-day resistance."
    DEFAULT_PARAMETERS = {"vol_mult": 1.8, "period": 20}

    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        mult = float(params.get("vol_mult", 1.8))
        period = int(params.get("period", 20))
        close = df["close"]
        vol = df["volume"]
        avg_vol = vol.rolling(window=period).mean()
        high_20 = close.shift(1).rolling(window=period).max()

        breakout = (vol > (avg_vol * mult)) & (close > high_20)
        sma_20 = close.rolling(window=period).mean()

        pos = pd.Series(0.0, index=df.index)
        is_in = False
        for i in range(len(df)):
            b = breakout.iloc[i]
            s = sma_20.iloc[i]
            c = close.iloc[i]
            if not is_in and b:
                is_in = True
            elif is_in and pd.notnull(s) and c < s:
                is_in = False
            pos.iloc[i] = 1.0 if is_in else 0.0
        return pos


class FundamentalValueStrategy(BaseStrategy):
    KEY = "fundamental_value"
    NAME = "Fundamental Value & Trend Alignment"
    CATEGORY = "fundamental"
    DESCRIPTION = "Enters when medium-term trend is positive (Price > SMA50) and recent momentum is non-deteriorating."
    DEFAULT_PARAMETERS = {"trend_sma": 50, "rsi_min": 40}

    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        trend_p = int(params.get("trend_sma", 50))
        rsi_min = float(params.get("rsi_min", 40))
        close = df["close"]
        sma = close.rolling(window=trend_p).mean()

        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100.0 - (100.0 / (1.0 + rs))

        pos = ((close > sma) & (rsi >= rsi_min)).astype(float)
        return pos.fillna(0.0)


class RiskParityStrategy(BaseStrategy):
    KEY = "risk_parity"
    NAME = "Volatility Risk-Managed Trend"
    CATEGORY = "risk"
    DESCRIPTION = "Stops out or scales down positions when 14-day ATR annualized volatility spikes above 30%."
    DEFAULT_PARAMETERS = {"max_volatility": 0.35, "trend_period": 20}

    def generate_positions(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        max_vol = float(params.get("max_volatility", 0.35))
        trend_p = int(params.get("trend_period", 20))
        close = df["close"]
        sma = close.rolling(window=trend_p).mean()

        log_ret = np.log(close / close.shift(1))
        rolling_vol = log_ret.rolling(window=20).std() * np.sqrt(252)

        pos = ((close > sma) & (rolling_vol <= max_vol)).astype(float)
        return pos.fillna(0.0)


# =====================================================================
# Strategy Registry & Multi-Strategy Consensus Orchestrator
# =====================================================================

class StrategyRegistry:
    """
    Central repository of registered quantitative strategies.
    Supports individual execution and multi-strategy consensus synthesis.
    """
    _REGISTRY: Dict[str, Type[BaseStrategy]] = {
        SMACrossoverStrategy.KEY: SMACrossoverStrategy,
        EMACrossoverStrategy.KEY: EMACrossoverStrategy,
        RSIThresholdStrategy.KEY: RSIThresholdStrategy,
        MACDMomentumStrategy.KEY: MACDMomentumStrategy,
        BollingerBandsStrategy.KEY: BollingerBandsStrategy,
        MeanReversionStrategy.KEY: MeanReversionStrategy,
        MomentumBreakoutStrategy.KEY: MomentumBreakoutStrategy,
        VolumeBreakoutStrategy.KEY: VolumeBreakoutStrategy,
        FundamentalValueStrategy.KEY: FundamentalValueStrategy,
        RiskParityStrategy.KEY: RiskParityStrategy,
    }

    @classmethod
    def list_strategies(cls) -> List[StrategyDefinitionSchema]:
        return [strat.get_definition() for strat in cls._REGISTRY.values()]

    @classmethod
    def get_strategy(cls, key: str) -> Optional[Type[BaseStrategy]]:
        return cls._REGISTRY.get(key)

    @classmethod
    def run_strategy(
        cls,
        key: str,
        bars: List[MarketBarSchema],
        parameters: Optional[Dict[str, Any]] = None,
        initial_capital: float = 100000.0,
        fee_pct: float = 0.001,
        slippage_pct: float = 0.0005,
        benchmark_bars: Optional[List[MarketBarSchema]] = None
    ) -> ExperimentMetricResponse:
        strat_cls = cls.get_strategy(key)
        if not strat_cls:
            raise ValueError(f"Unknown strategy key: {key}")
        return strat_cls.backtest(
            bars=bars,
            parameters=parameters,
            initial_capital=initial_capital,
            fee_pct=fee_pct,
            slippage_pct=slippage_pct,
            benchmark_bars=benchmark_bars
        )

    @classmethod
    def run_multi_strategy_consensus(
        cls,
        bars: List[MarketBarSchema],
        strategy_keys: Optional[List[str]] = None,
        initial_capital: float = 100000.0,
        benchmark_bars: Optional[List[MarketBarSchema]] = None
    ) -> StrategyConsensusResult:
        """
        Executes an ensemble of strategies across the historical series.
        Determines the current signal of each strategy (from the latest bar)
        and computes the consensus vote.
        """
        if not strategy_keys:
            strategy_keys = list(cls._REGISTRY.keys())

        signals: List[StrategySignal] = []
        buy_count = 0
        hold_count = 0
        sell_count = 0

        for key in strategy_keys:
            strat_cls = cls.get_strategy(key)
            if not strat_cls:
                continue

            try:
                # 1. Backtest strategy
                res = strat_cls.backtest(
                    bars=bars,
                    initial_capital=initial_capital,
                    benchmark_bars=benchmark_bars
                )

                # 2. Determine latest signal
                df = pd.DataFrame([b.model_dump() if hasattr(b, "model_dump") else b.dict() for b in bars])
                df = df.sort_values("timestamp").reset_index(drop=True)
                pos = strat_cls().generate_positions(df, strat_cls.DEFAULT_PARAMETERS)
                latest_pos = float(pos.iloc[-1]) if len(pos) > 0 else 0.0
                prev_pos = float(pos.iloc[-2]) if len(pos) > 1 else latest_pos

                if latest_pos > 0.0 and prev_pos == 0.0:
                    sig_label = "BUY"
                    strength = 0.85
                    buy_count += 1
                elif latest_pos > 0.0 and prev_pos > 0.0:
                    sig_label = "HOLD"
                    strength = 0.65
                    hold_count += 1
                elif latest_pos == 0.0 and prev_pos > 0.0:
                    sig_label = "SELL"
                    strength = 0.80
                    sell_count += 1
                else:
                    sig_label = "NEUTRAL"
                    strength = 0.50
                    hold_count += 1

                signals.append(StrategySignal(
                    strategy_key=key,
                    name=strat_cls.NAME,
                    category=strat_cls.CATEGORY,
                    signal=sig_label,
                    signal_strength=strength,
                    cagr=res.cagr,
                    sharpe_ratio=res.sharpe_ratio,
                    max_drawdown=res.max_drawdown,
                    win_rate=res.win_rate,
                    summary=f"{strat_cls.NAME}: Historical CAGR {round((res.cagr or 0)*100, 1)}%, Sharpe {res.sharpe_ratio}, Max DD {round((res.max_drawdown or 0)*100, 1)}%."
                ))
            except Exception as e:
                continue

        total = len(signals)
        if total == 0:
            return StrategyConsensusResult(
                total_strategies=0,
                buy_signals=0,
                hold_signals=0,
                sell_signals=0,
                consensus_rating="INSUFFICIENT_EVIDENCE",
                consensus_percentage=0.0,
                signals=[]
            )

        # Consensus determination
        if buy_count >= (total * 0.5):
            consensus_rating = "BUY"
            consensus_pct = round((buy_count / total) * 100.0, 1)
        elif sell_count >= (total * 0.4):
            consensus_rating = "SELL"
            consensus_pct = round((sell_count / total) * 100.0, 1)
        elif (buy_count + hold_count) >= (total * 0.6):
            consensus_rating = "HOLD"
            consensus_pct = round(((buy_count + hold_count) / total) * 100.0, 1)
        else:
            consensus_rating = "HOLD"
            consensus_pct = 50.0

        return StrategyConsensusResult(
            total_strategies=total,
            buy_signals=buy_count,
            hold_signals=hold_count,
            sell_signals=sell_count,
            consensus_rating=consensus_rating,
            consensus_percentage=consensus_pct,
            signals=signals
        )
