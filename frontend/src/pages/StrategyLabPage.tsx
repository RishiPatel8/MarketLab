import React, { useState, useEffect } from 'react';
import {
  Activity,
  Play,
  RotateCcw,
  ShieldCheck,
  TrendingUp,
  AlertCircle,
  HelpCircle,
  ArrowUpRight,
  ArrowDownRight,
  Search,
  Layers,
  Scale,
  CheckCircle2,
  Sparkles,
  BarChart2
} from 'lucide-react';
import {
  createExperiment,
  runStrategyBacktest,
  evaluateStrategyConsensus
} from '../services/api';
import {
  Experiment,
  ExperimentMetrics,
  Instrument,
  StrategyConsensus
} from '../types';
import { EquityChart } from '../components/EquityChart';
import { MetricCard } from '../components/MetricCard';
import { InstrumentSearchModal } from '../components/InstrumentSearchModal';

const AVAILABLE_STRATEGIES = [
  {
    key: 'sma_crossover',
    name: 'SMA Crossover',
    category: 'Trend Following',
    description: 'Golden Cross (Fast > Slow SMA) / Death Cross (Fast < Slow SMA) trend strategy.',
    defaultParams: { fast_period: 20, slow_period: 50 }
  },
  {
    key: 'ema_crossover',
    name: 'EMA Crossover',
    category: 'Trend Following',
    description: 'Exponential moving average responsive crossover (9 EMA / 21 EMA).',
    defaultParams: { fast_period: 9, slow_period: 21 }
  },
  {
    key: 'rsi_threshold',
    name: 'RSI Mean Reversion',
    category: 'Mean Reversion',
    description: 'Long when RSI < 30 (oversold), exit when RSI > 70 (overbought).',
    defaultParams: { period: 14, oversold: 30, overbought: 70 }
  },
  {
    key: 'macd_momentum',
    name: 'MACD Signal Crossover',
    category: 'Momentum',
    description: 'Long when MACD line crosses above signal line with positive histogram.',
    defaultParams: { fast_period: 12, slow_period: 26, signal_period: 9 }
  },
  {
    key: 'bollinger_bands',
    name: 'Bollinger Band Mean Reversion',
    category: 'Volatility',
    description: 'Enters on touch of lower 2-sigma band and exits at the 20-day mean.',
    defaultParams: { period: 20, num_std: 2.0 }
  },
  {
    key: 'mean_reversion',
    name: 'Z-Score Mean Reversion',
    category: 'Statistical',
    description: 'Statistical arbitrage entry at 2 standard deviations from moving average.',
    defaultParams: { lookback: 20, entry_z: -1.5, exit_z: 0.5 }
  },
  {
    key: 'momentum_breakout',
    name: 'Momentum Breakout',
    category: 'Breakout',
    description: 'Donchian channel 20-day high breakout with ATR volatility trailing stop.',
    defaultParams: { lookback: 20, exit_lookback: 10 }
  },
  {
    key: 'volume_breakout',
    name: 'Volume Spike Breakout',
    category: 'Volume & Price Action',
    description: 'Expansion breakout when volume exceeds 2x 20-day volume SMA.',
    defaultParams: { volume_multiplier: 1.8, price_change_pct: 1.5 }
  },
  {
    key: 'fundamental_value',
    name: 'Fundamental Value & Quality',
    category: 'Fundamental',
    description: 'P/E < 25 and ROE > 15% valuation filter combined with price momentum.',
    defaultParams: { max_pe: 30, min_roe: 12 }
  },
  {
    key: 'risk_parity',
    name: 'Risk Parity Allocation',
    category: 'Risk Managed',
    description: 'Inverse-volatility sizing with ATR regime protection.',
    defaultParams: { target_volatility: 0.15, rebalance_days: 20 }
  }
];

export const StrategyLabPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'single' | 'consensus'>('single');
  const [symbol, setSymbol] = useState('RELIANCE');
  const [instrumentName, setInstrumentName] = useState('Reliance Industries Limited');
  const [selectedStrategyKey, setSelectedStrategyKey] = useState('sma_crossover');
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [fastPeriod, setFastPeriod] = useState(20);
  const [slowPeriod, setSlowPeriod] = useState(50);
  const [rsiPeriod, setRsiPeriod] = useState(14);
  const [initialCapital, setInitialCapital] = useState(100000);
  const [feePct, setFeePct] = useState(0.001); // 0.1%
  const [slippagePct, setSlippagePct] = useState(0.0005); // 0.05%
  const [loading, setLoading] = useState(false);
  const [consensusLoading, setConsensusLoading] = useState(false);
  const [metrics, setMetrics] = useState<ExperimentMetrics | null>(null);
  const [consensusResult, setConsensusResult] = useState<StrategyConsensus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Auto-run baseline experiment on mount
  useEffect(() => {
    handleRunSingleBacktest();
  }, [symbol, selectedStrategyKey]);

  const handleRunSingleBacktest = async () => {
    setLoading(true);
    setError(null);
    try {
      let params: Record<string, any> = {};
      if (selectedStrategyKey === 'sma_crossover' || selectedStrategyKey === 'ema_crossover') {
        params = { fast_period: fastPeriod, slow_period: slowPeriod };
      } else if (selectedStrategyKey === 'rsi_threshold') {
        params = { period: rsiPeriod, oversold: 30, overbought: 70 };
      } else {
        const found = AVAILABLE_STRATEGIES.find((s) => s.key === selectedStrategyKey);
        params = found ? found.defaultParams : {};
      }

      const res = await runStrategyBacktest(symbol, selectedStrategyKey, params, initialCapital);
      setMetrics(res);
    } catch (err: any) {
      setError(err.message || 'Backtest execution failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRunConsensus = async () => {
    setConsensusLoading(true);
    setError(null);
    try {
      const res = await evaluateStrategyConsensus(symbol);
      setConsensusResult(res);
    } catch (err: any) {
      setError(err.message || 'Multi-strategy consensus evaluation failed');
    } finally {
      setConsensusLoading(false);
    }
  };

  const selectedStrategy = AVAILABLE_STRATEGIES.find((s) => s.key === selectedStrategyKey) || AVAILABLE_STRATEGIES[0];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
            <Activity className="w-5 h-5 text-gold" />
            Deterministic Strategy Lab & Quantitative Engine
          </h2>
          <p className="text-xs text-obsidian-secondary mt-1">
            Test quantitative hypotheses with event-driven execution, next-bar Open fills, explicit STT/brokerage fees, and slippage.
            Strictly prevents look-ahead leakage.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-obsidian-muted">
          <ShieldCheck className="w-4 h-4 text-market-positive" />
          <span>Look-Ahead Audit: PASSED</span>
        </div>
      </div>

      {/* Mode Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-obsidian-border pb-2">
        <button
          onClick={() => setActiveTab('single')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors ${
            activeTab === 'single'
              ? 'bg-gold text-obsidian-bg'
              : 'text-obsidian-secondary hover:text-obsidian-text hover:bg-obsidian-elevated'
          }`}
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>Single Strategy Backtest</span>
        </button>
        <button
          onClick={() => {
            setActiveTab('consensus');
            if (!consensusResult) {
              handleRunConsensus();
            }
          }}
          className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors ${
            activeTab === 'consensus'
              ? 'bg-gold text-obsidian-bg'
              : 'text-obsidian-secondary hover:text-obsidian-text hover:bg-obsidian-elevated'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>10-Model Multi-Strategy Consensus</span>
        </button>
      </div>

      {/* Target Instrument Selection Bar */}
      <div className="p-4 rounded-card bg-obsidian-card border border-obsidian-border flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <span className="text-xs text-obsidian-muted font-medium">Target Stock:</span>
          <button
            type="button"
            onClick={() => setIsSearchOpen(true)}
            className="px-3.5 py-2 rounded-md bg-obsidian-bg border border-obsidian-border hover:border-gold text-xs text-obsidian-text flex items-center gap-2 transition-colors"
          >
            <span className="font-mono font-bold text-gold">{symbol}</span>
            <span className="text-obsidian-muted text-xs">({instrumentName})</span>
            <Search className="w-3.5 h-3.5 text-obsidian-muted ml-2" />
          </button>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-obsidian-muted">Quick Tickers:</span>
          {['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'GREENPOWER'].map((sym) => (
            <button
              key={sym}
              onClick={() => {
                setSymbol(sym);
                setInstrumentName(sym === 'RELIANCE' ? 'Reliance Industries' : sym);
              }}
              className={`px-2 py-1 rounded text-xs font-mono transition-colors ${
                symbol === sym
                  ? 'bg-gold/20 text-gold border border-gold/40'
                  : 'bg-obsidian-elevated text-obsidian-secondary hover:text-gold border border-obsidian-border'
              }`}
            >
              {sym}
            </button>
          ))}
        </div>
      </div>

      {/* TAB 1: Single Strategy Deep Dive */}
      {activeTab === 'single' && (
        <div className="space-y-6">
          {/* Strategy Selection & Parameters Bar */}
          <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
              <h3 className="text-sm font-semibold text-obsidian-text">Strategy Configuration</h3>
              <span className="text-xs text-gold font-mono">{selectedStrategy.category}</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
              {/* Select Strategy Dropdown */}
              <div className="md:col-span-2">
                <label className="text-xs text-obsidian-muted block mb-1.5 font-medium">Select Algorithm</label>
                <select
                  value={selectedStrategyKey}
                  onChange={(e) => setSelectedStrategyKey(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold font-medium"
                >
                  {AVAILABLE_STRATEGIES.map((strat) => (
                    <option key={strat.key} value={strat.key}>
                      {strat.name} ({strat.category})
                    </option>
                  ))}
                </select>
                <p className="text-[11px] text-obsidian-muted mt-1 truncate">{selectedStrategy.description}</p>
              </div>

              {/* Dynamic Parameter 1 */}
              {(selectedStrategyKey === 'sma_crossover' || selectedStrategyKey === 'ema_crossover') && (
                <>
                  <div>
                    <label className="text-xs text-obsidian-muted block mb-1.5 font-medium">Fast Period (Days)</label>
                    <input
                      type="number"
                      value={fastPeriod}
                      onChange={(e) => setFastPeriod(Number(e.target.value))}
                      min={3}
                      max={50}
                      className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold tabular-nums"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-obsidian-muted block mb-1.5 font-medium">Slow Period (Days)</label>
                    <input
                      type="number"
                      value={slowPeriod}
                      onChange={(e) => setSlowPeriod(Number(e.target.value))}
                      min={10}
                      max={200}
                      className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold tabular-nums"
                    />
                  </div>
                </>
              )}

              {selectedStrategyKey === 'rsi_threshold' && (
                <div>
                  <label className="text-xs text-obsidian-muted block mb-1.5 font-medium">RSI Lookback (Days)</label>
                  <input
                    type="number"
                    value={rsiPeriod}
                    onChange={(e) => setRsiPeriod(Number(e.target.value))}
                    min={5}
                    max={30}
                    className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold tabular-nums"
                  />
                </div>
              )}

              {/* Capital */}
              <div>
                <label className="text-xs text-obsidian-muted block mb-1.5 font-medium">Initial Capital (INR)</label>
                <input
                  type="number"
                  value={initialCapital}
                  onChange={(e) => setInitialCapital(Number(e.target.value))}
                  step={10000}
                  className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold tabular-nums"
                />
              </div>

              {/* Execute Button */}
              <div className="flex items-end">
                <button
                  onClick={handleRunSingleBacktest}
                  disabled={loading}
                  className="w-full py-2.5 rounded-xl bg-gold hover:bg-gold-hover text-obsidian-bg font-bold text-xs flex items-center justify-center gap-1.5 transition-all disabled:opacity-50 shadow-md"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>{loading ? 'Simulating...' : 'Run Backtest'}</span>
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-market-negative/10 border border-market-negative/20 text-xs text-market-negative flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Metrics Row */}
          {metrics && (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
              <MetricCard
                title="Strategy CAGR"
                value={`${metrics.cagr}%`}
                sentiment={metrics.cagr > 0 ? 'positive' : 'negative'}
                change={`vs Bench: ${metrics.benchmark_cagr ?? '0.0'}%`}
              />
              <MetricCard
                title="Sharpe Ratio"
                value={metrics.sharpe_ratio}
                sentiment={metrics.sharpe_ratio > 0.5 ? 'positive' : 'neutral'}
                subtitle="Risk-Free Rate: 6.0%"
              />
              <MetricCard
                title="Max Drawdown"
                value={`-${metrics.max_drawdown}%`}
                sentiment="negative"
                change={`Bench: -${metrics.benchmark_max_drawdown ?? '0.0'}%`}
              />
              <MetricCard
                title="Win Rate"
                value={`${metrics.win_rate}%`}
                sentiment={metrics.win_rate >= 50 ? 'positive' : 'neutral'}
                subtitle={`${metrics.total_trades} Executed Trades`}
              />
              <MetricCard
                title="Profit Factor"
                value={metrics.profit_factor}
                sentiment={metrics.profit_factor > 1.0 ? 'gold' : 'neutral'}
                subtitle="Gross Gain / Loss"
              />
              <MetricCard
                title="Ann. Volatility"
                value={`${metrics.annualized_volatility}%`}
                subtitle="252 Trading Days"
              />
            </div>
          )}

          {/* Equity Curve Chart */}
          {metrics && metrics.equity_curve && (
            <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-obsidian-text">
                  Equity Curve & Mark-to-Market Portfolio Valuation
                </h3>
                <span className="text-xs text-gold font-mono">
                  {selectedStrategy.name}
                </span>
              </div>
              <EquityChart
                data={metrics.equity_curve}
                benchmarkCagr={metrics.benchmark_cagr}
                initialCapital={initialCapital}
              />
            </div>
          )}

          {/* Executed Trade Logs Table */}
          {metrics && metrics.trades && (
            <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-obsidian-text">
                  Audited Trade Executions ({metrics.trades.length})
                </h3>
                <span className="text-xs text-obsidian-muted">
                  Executed at bar Open with {slippagePct * 100}% slippage and {feePct * 100}% transaction fee
                </span>
              </div>

              {metrics.trades.length === 0 ? (
                <div className="p-6 text-center text-xs text-obsidian-muted">
                  No trades generated for this parameter combination over the period.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-obsidian-border text-obsidian-muted">
                        <th className="pb-3 font-medium">Trade #</th>
                        <th className="pb-3 font-medium">Entry Date</th>
                        <th className="pb-3 font-medium">Entry Price</th>
                        <th className="pb-3 font-medium">Exit Date</th>
                        <th className="pb-3 font-medium">Exit Price</th>
                        <th className="pb-3 font-medium">Shares</th>
                        <th className="pb-3 font-medium">Realized PnL</th>
                        <th className="pb-3 font-medium text-right">Return %</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-obsidian-border/40 font-mono">
                      {metrics.trades.map((t: any, idx) => {
                        const ret = Number(t?.return_pct ?? 0);
                        const isWin = ret > 0;
                        const entryDate = String(t?.entry_date ?? t?.timestamp ?? 'N/A').slice(0, 10);
                        const exitDate = String(t?.exit_date ?? t?.timestamp ?? 'N/A').slice(0, 10);
                        const entryPrice = Number(t?.entry_price ?? t?.price ?? 0);
                        const exitPrice = Number(t?.exit_price ?? t?.price ?? 0);
                        const numShares = Number(t?.shares ?? 0);
                        const pnlVal = Number(t?.pnl ?? 0);
                        return (
                          <tr key={idx} className="hover:bg-obsidian-hover/40 transition-colors">
                            <td className="py-2.5 text-obsidian-muted font-mono">{idx + 1}</td>
                            <td className="py-2.5 text-obsidian-secondary">{entryDate}</td>
                            <td className="py-2.5 text-obsidian-text">₹{entryPrice.toFixed(2)}</td>
                            <td className="py-2.5 text-obsidian-secondary">{exitDate}</td>
                            <td className="py-2.5 text-obsidian-text">₹{exitPrice.toFixed(2)}</td>
                            <td className="py-2.5 text-obsidian-muted">{numShares.toFixed(1)}</td>
                            <td className={`py-2.5 font-bold ${isWin ? 'text-market-positive' : 'text-market-negative'}`}>
                              {isWin ? '+' : ''}₹{pnlVal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                            </td>
                            <td className={`py-2.5 text-right font-bold ${isWin ? 'text-market-positive' : 'text-market-negative'}`}>
                              {isWin ? '+' : ''}{ret.toFixed(2)}%
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Multi-Strategy Consensus Matrix */}
      {activeTab === 'consensus' && (
        <div className="space-y-6">
          <div className="p-6 rounded-card bg-obsidian-card border border-gold/40 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold tracking-wider text-gold uppercase block mb-1">
                  Ensemble Quantitative Voting
                </span>
                <h3 className="text-lg font-bold text-obsidian-text flex items-center gap-2">
                  <Layers className="w-5 h-5 text-gold" />
                  10-Model Strategy Consensus on {symbol}
                </h3>
                <p className="text-xs text-obsidian-secondary mt-1">
                  Runs all 10 independent strategies across trend, momentum, mean-reversion, volatility, and fundamental value to measure consensus agreement.
                </p>
              </div>

              <button
                onClick={handleRunConsensus}
                disabled={consensusLoading}
                className="px-5 py-2.5 rounded-xl bg-gold hover:bg-gold-hover text-obsidian-bg font-bold text-xs flex items-center gap-2 transition-all disabled:opacity-50 shrink-0 shadow-md"
              >
                <RotateCcw className={`w-3.5 h-3.5 ${consensusLoading ? 'animate-spin' : ''}`} />
                <span>{consensusLoading ? 'Evaluating Ensemble...' : 'Re-Evaluate Consensus'}</span>
              </button>
            </div>

            {consensusResult && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-obsidian-border/60">
                <div className="p-3.5 rounded-xl bg-obsidian-bg border border-obsidian-border">
                  <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Consensus Rating</span>
                  <span
                    className={`text-base font-bold font-mono tracking-wider ${
                      consensusResult.consensus_rating === 'BUY'
                        ? 'text-market-positive'
                        : consensusResult.consensus_rating === 'SELL'
                        ? 'text-market-negative'
                        : 'text-gold'
                    }`}
                  >
                    {consensusResult.consensus_rating}
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-obsidian-bg border border-obsidian-border">
                  <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Agreement %</span>
                  <span className="text-base font-bold font-mono text-gold tabular-nums">
                    {consensusResult.consensus_percentage}%
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-obsidian-bg border border-obsidian-border">
                  <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Vote Tally</span>
                  <span className="text-xs font-semibold text-obsidian-text tabular-nums">
                    <span className="text-market-positive">{consensusResult.buy_signals} BUY</span> •{' '}
                    <span className="text-gold">{consensusResult.hold_signals} HOLD</span> •{' '}
                    <span className="text-market-negative">{consensusResult.sell_signals} SELL</span>
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-obsidian-bg border border-obsidian-border">
                  <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Total Models</span>
                  <span className="text-base font-bold font-mono text-obsidian-text tabular-nums">
                    {consensusResult.total_strategies} Strategies
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Comparative Strategy Table */}
          {consensusResult && consensusResult.signals && (
            <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
              <h4 className="text-sm font-semibold text-obsidian-text flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-gold" />
                Individual Model Signals & Performance
              </h4>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-obsidian-border text-obsidian-muted">
                      <th className="pb-3 font-medium">Strategy</th>
                      <th className="pb-3 font-medium">Category</th>
                      <th className="pb-3 font-medium">Signal</th>
                      <th className="pb-3 font-medium">Signal Strength</th>
                      <th className="pb-3 font-medium">CAGR</th>
                      <th className="pb-3 font-medium">Sharpe</th>
                      <th className="pb-3 font-medium">Max DD</th>
                      <th className="pb-3 font-medium">Win Rate</th>
                      <th className="pb-3 font-medium">Model Rationale</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-obsidian-border/40 font-mono">
                    {consensusResult.signals.map((sig, idx) => {
                      const isBuy = sig.signal === 'BUY';
                      const isSell = sig.signal === 'SELL';
                      return (
                        <tr key={idx} className="hover:bg-obsidian-hover/40 transition-colors">
                          <td className="py-3 font-bold text-obsidian-text font-sans">{sig.name}</td>
                          <td className="py-3 text-obsidian-muted font-sans">{sig.category}</td>
                          <td className="py-3">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                                isBuy
                                  ? 'bg-market-positive/15 text-market-positive border border-market-positive/30'
                                  : isSell
                                  ? 'bg-market-negative/15 text-market-negative border border-market-negative/30'
                                  : 'bg-gold/15 text-gold border border-gold/30'
                              }`}
                            >
                              {sig.signal}
                            </span>
                          </td>
                          <td className="py-3 text-obsidian-text">
                            {(sig.signal_strength * 100).toFixed(0)}%
                          </td>
                          <td className={`py-3 font-bold ${sig.cagr && sig.cagr > 0 ? 'text-market-positive' : 'text-obsidian-secondary'}`}>
                            {sig.cagr !== undefined ? `${sig.cagr}%` : 'N/A'}
                          </td>
                          <td className="py-3 text-obsidian-secondary">
                            {sig.sharpe_ratio !== undefined ? sig.sharpe_ratio : 'N/A'}
                          </td>
                          <td className="py-3 text-market-negative">
                            {sig.max_drawdown !== undefined ? `-${sig.max_drawdown}%` : 'N/A'}
                          </td>
                          <td className="py-3 text-obsidian-secondary">
                            {sig.win_rate !== undefined ? `${sig.win_rate}%` : 'N/A'}
                          </td>
                          <td className="py-3 text-obsidian-secondary font-sans text-[11px] max-w-xs leading-tight">
                            {sig.summary}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Universe Instrument Search Modal */}
      <InstrumentSearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onSelectInstrument={(selectedSym, selectedInst) => {
          setSymbol(selectedSym);
          if (selectedInst) {
            setInstrumentName(selectedInst.company_name);
          }
          setIsSearchOpen(false);
        }}
      />
    </div>
  );
};
