import React, { useState, useEffect } from 'react';
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  Activity,
  AlertTriangle,
  Play,
  RotateCcw,
  ShieldCheck,
  CheckCircle2,
  DollarSign,
  Plus
} from 'lucide-react';
import {
  listVirtualPortfolios,
  createVirtualPortfolio,
  getVirtualPortfolio,
  executeVirtualOrder,
  runScenarioSimulation
} from '../services/api';
import { VirtualPortfolio, ScenarioSimulation } from '../types';

export const VirtualPortfolioPage: React.FC = () => {
  const [portfolios, setPortfolios] = useState<VirtualPortfolio[]>([]);
  const [activePortfolio, setActivePortfolio] = useState<VirtualPortfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [orderSymbol, setOrderSymbol] = useState('RELIANCE');
  const [orderSide, setOrderSide] = useState<'BUY' | 'SELL'>('BUY');
  const [orderQuantity, setOrderQuantity] = useState(10);
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT'>('MARKET');
  const [orderPrice, setOrderPrice] = useState<number | undefined>(undefined);
  const [submittingOrder, setSubmittingOrder] = useState(false);
  const [orderMessage, setOrderMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Scenario Simulation State
  const [selectedScenario, setSelectedScenario] = useState<{ type: string; pct: number }>({ type: 'market_correction', pct: -15.0 });
  const [simulationResult, setSimulationResult] = useState<ScenarioSimulation | null>(null);
  const [simulating, setSimulating] = useState(false);

  // Create new portfolio modal state
  const [newPortName, setNewPortName] = useState('Primary Investment Simulation');
  const [newPortCapital, setNewPortCapital] = useState(100000);
  const [isCreatingPort, setIsCreatingPort] = useState(false);

  useEffect(() => {
    loadPortfolios();
  }, []);

  const loadPortfolios = async () => {
    setLoading(true);
    try {
      const list = await listVirtualPortfolios();
      if (list && list.length > 0) {
        setPortfolios(list);
        setActivePortfolio(list[0]);
      } else {
        // Auto-create default portfolio if none exist
        const defaultPort = await createVirtualPortfolio('Primary Research Portfolio', 100000);
        setPortfolios([defaultPort]);
        setActivePortfolio(defaultPort);
      }
    } catch (err) {
      console.error('Failed to load virtual portfolios:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshActivePortfolio = async () => {
    if (!activePortfolio) return;
    try {
      const updated = await getVirtualPortfolio(activePortfolio.id);
      setActivePortfolio(updated);
    } catch (err) {
      console.error('Failed to refresh portfolio:', err);
    }
  };

  const handleExecuteOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activePortfolio) return;
    setSubmittingOrder(true);
    setOrderMessage(null);

    try {
      await executeVirtualOrder(
        activePortfolio.id,
        orderSymbol,
        orderSide,
        orderQuantity,
        orderType,
        orderPrice
      );
      setOrderMessage({
        type: 'success',
        text: `Virtual ${orderSide} order for ${orderQuantity} shares of ${orderSymbol} executed successfully.`
      });
      await refreshActivePortfolio();
    } catch (err: any) {
      setOrderMessage({
        type: 'error',
        text: err.message || 'Virtual order execution failed.'
      });
    } finally {
      setSubmittingOrder(false);
    }
  };

  const handleRunScenario = async (type: string, pct: number) => {
    if (!activePortfolio) return;
    setSelectedScenario({ type, pct });
    setSimulating(true);

    try {
      const res = await runScenarioSimulation(activePortfolio.id, type, pct);
      setSimulationResult(res);
    } catch (err: any) {
      console.error('Scenario simulation failed:', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleCreateNewPortfolio = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createVirtualPortfolio(newPortName, newPortCapital);
      setPortfolios([...portfolios, created]);
      setActivePortfolio(created);
      setIsCreatingPort(false);
    } catch (err: any) {
      alert(err.message || 'Failed to create portfolio');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm text-obsidian-muted">Loading Virtual Investment Environment...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-obsidian-border pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-semibold text-obsidian-text tracking-tight">Virtual Investment Portfolio</h1>
            <span className="px-2 py-0.5 rounded text-xs font-mono font-medium bg-gold/10 text-gold border border-gold/30">
              PAPER TRADING LAB
            </span>
          </div>
          <p className="text-sm text-obsidian-muted mt-1">
            Simulate realistic order execution, mark-to-market positions, cash balances, and what-if stress tests without risking real capital.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {portfolios.length > 1 && (
            <select
              value={activePortfolio?.id}
              onChange={(e) => {
                const found = portfolios.find((p) => p.id === e.target.value);
                if (found) setActivePortfolio(found);
              }}
              className="bg-obsidian-card border border-obsidian-border text-obsidian-text text-xs rounded px-3 py-2 focus:border-gold outline-none"
            >
              {portfolios.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          )}

          <button
            onClick={() => setIsCreatingPort(!isCreatingPort)}
            className="flex items-center gap-1.5 px-3 py-2 rounded text-xs font-medium bg-obsidian-card text-gold border border-gold/30 hover:bg-gold/10 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Portfolio</span>
          </button>
        </div>
      </div>

      {/* New Portfolio Inline Modal */}
      {isCreatingPort && (
        <form onSubmit={handleCreateNewPortfolio} className="p-4 rounded-md bg-obsidian-card border border-gold/40 space-y-3">
          <h3 className="text-sm font-medium text-obsidian-text">Create Virtual Simulation Portfolio</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-obsidian-muted block mb-1">Portfolio Name</label>
              <input
                type="text"
                value={newPortName}
                onChange={(e) => setNewPortName(e.target.value)}
                className="w-full bg-obsidian-surface border border-obsidian-border rounded px-3 py-1.5 text-xs text-obsidian-text focus:border-gold outline-none"
                required
              />
            </div>
            <div>
              <label className="text-xs text-obsidian-muted block mb-1">Starting Capital (INR)</label>
              <input
                type="number"
                value={newPortCapital}
                onChange={(e) => setNewPortCapital(Number(e.target.value))}
                min={5000}
                step={5000}
                className="w-full bg-obsidian-surface border border-obsidian-border rounded px-3 py-1.5 text-xs text-obsidian-text focus:border-gold outline-none"
                required
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIsCreatingPort(false)}
              className="px-3 py-1.5 rounded text-xs text-obsidian-muted hover:text-obsidian-text"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 rounded text-xs font-medium bg-gold text-obsidian-bg hover:bg-gold-light"
            >
              Initialize Portfolio
            </button>
          </div>
        </form>
      )}

      {/* Primary KPI Metrics */}
      {activePortfolio && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="p-3.5 rounded-md bg-obsidian-card border border-obsidian-border">
            <span className="text-xs text-obsidian-muted block mb-1">Total Valuation</span>
            <div className="text-lg font-mono font-semibold text-obsidian-text">
              INR {activePortfolio.total_portfolio_value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
          </div>

          <div className="p-3.5 rounded-md bg-obsidian-card border border-obsidian-border">
            <span className="text-xs text-obsidian-muted block mb-1">Virtual Cash</span>
            <div className="text-lg font-mono font-semibold text-gold">
              INR {activePortfolio.cash_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
          </div>

          <div className="p-3.5 rounded-md bg-obsidian-card border border-obsidian-border">
            <span className="text-xs text-obsidian-muted block mb-1">Invested Capital</span>
            <div className="text-lg font-mono font-semibold text-obsidian-secondary">
              INR {activePortfolio.invested_capital.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
          </div>

          <div className="p-3.5 rounded-md bg-obsidian-card border border-obsidian-border">
            <span className="text-xs text-obsidian-muted block mb-1">Unrealized P&L</span>
            <div className={`text-lg font-mono font-semibold flex items-center gap-1 ${
              activePortfolio.total_unrealized_pnl >= 0 ? 'text-market-positive' : 'text-market-negative'
            }`}>
              {activePortfolio.total_unrealized_pnl >= 0 ? '+' : ''}
              INR {activePortfolio.total_unrealized_pnl.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
          </div>

          <div className="p-3.5 rounded-md bg-obsidian-card border border-obsidian-border">
            <span className="text-xs text-obsidian-muted block mb-1">Realized P&L</span>
            <div className={`text-lg font-mono font-semibold ${
              activePortfolio.total_realized_pnl >= 0 ? 'text-market-positive' : 'text-market-negative'
            }`}>
              {activePortfolio.total_realized_pnl >= 0 ? '+' : ''}
              INR {activePortfolio.total_realized_pnl.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
          </div>

          <div className="p-3.5 rounded-md bg-obsidian-card border border-obsidian-border">
            <span className="text-xs text-obsidian-muted block mb-1">Total Return</span>
            <div className={`text-lg font-mono font-semibold ${
              activePortfolio.total_return_pct >= 0 ? 'text-market-positive' : 'text-market-negative'
            }`}>
              {activePortfolio.total_return_pct >= 0 ? '+' : ''}
              {activePortfolio.total_return_pct.toFixed(2)}%
            </div>
          </div>
        </div>
      )}

      {/* Main Workspace: Order Console & Holdings */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Paper Trading Order Execution Form */}
        <div className="p-5 rounded-md bg-obsidian-card border border-obsidian-border space-y-4">
          <div className="flex items-center justify-between border-b border-obsidian-border pb-3">
            <h2 className="text-sm font-semibold text-obsidian-text flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-gold" />
              Virtual Paper Trade
            </h2>
            <span className="text-xs text-obsidian-muted font-mono">0.1% fee | 0.05% slip</span>
          </div>

          {orderMessage && (
            <div className={`p-3 rounded text-xs flex items-center gap-2 ${
              orderMessage.type === 'success'
                ? 'bg-market-positive/10 border border-market-positive/30 text-market-positive'
                : 'bg-market-negative/10 border border-market-negative/30 text-market-negative'
            }`}>
              {orderMessage.type === 'success' ? (
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              ) : (
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              )}
              <span>{orderMessage.text}</span>
            </div>
          )}

          <form onSubmit={handleExecuteOrder} className="space-y-3.5">
            {/* Side Toggle: BUY vs SELL */}
            <div className="grid grid-cols-2 gap-2 p-1 rounded bg-obsidian-surface border border-obsidian-border">
              <button
                type="button"
                onClick={() => setOrderSide('BUY')}
                className={`py-1.5 rounded text-xs font-semibold transition-colors ${
                  orderSide === 'BUY'
                    ? 'bg-market-positive text-obsidian-bg shadow-sm'
                    : 'text-obsidian-muted hover:text-obsidian-text'
                }`}
              >
                BUY / LONG
              </button>
              <button
                type="button"
                onClick={() => setOrderSide('SELL')}
                className={`py-1.5 rounded text-xs font-semibold transition-colors ${
                  orderSide === 'SELL'
                    ? 'bg-market-negative text-obsidian-bg shadow-sm'
                    : 'text-obsidian-muted hover:text-obsidian-text'
                }`}
              >
                SELL / EXIT
              </button>
            </div>

            {/* Instrument Symbol */}
            <div>
              <label className="text-xs font-medium text-obsidian-muted block mb-1">Target Instrument</label>
              <div className="flex gap-1.5 mb-1.5">
                {['RELIANCE', 'GREENPOWER', 'TATAMOTORS', 'INFY'].map((sym) => (
                  <button
                    key={sym}
                    type="button"
                    onClick={() => setOrderSymbol(sym)}
                    className={`px-2 py-1 rounded text-xs font-mono transition-colors ${
                      orderSymbol === sym
                        ? 'bg-gold/20 text-gold border border-gold/40'
                        : 'bg-obsidian-surface text-obsidian-muted border border-obsidian-border hover:text-obsidian-text'
                    }`}
                  >
                    {sym}
                  </button>
                ))}
              </div>
              <input
                type="text"
                value={orderSymbol}
                onChange={(e) => setOrderSymbol(e.target.value.toUpperCase())}
                placeholder="e.g. RELIANCE, TATASTEEL"
                className="w-full bg-obsidian-surface border border-obsidian-border rounded px-3 py-2 text-xs font-mono text-obsidian-text focus:border-gold outline-none"
                required
              />
            </div>

            {/* Quantity */}
            <div>
              <label className="text-xs font-medium text-obsidian-muted block mb-1">Shares Quantity</label>
              <input
                type="number"
                min={1}
                value={orderQuantity}
                onChange={(e) => setOrderQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-full bg-obsidian-surface border border-obsidian-border rounded px-3 py-2 text-xs font-mono text-obsidian-text focus:border-gold outline-none"
                required
              />
            </div>

            {/* Order Type */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-medium text-obsidian-muted block mb-1">Order Execution</label>
                <select
                  value={orderType}
                  onChange={(e) => setOrderType(e.target.value as any)}
                  className="w-full bg-obsidian-surface border border-obsidian-border rounded px-2.5 py-2 text-xs text-obsidian-text focus:border-gold outline-none"
                >
                  <option value="MARKET">Market Execution</option>
                  <option value="LIMIT">Limit Price</option>
                </select>
              </div>

              {orderType === 'LIMIT' && (
                <div>
                  <label className="text-xs font-medium text-obsidian-muted block mb-1">Limit Price (INR)</label>
                  <input
                    type="number"
                    step="0.05"
                    value={orderPrice || ''}
                    onChange={(e) => setOrderPrice(parseFloat(e.target.value) || undefined)}
                    placeholder="e.g. 2500.00"
                    className="w-full bg-obsidian-surface border border-obsidian-border rounded px-2.5 py-2 text-xs font-mono text-obsidian-text focus:border-gold outline-none"
                  />
                </div>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submittingOrder}
              className={`w-full py-2.5 rounded font-medium text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm ${
                orderSide === 'BUY'
                  ? 'bg-market-positive text-obsidian-bg hover:brightness-110'
                  : 'bg-market-negative text-obsidian-bg hover:brightness-110'
              } disabled:opacity-50`}
            >
              {submittingOrder ? (
                <span>Executing Order...</span>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Execute Virtual {orderSide} Order</span>
                </>
              )}
            </button>
          </form>

          {/* Micro Disclaimers */}
          <p className="text-[11px] text-obsidian-muted leading-relaxed border-t border-obsidian-border pt-3">
            Virtual trades execute against live or validated historical market feeds with deterministic slippage (0.05%) and statutory fees (0.10%). Real broker orders are never submitted.
          </p>
        </div>

        {/* Right: Open Holdings / Positions Table */}
        <div className="lg:col-span-2 p-5 rounded-md bg-obsidian-card border border-obsidian-border space-y-4">
          <div className="flex items-center justify-between border-b border-obsidian-border pb-3">
            <h2 className="text-sm font-semibold text-obsidian-text flex items-center gap-2">
              <Wallet className="w-4 h-4 text-gold" />
              Active Simulated Positions ({activePortfolio?.positions.length || 0})
            </h2>
            <button
              onClick={refreshActivePortfolio}
              className="text-xs text-obsidian-muted hover:text-gold flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Refresh Mark-to-Market</span>
            </button>
          </div>

          {activePortfolio && activePortfolio.positions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-obsidian-surface/60 text-obsidian-muted border-b border-obsidian-border font-medium">
                  <tr>
                    <th className="py-2.5 px-3">Symbol</th>
                    <th className="py-2.5 px-3 text-right">Shares</th>
                    <th className="py-2.5 px-3 text-right">Avg Entry</th>
                    <th className="py-2.5 px-3 text-right">Current Price</th>
                    <th className="py-2.5 px-3 text-right">Valuation</th>
                    <th className="py-2.5 px-3 text-right">Unrealized P&L</th>
                    <th className="py-2.5 px-3 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-obsidian-border font-mono">
                  {activePortfolio.positions.map((pos) => (
                    <tr key={pos.id} className="hover:bg-obsidian-hover/40 transition-colors">
                      <td className="py-3 px-3 font-semibold text-obsidian-text">
                        <div>{pos.symbol}</div>
                        <span className="text-[10px] text-obsidian-muted">{pos.exchange}</span>
                      </td>
                      <td className="py-3 px-3 text-right">{pos.quantity}</td>
                      <td className="py-3 px-3 text-right">INR {pos.average_entry_price.toFixed(2)}</td>
                      <td className="py-3 px-3 text-right">INR {pos.current_price.toFixed(2)}</td>
                      <td className="py-3 px-3 text-right">INR {pos.current_value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                      <td className={`py-3 px-3 text-right font-semibold ${
                        pos.unrealized_pnl >= 0 ? 'text-market-positive' : 'text-market-negative'
                      }`}>
                        {pos.unrealized_pnl >= 0 ? '+' : ''}
                        INR {pos.unrealized_pnl.toFixed(2)} ({pos.unrealized_pnl_pct.toFixed(2)}%)
                      </td>
                      <td className="py-3 px-3 text-center">
                        <button
                          onClick={() => {
                            setOrderSymbol(pos.symbol);
                            setOrderSide('SELL');
                            setOrderQuantity(pos.quantity);
                          }}
                          className="px-2 py-1 rounded text-[11px] font-sans font-medium bg-obsidian-surface text-market-negative border border-market-negative/30 hover:bg-market-negative/10"
                        >
                          Quick Exit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-12 text-center text-obsidian-muted space-y-2">
              <Wallet className="w-8 h-8 text-obsidian-muted/50 mx-auto" />
              <p className="text-xs">No active positions in this virtual portfolio.</p>
              <p className="text-[11px] text-obsidian-muted/70">Execute a paper trade on the left to allocate starting capital.</p>
            </div>
          )}
        </div>
      </div>

      {/* What-If Scenario Stress Testing Console */}
      <div className="p-5 rounded-md bg-obsidian-card border border-obsidian-border space-y-4">
        <div className="flex items-center justify-between border-b border-obsidian-border pb-3">
          <div>
            <h2 className="text-sm font-semibold text-obsidian-text flex items-center gap-2">
              <Activity className="w-4 h-4 text-gold" />
              What-If Market Stress Testing
            </h2>
            <p className="text-xs text-obsidian-muted mt-0.5">
              Simulate macro shocks across portfolio positions to evaluate downside resilience and drawdown vulnerability.
            </p>
          </div>
          <span className="text-xs font-mono text-obsidian-muted">Deterministic Stress Engine</span>
        </div>

        {/* Preset Shock Scenarios */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Bull Rally (+20%)', type: 'bull_rally', pct: 20.0, color: 'border-market-positive/30 hover:bg-market-positive/10 text-market-positive' },
            { label: 'Baseline Trend (+8%)', type: 'base_case', pct: 8.0, color: 'border-gold/30 hover:bg-gold/10 text-gold' },
            { label: 'Market Correction (-15%)', type: 'market_correction', pct: -15.0, color: 'border-market-warning/30 hover:bg-market-warning/10 text-market-warning' },
            { label: 'Severe Bear Crash (-30%)', type: 'severe_bear', pct: -30.0, color: 'border-market-negative/30 hover:bg-market-negative/10 text-market-negative' }
          ].map((scen) => (
            <button
              key={scen.type}
              type="button"
              disabled={simulating}
              onClick={() => handleRunScenario(scen.type, scen.pct)}
              className={`p-3 rounded-md bg-obsidian-surface border text-left transition-colors ${scen.color} ${
                selectedScenario.type === scen.type ? 'ring-1 ring-gold' : ''
              }`}
            >
              <div className="text-xs font-medium">{scen.label}</div>
              <span className="text-[11px] font-mono opacity-80 mt-1 block">
                {scen.pct >= 0 ? `+${scen.pct}%` : `${scen.pct}%`} equity shift
              </span>
            </button>
          ))}
        </div>

        {/* Simulation Output Card */}
        {simulationResult && (
          <div className="p-4 rounded-md bg-obsidian-surface border border-gold/30 space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-obsidian-border pb-2">
              <span className="text-obsidian-text font-sans font-medium text-sm">
                Scenario Result: {simulationResult.scenario_name}
              </span>
              <span className={`font-semibold ${simulationResult.simulated_pnl >= 0 ? 'text-market-positive' : 'text-market-negative'}`}>
                {simulationResult.simulated_pnl >= 0 ? '+' : ''}
                {simulationResult.simulated_pnl_pct.toFixed(2)}%
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-1">
              <div>
                <span className="text-[11px] text-obsidian-muted block font-sans">Baseline Valuation</span>
                <span className="text-obsidian-text">
                  INR {simulationResult.baseline_portfolio_value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div>
                <span className="text-[11px] text-obsidian-muted block font-sans">Simulated Valuation</span>
                <span className="text-gold">
                  INR {simulationResult.simulated_portfolio_value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div>
                <span className="text-[11px] text-obsidian-muted block font-sans">Simulated P&L Impact</span>
                <span className={simulationResult.simulated_pnl >= 0 ? 'text-market-positive' : 'text-market-negative'}>
                  INR {simulationResult.simulated_pnl.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div>
                <span className="text-[11px] text-obsidian-muted block font-sans">Max Loss Exposure</span>
                <span className="text-market-negative">
                  INR {simulationResult.estimated_max_loss.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Statutory SEBI Footer Notice */}
      <div className="p-4 rounded-md bg-obsidian-card/60 border border-obsidian-border text-[11px] text-obsidian-muted space-y-1">
        <div className="flex items-center gap-1.5 font-medium text-obsidian-secondary">
          <ShieldCheck className="w-3.5 h-3.5 text-gold" />
          <span>Virtual Environment Regulatory Safeguards</span>
        </div>
        <p>
          MarketLab AI Virtual Portfolio is purely an educational research sandbox. All orders, executions, fills, and cash accounting are simulated in software. No real-world broker connection exists, and virtual outcomes do not represent guaranteed real-money performance.
        </p>
      </div>
    </div>
  );
};
