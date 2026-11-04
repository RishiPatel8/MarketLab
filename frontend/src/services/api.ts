import {
  Instrument,
  PaginatedInstruments,
  InstrumentSyncStatus,
  ResearchRunSummary,
  ResearchReport,
  Experiment
} from '../types';

const API_BASE = '/api/v1';

export async function searchInstruments(
  query: string = '',
  instrumentType: string = 'ALL',
  exchange: string = 'ALL',
  page: number = 1,
  limit: number = 20
): Promise<PaginatedInstruments> {
  try {
    const params = new URLSearchParams({
      q: query,
      instrument_type: instrumentType,
      exchange: exchange,
      page: page.toString(),
      limit: limit.toString()
    });
    const res = await fetch(`${API_BASE}/instruments/search?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to search instruments');
    return await res.json();
  } catch (err) {
    console.error('searchInstruments error:', err);
    return { total: 0, page: 1, limit: 20, items: [] };
  }
}

export async function getInstrumentSyncStatus(): Promise<InstrumentSyncStatus> {
  const res = await fetch(`${API_BASE}/instruments/sync/status`);
  if (!res.ok) throw new Error('Failed to fetch instrument sync status');
  return await res.json();
}

export async function getInstrumentById(instrumentId: string): Promise<Instrument | null> {
  try {
    const res = await fetch(`${API_BASE}/instruments/${instrumentId}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error('getInstrumentById error:', err);
    return null;
  }
}

export async function resolveInstrument(query: string) {
  const res = await fetch(`${API_BASE}/instruments/resolve?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error('Failed to resolve instrument');
  return await res.json();
}

export async function getInstrumentMarketData(instrumentId: string) {
  const res = await fetch(`${API_BASE}/instruments/${instrumentId}/market-data`);
  if (!res.ok) throw new Error('Failed to fetch market data');
  return await res.json();
}

export async function createResearch(
  question: string,
  symbol?: string,
  horizonDays: number = 180,
  investmentAmountInr: number = 50000,
  horizonCategory: string = 'medium_term',
  riskTolerance: string = 'moderate'
): Promise<{ run_id: string; status: string; message: string }> {
  const res = await fetch(`${API_BASE}/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      symbol,
      horizon_days: horizonDays,
      investment_amount_inr: investmentAmountInr,
      horizon_category: horizonCategory,
      risk_tolerance: riskTolerance
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || 'Failed to initiate research');
  }
  return await res.json();
}

// ==========================================
// Virtual Portfolio & Simulation API
// ==========================================

export async function listVirtualPortfolios() {
  const res = await fetch(`${API_BASE}/portfolios`);
  if (!res.ok) throw new Error('Failed to list virtual portfolios');
  return await res.json();
}

export async function createVirtualPortfolio(name: string, initialCapital: number = 100000) {
  const res = await fetch(`${API_BASE}/portfolios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, initial_capital: initialCapital, currency: 'INR' })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create virtual portfolio');
  }
  return await res.json();
}

export async function getVirtualPortfolio(portfolioId: string) {
  const res = await fetch(`${API_BASE}/portfolios/${portfolioId}`);
  if (!res.ok) throw new Error('Failed to load virtual portfolio');
  return await res.json();
}

export async function executeVirtualOrder(
  portfolioId: string,
  symbol: string,
  side: 'BUY' | 'SELL',
  quantity: number,
  orderType: 'MARKET' | 'LIMIT' = 'MARKET',
  requestedPrice?: number,
  exchange: string = 'NSE'
) {
  const res = await fetch(`${API_BASE}/portfolios/${portfolioId}/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol,
      side,
      quantity,
      order_type: orderType,
      requested_price: requestedPrice,
      exchange
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to execute virtual order');
  }
  return await res.json();
}

export async function runScenarioSimulation(
  portfolioId: string,
  scenarioType: string,
  shockPct: number
) {
  const res = await fetch(`${API_BASE}/portfolios/${portfolioId}/scenarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scenario_type: scenarioType,
      shock_pct: shockPct
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to run scenario simulation');
  }
  return await res.json();
}

// ==========================================
// Strategies & Quantitative Modeling API
// ==========================================

export async function getAvailableStrategies() {
  const res = await fetch(`${API_BASE}/strategies`);
  if (!res.ok) throw new Error('Failed to fetch available strategies');
  return await res.json();
}

export async function runStrategyBacktest(
  symbol: string,
  strategyKey: string,
  parameters: Record<string, any> = {},
  initialCapital: number = 100000
) {
  const res = await fetch(`${API_BASE}/strategies/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol,
      strategy_key: strategyKey,
      parameters,
      initial_capital: initialCapital
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to run strategy backtest');
  }
  return await res.json();
}

export async function evaluateStrategyConsensus(symbol: string, exchange: string = 'NSE') {
  const res = await fetch(`${API_BASE}/strategies/consensus`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol,
      exchange
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to evaluate strategy consensus');
  }
  return await res.json();
}

export async function getResearchStatus(runId: string) {
  const res = await fetch(`${API_BASE}/research/${runId}`);
  if (!res.ok) throw new Error('Failed to retrieve research status');
  return await res.json();
}

export async function getResearchReport(runId: string): Promise<ResearchReport> {
  const res = await fetch(`${API_BASE}/research/${runId}/report`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Research report not yet ready or failed.');
  }
  return await res.json();
}

export async function listResearchRuns(): Promise<ResearchRunSummary[]> {
  try {
    const res = await fetch(`${API_BASE}/research`);
    if (!res.ok) throw new Error('Failed to list research runs');
    return await res.json();
  } catch (err) {
    console.error('listResearchRuns error:', err);
    return [];
  }
}

export async function deleteResearchRun(runId: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/research/${runId}`, {
    method: 'DELETE'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to delete research run');
  }
  return true;
}

export async function clearAllResearchRuns(): Promise<boolean> {
  const res = await fetch(`${API_BASE}/research`, {
    method: 'DELETE'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to clear research library');
  }
  return true;
}

export async function createExperiment(
  symbol: string,
  parameters: { fast_period: number; slow_period: number },
  feePct: number = 0.001,
  slippagePct: number = 0.0005
): Promise<Experiment> {
  const res = await fetch(`${API_BASE}/experiments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol,
      strategy_type: 'sma_crossover',
      parameters,
      transaction_fee_pct: feePct,
      slippage_pct: slippagePct,
      benchmark_symbol: '^NSEI'
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to execute experiment');
  }
  return await res.json();
}

export async function getExperiment(id: string): Promise<Experiment> {
  const res = await fetch(`${API_BASE}/experiments/${id}`);
  if (!res.ok) throw new Error('Failed to load experiment');
  return await res.json();
}

export async function rerunExperiment(id: string): Promise<Experiment> {
  const res = await fetch(`${API_BASE}/experiments/${id}/rerun`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to rerun experiment');
  return await res.json();
}

export async function getHealth() {
  try {
    const res = await fetch('/health/ready');
    return await res.json();
  } catch {
    return { status: 'offline' };
  }
}

export async function getSystemStatus() {
  try {
    const res = await fetch(`${API_BASE}/system/status`);
    if (!res.ok) throw new Error('Failed to retrieve system status');
    return await res.json();
  } catch (err) {
    console.error('getSystemStatus error:', err);
    return null;
  }
}

export async function triggerReindex() {
  const res = await fetch(`${API_BASE}/system/reindex`, { method: 'POST' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Reindexing failed');
  }
  return await res.json();
}
