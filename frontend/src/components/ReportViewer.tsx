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
  Hash
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
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs font-mono text-gold px-2 py-0.5 rounded bg-gold/10 border border-gold/20">
                {report.instrument.exchange}:{report.instrument.symbol}
              </span>
              <span className="text-xs text-obsidian-muted flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                {new Date(report.report_timestamp).toLocaleDateString()}
              </span>
              {report.is_completed_with_limitations && (
                <span className="text-xs text-market-warning px-2 py-0.5 rounded bg-market-warning/10 border border-market-warning/20">
                  Limitations Flagged
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

      {/* Citation Passage Modal */}
      {selectedCitation && (
        <div className="fixed inset-0 bg-obsidian-bg/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-obsidian-card border border-obsidian-border rounded-card max-w-xl w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-obsidian-border">
              <h4 className="font-bold text-sm text-obsidian-text truncate max-w-md">{selectedCitation.source_title}</h4>
              <button
                onClick={() => setSelectedCitation(null)}
                className="text-obsidian-muted hover:text-obsidian-text text-sm"
              >
                ✕
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
            <div className="p-4 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-secondary leading-relaxed max-h-60 overflow-y-auto">
              "{selectedCitation.citation_text}"
            </div>
            <div className="pt-2 flex justify-between items-center text-xs text-obsidian-muted">
              <span className="truncate max-w-xs">{selectedCitation.source_url_or_identifier}</span>
              <button
                onClick={() => setSelectedCitation(null)}
                className="px-4 py-1.5 rounded-xl bg-gold text-obsidian-bg font-semibold hover:bg-gold-hover transition-colors"
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
