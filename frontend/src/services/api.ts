import {
  Instrument,
  ResearchRunSummary,
  ResearchReport,
  Experiment
} from '../types';

const API_BASE = '/api/v1';

export async function searchInstruments(query: string): Promise<Instrument[]> {
  try {
    const res = await fetch(`${API_BASE}/instruments/search?q=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to search instruments');
    return await res.json();
  } catch (err) {
    console.error('searchInstruments error:', err);
    return [];
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
  horizonDays: number = 180
): Promise<{ run_id: string; status: string; message: string }> {
  const res = await fetch(`${API_BASE}/research`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, symbol, horizon_days: horizonDays })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || 'Failed to initiate research');
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
