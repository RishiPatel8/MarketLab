export interface Instrument {
  id: string;
  symbol: string;
  company_name: string;
  exchange: string;
  instrument_type: string;
  currency: string;
  sector?: string;
  industry?: string;
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
  report_timestamp: string;
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
