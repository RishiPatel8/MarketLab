import React, { useState } from 'react';
import {
  Compass,
  ArrowRight,
  ShieldCheck,
  Calculator,
  Search,
  Activity,
  Layers,
  Sparkles
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';

interface OverviewPageProps {
  onNavigate: (tab: string, symbolHint?: string) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigate }) => {
  const [quickQuery, setQuickQuery] = useState('');

  const handleQuickSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (quickQuery.trim()) {
      onNavigate('research', quickQuery.trim());
    }
  };

  const samplePrompts = [
    "Research Orient Green Power for a six-month horizon",
    "Analyze Reliance Industries operating margins and debt",
    "Test a 20-day and 50-day moving average crossover on GREENPOWER",
    "Compare renewable energy financials for Orient Green Power"
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="p-8 md:p-10 rounded-card-lg bg-gradient-to-b from-obsidian-surface to-obsidian-card border border-obsidian-border relative overflow-hidden gold-glow">
        <div className="max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gold/10 border border-gold/20 text-xs font-semibold text-gold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Agentic Indian Equities Research Platform</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-extrabold text-obsidian-text tracking-tight leading-tight">
            Transparent stock research backed by real market data and citations.
          </h2>
          <p className="text-sm md:text-base text-obsidian-secondary leading-relaxed">
            MarketLab AI separates probabilistic language models from quantitative math. Language models orchestrate
            research and verify claims, while dedicated Python engines execute deterministic calculations.
          </p>

          {/* Quick Input Bar */}
          <form onSubmit={handleQuickSubmit} className="pt-2">
            <div className="flex flex-col sm:flex-row gap-2.5 p-1.5 rounded-2xl bg-obsidian-bg border border-obsidian-border-muted shadow-lg">
              <div className="flex items-center gap-3 px-4 flex-1">
                <Search className="w-5 h-5 text-gold shrink-0" />
                <input
                  type="text"
                  value={quickQuery}
                  onChange={(e) => setQuickQuery(e.target.value)}
                  placeholder="Ask e.g. 'Research Orient Green Power for a six-month horizon'..."
                  className="w-full bg-transparent text-sm text-obsidian-text focus:outline-none placeholder:text-obsidian-muted"
                />
              </div>
              <button
                type="submit"
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-gold to-gold-hover text-obsidian-bg font-bold text-sm flex items-center justify-center gap-2 hover:opacity-95 transition-all shadow-md shrink-0"
              >
                <span>Launch Research</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Sample Prompts */}
          <div className="flex flex-wrap items-center gap-2 pt-2">
            <span className="text-xs text-obsidian-muted">Try asking:</span>
            {samplePrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => onNavigate('research', p)}
                className="text-xs px-2.5 py-1 rounded-lg bg-obsidian-elevated/70 text-obsidian-secondary hover:text-gold border border-obsidian-border transition-colors text-left truncate max-w-xs"
              >
                "{p}"
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Market Indicators Snapshot */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-obsidian-text">Active Research Coverage (NSE Equities)</h3>
          <span className="text-xs text-obsidian-muted">End-of-Day Validated Observations</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="NIFTY 50 Benchmark"
            value="23,500.00"
            change="+0.85%"
            isPositive={true}
            subtitle="Annualized Volatility: 12.8%"
          />
          <MetricCard
            title="Orient Green Power (GREENPOWER)"
            value="₹17.71"
            change="+3.42%"
            sentiment="gold"
            subtitle="Installed Wind: 402.3 MW"
          />
          <MetricCard
            title="Reliance Industries (RELIANCE)"
            value="₹2,750.00"
            change="-0.45%"
            isPositive={false}
            subtitle="O2C & Jio 5G Giga Complex"
          />
          <MetricCard
            title="Tata Motors (TATAMOTORS)"
            value="₹820.00"
            change="+1.12%"
            isPositive={true}
            subtitle="EV Market & JLR Fleet"
          />
        </div>
      </div>

      {/* Core Architectural Pillars */}
      <div>
        <h3 className="text-base font-bold text-obsidian-text mb-4">Architectural Integrity Principles</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-3">
            <div className="w-10 h-10 rounded-xl bg-gold/10 border border-gold/20 flex items-center justify-center text-gold">
              <Calculator className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-obsidian-text">Deterministic Calculations</h4>
            <p className="text-xs text-obsidian-secondary leading-relaxed">
              Language models are strictly forbidden from guessing numerical returns, indicators, or backtest results.
              All metrics are calculated in NumPy, pandas, and verified event-driven Python code.
            </p>
          </div>

          <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-3">
            <div className="w-10 h-10 rounded-xl bg-gold/10 border border-gold/20 flex items-center justify-center text-gold">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-obsidian-text">Traceable Citations</h4>
            <p className="text-xs text-obsidian-secondary leading-relaxed">
              Every material qualitative claim links back to authoritative regulatory filings, quarterly disclosures,
              and annual reports stored in pgvector with cryptographic content hashes.
            </p>
          </div>

          <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-3">
            <div className="w-10 h-10 rounded-xl bg-gold/10 border border-gold/20 flex items-center justify-center text-gold">
              <Activity className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-obsidian-text">Adversarial Critic Verification</h4>
            <p className="text-xs text-obsidian-secondary leading-relaxed">
              Before final assembly, an independent Verifier agent audits evidence coverage, data freshness,
              calculation consistency, and guarantees next-bar execution without look-ahead bias.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
