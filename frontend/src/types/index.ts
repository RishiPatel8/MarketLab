export interface Instrument {
  id: string;
  symbol: string;
  company_name: string;
  canonical_name?: string;
  display_name?: string;
  exchange: string;
  instrument_type: string;
  currency: string;
  sector?: string;
  industry?: string;
  isin?: string;
  nse_symbol?: string;
  bse_code?: string;
  bse_symbol?: string;
  scheme_code?: string;
  amc_or_issuer?: string;
  scheme_category?: string;
  plan_type?: string;
  option_type?: string;
  latest_nav?: number;
  latest_nav_date?: string;
  status?: string;
  source_provider?: string;
  data_availability?: string;
  aliases?: string;
}

export interface PaginatedInstruments {
  total: number;
  page: number;
  limit: number;
  items: Instrument[];
}

export interface InstrumentSyncStatus {
  total_instruments: number;
  active_instruments: number;
  nse_listed_count: number;
  bse_listed_count: number;
  dual_listed_count: number;
  bse_exclusive_count: number;
  etf_count: number;
  mutual_fund_count: number;
  sme_count: number;
  records_with_isin: number;
  last_sync_time_nse?: string;
  last_sync_time_bse?: string;
  last_sync_time_amfi?: string;
  last_sync_status: string;
  message: string;
}

export interface MarketBar {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  adjusted_close?: number;
  provider: string;
}

export interface ResearchSourceCitation {
  source_title: string;
  source_url_or_identifier: string;
  publication_date?: string;
  page_or_section?: string;
  citation_text: string;
  confidence_score: number;
}

export interface VerificationFindings {
  evidence_coverage_score: number;
  data_freshness_status: string;
  contradictions_detected: string[];
  unsupported_claims_flagged: string[];
  calculation_consistency: boolean;
  look_ahead_bias_audit: string;
  verification_passed: boolean;
  recommendations: string[];
}

export interface PriceTargetScenario {
  scenario: 'BULL' | 'BASE' | 'BEAR';
  probability: number;
  target_price: number;
  expected_return_pct: number;
  rationale: string;
}

export interface StrategySignal {
  strategy_key: string;
  name: string;
  category: string;
  signal: 'BUY' | 'HOLD' | 'SELL' | 'NEUTRAL';
  signal_strength: number;
  cagr?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  win_rate?: number;
  summary: string;
}

export interface StrategyConsensus {
  total_strategies: number;
  buy_signals: number;
  hold_signals: number;
  sell_signals: number;
  consensus_rating: 'BUY' | 'HOLD' | 'SELL' | 'INSUFFICIENT_EVIDENCE';
  consensus_percentage: number;
  signals: StrategySignal[];
}

export interface StrategyDefinition {
  id: string;
  strategy_key: string;
  name: string;
  category: string;
  description?: string;
  default_parameters: Record<string, any>;
  supported_timeframes: string[];
  version: string;
  is_active: boolean;
}

export interface VirtualPosition {
  id: string;
  portfolio_id: string;
  instrument_id: string;
  symbol: string;
  exchange: string;
  quantity: number;
  average_entry_price: number;
  current_price: number;
  invested_amount: number;
  current_value: number;
  realized_pnl: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
}

export interface VirtualOrder {
  id: string;
  portfolio_id: string;
  symbol: string;
  exchange: string;
  order_type: 'MARKET' | 'LIMIT';
  side: 'BUY' | 'SELL';
  quantity: number;
  requested_price?: number;
  executed_price?: number;
  transaction_fee: number;
  slippage: number;
  status: 'PENDING' | 'FILLED' | 'REJECTED' | 'CANCELLED';
  rejection_reason?: string;
  executed_at?: string;
  created_at: string;
}

export interface VirtualPortfolio {
  id: string;
  name: string;
  initial_capital: number;
  cash_balance: number;
  invested_capital: number;
  total_portfolio_value: number;
  total_unrealized_pnl: number;
  total_realized_pnl: number;
  total_return_pct: number;
  currency: string;
  portfolio_type: string;
  status: string;
  positions: VirtualPosition[];
  created_at: string;
}

export interface ScenarioSimulation {
  id: string;
  scenario_name: string;
  scenario_type: string;
  shock_pct: number;
  baseline_portfolio_value: number;
  simulated_portfolio_value: number;
  simulated_pnl: number;
  simulated_pnl_pct: number;
  estimated_max_loss: number;
  notes?: string;
  created_at: string;
}

export interface ResearchReport {
  report_id: string;
  run_id: string;
  instrument: {
    symbol: string;
    company_name: string;
    exchange: string;
  };
  research_question: string;
  sentiment_label: 'bullish' | 'neutral' | 'bearish' | 'inconclusive';
  decision_rating?: 'BUY' | 'HOLD' | 'SELL' | 'INSUFFICIENT_EVIDENCE';
  entry_price_min?: number;
  entry_price_max?: number;
  fair_value_min?: number;
  fair_value_max?: number;
  target_bull?: number;
  target_base?: number;
  target_bear?: number;
  stop_loss_price?: number;
  horizon_type?: string;
  strategy_consensus?: StrategyConsensus;
  scenario_projections?: PriceTargetScenario[];
  sebi_notice?: string;
  report_timestamp: string;
  market_data_provider?: string;
  is_fixture?: boolean;
  latency_type?: string;
  embedding_provider?: string;
  is_mock_embedding?: boolean;
  llm_provider?: string;
  llm_model?: string;
  data_coverage?: Record<string, any>;
  executive_summary: string;
  business_financial_analysis?: string;
  technical_analysis?: string;
  financial_metrics: Record<string, any>;
  technical_metrics: Record<string, any>;
  positive_evidence: string[];
  negative_evidence: string[];
  key_risks: string[];
  sources: ResearchSourceCitation[];
  verification: VerificationFindings;
  limitations: string[];
  report_markdown: string;
  is_completed_with_limitations: boolean;
}

export interface SystemStatusResponse {
  timestamp: string;
  market_data: {
    provider: string;
    status: 'CONFIGURED' | 'REACHABLE' | 'VERIFIED' | 'DEGRADED' | 'MOCK' | 'BLOCKED';
    latency_type: string;
    message: string;
  };
  llm: {
    provider: string;
    model: string;
    status: 'CONFIGURED' | 'REACHABLE' | 'VERIFIED' | 'DEGRADED' | 'MOCK' | 'BLOCKED';
    message: string;
  };
  embeddings: {
    provider: string;
    model: string;
    dimensions: number;
    status: 'CONFIGURED' | 'REACHABLE' | 'VERIFIED' | 'DEGRADED' | 'MOCK' | 'BLOCKED';
    message: string;
  };
  documents: {
    total_documents: number;
    total_chunks: number;
    mock_embedding_chunks: number;
    real_embedding_chunks: number;
    is_collection_mixed: boolean;
  };
}

export interface ResearchRunSummary {
  id: string;
  research_question: string;
  status: 'queued' | 'running' | 'completed' | 'completed_with_limitations' | 'needs_clarification' | 'failed';
  current_step: string;
  progress_percentage: number;
  resolved_instrument_id?: string;
  verification_status: string;
  created_at: string;
  completed_at?: string;
}

export interface EquityPoint {
  date: string;
  portfolio_value: number;
  close_price: number;
}

export interface TradeLog {
  entry_date: string;
  exit_date: string;
  entry_price: number;
  exit_price: number;
  shares: number;
  pnl: number;
  return_pct: number;
}

export interface ExperimentMetrics {
  cagr: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  calmar_ratio?: number;
  annualized_volatility: number;
  win_rate: number;
  profit_factor: number;
  total_trades: number;
  benchmark_cagr?: number;
  benchmark_max_drawdown?: number;
  equity_curve: EquityPoint[];
  trades: TradeLog[];
}

export interface Experiment {
  id: string;
  instrument_id: string;
  symbol: string;
  strategy_type: string;
  strategy_configuration: Record<string, any>;
  cost_assumptions: Record<string, any>;
  status: string;
  engine_version: string;
  created_at: string;
  metrics?: ExperimentMetrics;
}
