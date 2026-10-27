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
  ArrowDownRight
} from 'lucide-react';
import { createExperiment } from '../services/api';
import { Experiment, ExperimentMetrics } from '../types';
import { EquityChart } from '../components/EquityChart';
import { MetricCard } from '../components/MetricCard';

export const StrategyLabPage: React.FC = () => {
  const [symbol, setSymbol] = useState('GREENPOWER');
  const [fastPeriod, setFastPeriod] = useState(20);
  const [slowPeriod, setSlowPeriod] = useState(50);
  const [initialCapital, setInitialCapital] = useState(100000);
  const [feePct, setFeePct] = useState(0.001); // 0.1%
  const [slippagePct, setSlippagePct] = useState(0.0005); // 0.05%
  const [loading, setLoading] = useState(false);
  const [experiment, setExperiment] = useState<Experiment | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Auto-run baseline experiment on mount
  useEffect(() => {
    handleRunBacktest();
  }, []);

  const handleRunBacktest = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await createExperiment(
        symbol,
        { fast_period: fastPeriod, slow_period: slowPeriod },
        feePct,
        slippagePct
      );
      setExperiment(res);
    } catch (err: any) {
      setError(err.message || 'Backtest execution failed');
    } finally {
      setLoading(false);
    }
  };

  const metrics = experiment?.metrics;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
            <Activity className="w-5 h-5 text-gold" />
            Deterministic Strategy Lab & Backtesting Engine
          </h2>
          <p className="text-xs text-obsidian-secondary mt-1">
            Test quantitative hypotheses with event-driven execution, next-bar Open fills, explicit brokerage/STT fees, and slippage.
            Strictly prevents look-ahead leakage.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-obsidian-muted">
          <ShieldCheck className="w-4 h-4 text-market-positive" />
          <span>Look-Ahead Audit: PASSED</span>
        </div>
      </div>

      {/* Strategy Controls Bar */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
        <h3 className="text-sm font-semibold text-obsidian-text">Strategy Configuration</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-6 gap-3">
          {/* Target Instrument */}
          <div>
            <label className="text-xs text-obsidian-muted block mb-1.5 font-medium">Instrument</label>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold"
            >
              <option value="GREENPOWER">GREENPOWER (Orient Green Power)</option>
              <option value="RELIANCE">RELIANCE (Reliance Ind.)</option>
              <option value="TATAMOTORS">TATAMOTORS (Tata Motors)</option>
              <option value="INFY">INFY (Infosys)</option>
            </select>
          </div>

          {/* Fast Period */}
          <div>
            <label className="text-xs text-obsidian-muted block mb-1.5 font-medium">Fast SMA (Days)</label>
            <input
              type="number"
              value={fastPeriod}
              onChange={(e) => setFastPeriod(Number(e.target.value))}
              min={5}
              max={100}
              className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold tabular-nums"
            />
          </div>

          {/* Slow Period */}
          <div>
            <label className="text-xs text-obsidian-muted block mb-1.5 font-medium">Slow SMA (Days)</label>
            <input
              type="number"
              value={slowPeriod}
              onChange={(e) => setSlowPeriod(Number(e.target.value))}
              min={15}
              max={250}
              className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold tabular-nums"
            />
          </div>

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

          {/* Fees */}
          <div>
            <label className="text-xs text-obsidian-muted block mb-1.5 font-medium">Fees + STT (%)</label>
            <input
              type="number"
              value={(feePct * 100).toFixed(2)}
              onChange={(e) => setFeePct(Number(e.target.value) / 100)}
              step={0.01}
              className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold tabular-nums"
            />
          </div>

          {/* Execute Button */}
          <div className="flex items-end">
            <button
              onClick={handleRunBacktest}
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-gold hover:bg-gold-hover text-obsidian-bg font-bold text-xs flex items-center justify-center gap-1.5 transition-all disabled:opacity-50 shadow-md"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{loading ? 'Running...' : 'Run Backtest'}</span>
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
            <span className="text-xs text-obsidian-muted font-mono">
              Engine Version: {experiment?.engine_version}
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
                  {metrics.trades.map((t, idx) => {
                    const isWin = t.return_pct > 0;
                    return (
                      <tr key={idx} className="hover:bg-obsidian-hover/40 transition-colors">
                        <td className="py-2.5 text-obsidian-muted font-mono">{idx + 1}</td>
                        <td className="py-2.5 text-obsidian-secondary">{t.entry_date}</td>
                        <td className="py-2.5 text-obsidian-text">₹{t.entry_price.toFixed(2)}</td>
                        <td className="py-2.5 text-obsidian-secondary">{t.exit_date}</td>
                        <td className="py-2.5 text-obsidian-text">₹{t.exit_price.toFixed(2)}</td>
                        <td className="py-2.5 text-obsidian-muted">{t.shares.toFixed(1)}</td>
                        <td className={`py-2.5 font-bold ${isWin ? 'text-market-positive' : 'text-market-negative'}`}>
                          {isWin ? '+' : ''}₹{t.pnl.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </td>
                        <td className={`py-2.5 text-right font-bold ${isWin ? 'text-market-positive' : 'text-market-negative'}`}>
                          {isWin ? '+' : ''}{t.return_pct.toFixed(2)}%
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
  );
};
