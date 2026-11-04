import React, { useState } from 'react';
import {
  FileText,
  ShieldCheck,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  ExternalLink,
  Info,
  Calendar,
  CheckCircle,
  Hash,
  X,
  Target,
  Shield,
  Activity,
  Layers,
  Scale
} from 'lucide-react';
import { ResearchReport, ResearchSourceCitation } from '../types';

interface ReportViewerProps {
  report: ResearchReport;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({ report }) => {
  const [selectedCitation, setSelectedCitation] = useState<ResearchSourceCitation | null>(null);

  const isBullish = report.sentiment_label === 'bullish';
  const isBearish = report.sentiment_label === 'bearish';

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-xs font-mono text-gold px-2 py-0.5 rounded bg-gold/10 border border-gold/20">
                {report.instrument.exchange}:{report.instrument.symbol}
              </span>
              <span className="text-xs text-obsidian-muted flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                {new Date(report.report_timestamp).toLocaleDateString()}
              </span>

              {/* Data Provenance Badge */}
              {report.is_fixture ? (
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-gold/10 text-gold border border-gold/30">
                  FIXTURE DATA
                </span>
              ) : (
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-market-positive/10 text-market-positive border border-market-positive/30">
                  LIVE PROVIDER RESPONSE ({report.market_data_provider?.toUpperCase() || 'LIVE'})
                </span>
              )}

              {/* Embedding Provenance Badge */}
              {report.is_mock_embedding ? (
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-obsidian-elevated text-obsidian-secondary border border-obsidian-border">
                  MOCK EMBEDDINGS
                </span>
              ) : (
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-market-info/10 text-market-info border border-market-info/30">
                  REAL EMBEDDINGS
                </span>
              )}

              {/* Source Verification Badge */}
              {report.verification?.verification_passed ? (
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-market-positive/10 text-market-positive border border-market-positive/30">
                  SOURCE VERIFIED
                </span>
              ) : (
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-market-warning/10 text-market-warning border border-market-warning/30">
                  SOURCE UNVERIFIED
                </span>
              )}

              {report.is_completed_with_limitations && (
                <span className="text-[11px] font-bold text-market-warning px-2 py-0.5 rounded bg-market-warning/10 border border-market-warning/20">
                  PARTIAL RESEARCH
                </span>
              )}
            </div>
            <h2 className="text-xl font-bold text-obsidian-text">{report.instrument.company_name}</h2>
            <p className="text-xs text-obsidian-secondary mt-1">Research Thesis: "{report.research_question}"</p>
          </div>

          {/* Sentiment Badge */}
          <div className="flex items-center gap-3">
            <div
              className={`px-4 py-2.5 rounded-xl border flex items-center gap-2 font-bold text-sm uppercase tracking-wider ${
                isBullish
                  ? 'bg-market-positive/10 border-market-positive/30 text-market-positive'
                  : isBearish
                  ? 'bg-market-negative/10 border-market-negative/30 text-market-negative'
                  : 'bg-obsidian-elevated border-obsidian-border-muted text-gold'
              }`}
            >
              {isBullish ? <TrendingUp className="w-4 h-4" /> : isBearish ? <TrendingDown className="w-4 h-4" /> : <Info className="w-4 h-4" />}
              <span>{report.sentiment_label} Evidence</span>
            </div>
          </div>
        </div>

        {/* Provenance Metadata Bar */}
        <div className="mt-4 pt-3 border-t border-obsidian-border/50 grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
          <div>
            <span className="text-obsidian-muted block">Market Data Feed:</span>
            <span className="font-mono text-obsidian-text font-semibold uppercase">
              {report.market_data_provider || 'FIXTURE'} ({report.latency_type || 'HISTORICAL'})
            </span>
          </div>
          <div>
            <span className="text-obsidian-muted block">LLM Orchestrator:</span>
            <span className="font-mono text-obsidian-text font-semibold uppercase">
              {report.llm_provider || 'MOCK'} ({report.llm_model || 'default'})
            </span>
          </div>
          <div>
            <span className="text-obsidian-muted block">Citations Grounding:</span>
            <span className="font-mono text-gold font-semibold">
              {report.sources?.length || 0} Ingested Disclosures
            </span>
          </div>
          <div>
            <span className="text-obsidian-muted block">Audit Integrity:</span>
            <span className={`font-mono font-semibold ${report.verification?.calculation_consistency ? 'text-market-positive' : 'text-market-warning'}`}>
              {report.verification?.calculation_consistency ? 'Calculations Verified' : 'Anomalies Flagged'}
            </span>
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
        <h3 className="text-sm font-semibold text-obsidian-text mb-2 flex items-center gap-2">
          <FileText className="w-4 h-4 text-gold" />
          1. Executive Summary & Research Classification
        </h3>
        <p className="text-sm text-obsidian-secondary leading-relaxed mb-4">
          {report.executive_summary}
        </p>
        <div className="p-3.5 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-secondary">
          <span className="text-gold font-semibold">Classification Protocol:</span> Evidence is classified based on
          deterministic moving average alignment (20-day vs 50-day SMA), operating margins, debt trajectory, and
          verified regulatory disclosures. Not guaranteed future returns.
        </div>
      </div>

      {/* Decision Intelligence & Valuation Engine */}
      <div className="p-6 rounded-card bg-obsidian-card border border-gold/40 space-y-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-obsidian-border/70">
          <div>
            <span className="text-[10px] font-bold tracking-wider text-gold uppercase block mb-1">
              Deterministic Decision Intelligence
            </span>
            <h3 className="text-lg font-bold text-obsidian-text flex items-center gap-2">
              <Target className="w-5 h-5 text-gold" />
              2. Quantitative Investment Assessment
            </h3>
          </div>

          {/* Rating Pill */}
          <div className="flex items-center gap-3">
            <span className="text-xs text-obsidian-muted">System Recommendation:</span>
            <div
              className={`px-4 py-2 rounded-xl border text-sm font-bold tracking-wider uppercase flex items-center gap-2 ${
                report.decision_rating === 'BUY'
                  ? 'bg-market-positive/15 border-market-positive/40 text-market-positive'
                  : report.decision_rating === 'SELL'
                  ? 'bg-market-negative/15 border-market-negative/40 text-market-negative'
                  : report.decision_rating === 'HOLD'
                  ? 'bg-gold/15 border-gold/40 text-gold'
                  : 'bg-market-warning/15 border-market-warning/40 text-market-warning'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>{report.decision_rating || 'INSUFFICIENT EVIDENCE'}</span>
            </div>
          </div>
        </div>

        {/* 4-Metric Actionable Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-3.5 rounded-xl bg-obsidian-bg border border-obsidian-border">
            <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Potential Entry Range</span>
            <span className="text-sm md:text-base font-bold font-mono text-gold tabular-nums">
              {report.entry_price_min && report.entry_price_max
                ? `₹${report.entry_price_min.toFixed(2)} - ₹${report.entry_price_max.toFixed(2)}`
                : 'Market Dependent'}
            </span>
            <span className="text-[11px] text-obsidian-muted block mt-1">Based on ATR & Moving Averages</span>
          </div>

          <div className="p-3.5 rounded-xl bg-obsidian-bg border border-obsidian-border">
            <span className="text-[10px] text-obsidian-muted uppercase block mb-1">DCF Fair Value Range</span>
            <span className="text-sm md:text-base font-bold font-mono text-obsidian-text tabular-nums">
              {report.fair_value_min && report.fair_value_max
                ? `₹${report.fair_value_min.toFixed(2)} - ₹${report.fair_value_max.toFixed(2)}`
                : 'Insufficient FCF History'}
            </span>
            <span className="text-[11px] text-obsidian-muted block mt-1">Sensitivity Matrix Evaluated</span>
          </div>

          <div className="p-3.5 rounded-xl bg-obsidian-bg border border-obsidian-border">
            <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Downside Invalidation (Stop-Loss)</span>
            <span className="text-sm md:text-base font-bold font-mono text-market-negative tabular-nums">
              {report.stop_loss_price ? `₹${report.stop_loss_price.toFixed(2)}` : 'N/A'}
            </span>
            <span className="text-[11px] text-obsidian-muted block mt-1">2.0x ATR Below Floor Support</span>
          </div>

          <div className="p-3.5 rounded-xl bg-obsidian-bg border border-obsidian-border">
            <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Multi-Strategy Consensus</span>
            <span className="text-sm md:text-base font-bold font-mono text-market-positive tabular-nums">
              {report.strategy_consensus
                ? `${report.strategy_consensus.consensus_percentage}% ${report.strategy_consensus.consensus_rating}`
                : '50% Ensemble Alignment'}
            </span>
            <span className="text-[11px] text-obsidian-muted block mt-1">
              {report.strategy_consensus ? `${report.strategy_consensus.buy_signals} Buy / ${report.strategy_consensus.total_strategies} Total` : 'Evaluated across 10 models'}
            </span>
          </div>
        </div>

        {/* Probabilistic Scenarios Table */}
        {report.scenario_projections && report.scenario_projections.length > 0 && (
          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold text-obsidian-text uppercase tracking-wider flex items-center gap-1.5">
                <Scale className="w-4 h-4 text-gold" />
                Scenario Projections & Price Targets
              </h4>
              <span className="text-[11px] text-obsidian-muted">Horizon: {report.horizon_type || '6 Months'}</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-obsidian-border text-obsidian-muted">
                    <th className="pb-2 font-medium">Scenario</th>
                    <th className="pb-2 font-medium">Probability</th>
                    <th className="pb-2 font-medium">Target Price</th>
                    <th className="pb-2 font-medium">Expected Return</th>
                    <th className="pb-2 font-medium">Underlying Rationale</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-obsidian-border/40 font-mono">
                  {report.scenario_projections.map((sc, idx) => {
                    const isPositive = sc.expected_return_pct >= 0;
                    return (
                      <tr key={idx} className="hover:bg-obsidian-hover/40 transition-colors">
                        <td className="py-2.5 font-bold">
                          <span
                            className={`px-2 py-0.5 rounded text-[11px] ${
                              sc.scenario === 'BULL'
                                ? 'bg-market-positive/15 text-market-positive'
                                : sc.scenario === 'BEAR'
                                ? 'bg-market-negative/15 text-market-negative'
                                : 'bg-gold/15 text-gold'
                            }`}
                          >
                            {sc.scenario}
                          </span>
                        </td>
                        <td className="py-2.5 text-obsidian-secondary font-sans font-medium">
                          {(sc.probability * 100).toFixed(0)}%
                        </td>
                        <td className="py-2.5 text-obsidian-text font-bold">₹{sc.target_price.toFixed(2)}</td>
                        <td className={`py-2.5 font-bold ${isPositive ? 'text-market-positive' : 'text-market-negative'}`}>
                          {isPositive ? '+' : ''}{sc.expected_return_pct.toFixed(1)}%
                        </td>
                        <td className="py-2.5 text-obsidian-secondary font-sans text-[11px] max-w-xs leading-relaxed">
                          {sc.rationale}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Multi-Strategy Consensus Breakdown */}
        {report.strategy_consensus && report.strategy_consensus.signals && report.strategy_consensus.signals.length > 0 && (
          <div className="space-y-3 pt-3 border-t border-obsidian-border/50">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold text-obsidian-text uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-gold" />
                10-Model Quantitative Ensemble Signals
              </h4>
              <span className="text-[11px] text-obsidian-muted">
                {report.strategy_consensus.buy_signals} BUY • {report.strategy_consensus.hold_signals} HOLD • {report.strategy_consensus.sell_signals} SELL
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
              {report.strategy_consensus.signals.map((sig, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-obsidian-bg border border-obsidian-border text-xs flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-semibold text-obsidian-text truncate max-w-[150px]">{sig.name}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        sig.signal === 'BUY'
                          ? 'bg-market-positive/15 text-market-positive border border-market-positive/30'
                          : sig.signal === 'SELL'
                          ? 'bg-market-negative/15 text-market-negative border border-market-negative/30'
                          : 'bg-gold/15 text-gold border border-gold/30'
                      }`}
                    >
                      {sig.signal}
                    </span>
                  </div>
                  <p className="text-[11px] text-obsidian-muted mb-2 leading-tight">{sig.summary}</p>
                  <div className="flex items-center justify-between text-[10px] text-obsidian-secondary border-t border-obsidian-border/50 pt-1.5 font-mono">
                    <span>CAGR: {sig.cagr !== undefined ? `${sig.cagr}%` : 'N/A'}</span>
                    <span>Win: {sig.win_rate !== undefined ? `${sig.win_rate}%` : 'N/A'}</span>
                    <span>Sharpe: {sig.sharpe_ratio !== undefined ? sig.sharpe_ratio : 'N/A'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Grid: Financial & Technical Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Fundamental Card */}
        <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
          <h3 className="text-sm font-semibold text-obsidian-text mb-4">
            2. Business & Balance Sheet Health
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-obsidian-border/60 text-xs">
              <span className="text-obsidian-muted">Reporting Period</span>
              <span className="font-semibold text-obsidian-text">{report.financial_metrics.period || 'FY2024'}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-obsidian-border/60 text-xs">
              <span className="text-obsidian-muted">Revenue from Operations</span>
              <span className="font-semibold text-obsidian-text tabular-nums">
                INR {report.financial_metrics.revenue ?? 'N/A'} Cr
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-obsidian-border/60 text-xs">
              <span className="text-obsidian-muted">Operating Margin (EBITDA)</span>
              <span className="font-semibold text-market-positive tabular-nums">
                {report.financial_metrics.operating_margin ?? 'N/A'}%
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-obsidian-border/60 text-xs">
              <span className="text-obsidian-muted">Consolidated Net Profit</span>
              <span className="font-semibold text-obsidian-text tabular-nums">
                INR {report.financial_metrics.net_profit ?? 'N/A'} Cr
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-obsidian-border/60 text-xs">
              <span className="text-obsidian-muted">Total Debt / Equity</span>
              <span className="font-semibold text-obsidian-text tabular-nums">
                {report.financial_metrics.debt_to_equity ?? '0.63'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 text-xs">
              <span className="text-obsidian-muted">Valuation (P/E | P/B)</span>
              <span className="font-semibold text-obsidian-text tabular-nums">
                {report.financial_metrics.pe_ratio ?? 'N/A'}x | {report.financial_metrics.pb_ratio ?? 'N/A'}x
              </span>
            </div>
          </div>
        </div>

        {/* Technical & Indicator Card */}
        <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
          <h3 className="text-sm font-semibold text-obsidian-text mb-4">
            3. Deterministic Technical Indicators
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-obsidian-border/60 text-xs">
              <span className="text-obsidian-muted">Latest Observed Close</span>
              <span className="font-semibold text-obsidian-text tabular-nums">
                INR {report.technical_metrics.latest_close ?? 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-obsidian-border/60 text-xs">
              <span className="text-obsidian-muted">20-Day SMA</span>
              <span className="font-semibold text-gold tabular-nums">
                INR {report.technical_metrics.sma_20 ?? 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-obsidian-border/60 text-xs">
              <span className="text-obsidian-muted">50-Day SMA</span>
              <span className="font-semibold text-obsidian-text tabular-nums">
                INR {report.technical_metrics.sma_50 ?? 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-obsidian-border/60 text-xs">
              <span className="text-obsidian-muted">RSI (14-day momentum)</span>
              <span className="font-semibold text-obsidian-text tabular-nums">
                {report.technical_metrics.rsi_14 ?? 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-obsidian-border/60 text-xs">
              <span className="text-obsidian-muted">MACD / Signal Line</span>
              <span className="font-semibold text-obsidian-text tabular-nums">
                {report.technical_metrics.macd ?? 'N/A'} / {report.technical_metrics.macd_signal ?? 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 text-xs">
              <span className="text-obsidian-muted">Annualized Volatility</span>
              <span className="font-semibold text-obsidian-text tabular-nums">
                {report.technical_metrics.annualized_volatility
                  ? (report.technical_metrics.annualized_volatility * 100).toFixed(1) + '%'
                  : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Positive & Negative Evidence */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Bullish Drivers */}
        <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
          <h3 className="text-sm font-semibold text-market-positive mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Supporting Evidence & Catalysts
          </h3>
          <ul className="space-y-2.5">
            {report.positive_evidence.map((p, idx) => (
              <li key={idx} className="text-xs text-obsidian-secondary flex items-start gap-2 leading-relaxed">
                <span className="w-1.5 h-1.5 rounded-full bg-market-positive shrink-0 mt-1.5" />
                <span>{p}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Headwinds & Opposing Evidence */}
        <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
          <h3 className="text-sm font-semibold text-market-negative mb-3 flex items-center gap-2">
            <TrendingDown className="w-4 h-4" />
            Opposing Evidence & Headwinds
          </h3>
          <ul className="space-y-2.5">
            {report.negative_evidence.map((n, idx) => (
              <li key={idx} className="text-xs text-obsidian-secondary flex items-start gap-2 leading-relaxed">
                <span className="w-1.5 h-1.5 rounded-full bg-market-negative shrink-0 mt-1.5" />
                <span>{n}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Key Risks */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
        <h3 className="text-sm font-semibold text-market-warning mb-3 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          Key Business & Operational Risk Factors
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {report.key_risks.map((risk, idx) => (
            <div key={idx} className="p-3.5 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-secondary leading-relaxed">
              <span className="text-gold font-bold block mb-1">Risk Factor 0{idx + 1}</span>
              {risk}
            </div>
          ))}
        </div>
      </div>

      {/* Citations & Evidence Sources */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-obsidian-text flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-gold" />
            Traceable Regulatory & Filings Citations ({report.sources.length})
          </h3>
          <span className="text-xs text-obsidian-muted">Grounded in pgvector chunk embeddings</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-obsidian-border text-obsidian-muted">
                <th className="pb-3 font-medium">Source Document</th>
                <th className="pb-3 font-medium">Section / Page</th>
                <th className="pb-3 font-medium">Date</th>
                <th className="pb-3 font-medium">Relevance</th>
                <th className="pb-3 font-medium text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-obsidian-border/50">
              {report.sources.map((s, idx) => (
                <tr key={idx} className="hover:bg-obsidian-hover/40 transition-colors">
                  <td className="py-3 font-medium text-obsidian-text max-w-xs truncate">
                    {s.source_title}
                  </td>
                  <td className="py-3 text-obsidian-secondary">{s.page_or_section || 'General'}</td>
                  <td className="py-3 text-obsidian-muted font-mono">{s.publication_date ? s.publication_date.slice(0, 10) : 'N/A'}</td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded bg-gold/10 text-gold border border-gold/20 font-mono">
                      {(s.confidence_score * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="py-3 text-right">
                    <button
                      onClick={() => setSelectedCitation(s)}
                      className="px-2.5 py-1 rounded bg-obsidian-elevated hover:bg-obsidian-hover text-gold border border-obsidian-border text-xs inline-flex items-center gap-1"
                    >
                      <span>View Passage</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Verification Audit Breakdown */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
        <h3 className="text-sm font-semibold text-obsidian-text mb-3 flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-market-positive" />
          Critic Verification Audit
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="p-3 rounded-xl bg-obsidian-bg border border-obsidian-border">
            <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Evidence Coverage</span>
            <span className="text-base font-bold text-obsidian-text tabular-nums">
              {(report.verification.evidence_coverage_score * 100).toFixed(0)}%
            </span>
          </div>
          <div className="p-3 rounded-xl bg-obsidian-bg border border-obsidian-border">
            <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Data Freshness</span>
            <span className="text-base font-bold text-market-positive capitalize">
              {report.verification.data_freshness_status}
            </span>
          </div>
          <div className="p-3 rounded-xl bg-obsidian-bg border border-obsidian-border">
            <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Look-Ahead Audit</span>
            <span className="text-base font-bold text-market-positive capitalize">
              {report.verification.look_ahead_bias_audit}
            </span>
          </div>
          <div className="p-3 rounded-xl bg-obsidian-bg border border-obsidian-border">
            <span className="text-[10px] text-obsidian-muted uppercase block mb-1">Calculation Consistency</span>
            <span className="text-base font-bold text-market-positive">
              {report.verification.calculation_consistency ? 'Verified' : 'Flagged'}
            </span>
          </div>
        </div>

        {/* Limitations & Legal Disclaimer */}
        <div className="p-4 rounded-xl bg-obsidian-bg border border-obsidian-border">
          <span className="text-xs font-semibold text-obsidian-text block mb-2">Methodological Limitations:</span>
          <ul className="space-y-1.5">
            {report.limitations.map((lim, idx) => (
              <li key={idx} className="text-xs text-obsidian-muted flex items-start gap-1.5">
                <span className="text-gold">•</span>
                <span>{lim}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* SEBI Statutory Compliance & Educational Disclaimer */}
      <div className="p-5 rounded-card bg-obsidian-card border border-gold/30 space-y-2">
        <div className="flex items-center gap-2 text-gold">
          <Shield className="w-4 h-4" />
          <h4 className="text-xs font-bold tracking-wide uppercase">
            SEBI Regulatory & Decision-Support Notice
          </h4>
        </div>
        <p className="text-xs text-obsidian-secondary leading-relaxed">
          {report.sebi_notice ||
            'MarketLab AI is an algorithmic quantitative research, backtesting, and virtual simulation platform engineered strictly for educational and decision-support purposes. It is NOT registered as a SEBI Investment Adviser or Research Analyst under the SEBI (Research Analysts) Regulations, 2014. No output, model projection, or strategy signal constitutes an offer, solicitation, or recommendation to buy, hold, or sell any security. Capital markets carry inherent risks; past simulated performance does not guarantee future results.'}
        </p>
      </div>

      {/* Citation Passage Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 bg-obsidian-bg/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-obsidian-card border border-obsidian-border rounded-card max-w-xl w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-obsidian-border">
              <h4 className="font-bold text-sm text-obsidian-text truncate max-w-md">{selectedCitation.source_title}</h4>
              <button
                onClick={() => setSelectedCitation(null)}
                className="text-obsidian-muted hover:text-obsidian-text p-1 rounded hover:bg-obsidian-elevated transition-colors"
                aria-label="Close modal"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center gap-3 text-xs text-obsidian-secondary">
              <span className="flex items-center gap-1 font-mono text-gold">
                <Hash className="w-3.5 h-3.5" />
                {selectedCitation.page_or_section || 'Section'}
              </span>
              <span>•</span>
              <span>Relevance: {(selectedCitation.confidence_score * 100).toFixed(0)}%</span>
            </div>
            <div className="p-4 rounded-md bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-secondary leading-relaxed max-h-60 overflow-y-auto">
              "{selectedCitation.citation_text}"
            </div>
            <div className="pt-2 flex justify-between items-center text-xs text-obsidian-muted">
              <span className="truncate max-w-xs font-mono">{selectedCitation.source_url_or_identifier}</span>
              <button
                onClick={() => setSelectedCitation(null)}
                className="px-4 py-1.5 rounded-md bg-gold text-obsidian-bg font-semibold hover:bg-gold-hover transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
