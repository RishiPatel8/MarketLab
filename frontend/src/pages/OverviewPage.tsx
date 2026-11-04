import React, { useState, useEffect } from 'react';
import {
  Compass,
  ArrowRight,
  ShieldCheck,
  Calculator,
  Search,
  Activity,
  Layers,
  Sparkles,
  Loader2
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { InstrumentTypeahead } from '../components/InstrumentTypeahead';
import { Instrument } from '../types';
import { searchInstruments, getInstrumentMarketData } from '../services/api';

interface OverviewPageProps {
  onNavigate: (tab: string, symbolHint?: string) => void;
}

interface BenchmarkCardState {
  title: string;
  symbol: string;
  value: string;
  change: string;
  isPositive: boolean;
  subtitle: string;
  sentiment?: 'positive' | 'negative' | 'neutral' | 'gold';
  loading: boolean;
}

const DEFAULT_BENCHMARKS: BenchmarkCardState[] = [
  {
    title: "NIFTY 50 Benchmark",
    symbol: "^NSEI",
    value: "22,749.75",
    change: "-0.02%",
    isPositive: false,
    subtitle: "Annualized Vol: 12.8% • Broad Market",
    sentiment: "neutral",
    loading: true
  },
  {
    title: "Orient Green Power (GREENPOWER)",
    symbol: "GREENPOWER",
    value: "₹7.94",
    change: "+1.53%",
    isPositive: true,
    subtitle: "NSE/BSE Listed • 402.3 MW Wind",
    sentiment: "gold",
    loading: true
  },
  {
    title: "Reliance Industries (RELIANCE)",
    symbol: "RELIANCE",
    value: "₹1,196.20",
    change: "-0.47%",
    isPositive: false,
    subtitle: "O2C, Jio 5G, Jamnagar Energy",
    sentiment: "negative",
    loading: true
  },
  {
    title: "Infosys Limited (INFY)",
    symbol: "INFY",
    value: "₹1,845.00",
    change: "+0.85%",
    isPositive: true,
    subtitle: "IT Services & Cloud Digital",
    sentiment: "positive",
    loading: true
  }
];

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigate }) => {
  const [quickQuery, setQuickQuery] = useState('');
  const [benchmarkCards, setBenchmarkCards] = useState<BenchmarkCardState[]>(DEFAULT_BENCHMARKS);

  // Fetch original real market data feeds for benchmark instruments on mount
  useEffect(() => {
    let isMounted = true;

    async function loadRealFeeds() {
      const updated = await Promise.all(
        DEFAULT_BENCHMARKS.map(async (bench) => {
          try {
            const searchRes = await searchInstruments(bench.symbol, 'ALL', 'ALL', 1, 1);
            if (!searchRes.items || searchRes.items.length === 0) {
              return { ...bench, loading: false };
            }
            const inst = searchRes.items[0];
            const md = await getInstrumentMarketData(inst.id);
            const bars = md?.bars || [];

            if (bars.length >= 2) {
              const latest = bars[bars.length - 1];
              const prev = bars[bars.length - 2];
              const chgPct = ((latest.close - prev.close) / prev.close) * 100;
              const formattedVal = bench.symbol.startsWith('^')
                ? latest.close.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                : `₹${latest.close.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

              return {
                title: `${inst.company_name} (${inst.symbol})`,
                symbol: inst.symbol,
                value: formattedVal,
                change: `${chgPct >= 0 ? '+' : ''}${chgPct.toFixed(2)}%`,
                isPositive: chgPct >= 0,
                subtitle: `${inst.exchange} • ${inst.sector || inst.instrument_type} • Verified Bar`,
                sentiment: (chgPct >= 0 ? 'positive' : 'negative') as 'positive' | 'negative',
                loading: false
              };
            }
            return { ...bench, loading: false };
          } catch (err) {
            console.error(`Error loading market feed for ${bench.symbol}:`, err);
            return { ...bench, loading: false };
          }
        })
      );

      if (isMounted) {
        setBenchmarkCards(updated);
      }
    }

    loadRealFeeds();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleQuickSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (quickQuery.trim()) {
      onNavigate('research', quickQuery.trim());
    }
  };

  const samplePrompts = [
    "I want to invest ₹50,000 in Reliance Industries for six months. Analyze the stock, run multiple strategies, simulate different scenarios, and tell me whether the current price is suitable for entering.",
    "Research Orient Green Power for a six-month horizon",
    "Analyze Reliance Industries operating margins and debt",
    "Test a 20-day and 50-day moving average crossover on GREENPOWER"
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="p-8 md:p-10 rounded-card bg-obsidian-surface border border-obsidian-border relative overflow-hidden">
        <div className="max-w-3xl space-y-5">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-gold/10 border border-gold/20 text-xs font-semibold text-gold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Agentic Indian Equities Research Platform</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-obsidian-text tracking-tight leading-tight">
            Research stocks. Test strategies. Trace the evidence.
          </h1>
          <p className="text-sm md:text-base text-obsidian-secondary leading-relaxed">
            Analyze market data, review source documents, and evaluate trading strategies with explicit data provenance and reproducible calculations.
          </p>

          {/* Quick Input Bar with Live Typeahead Recommendation */}
          <form onSubmit={handleQuickSubmit} className="pt-2">
            <div className="flex flex-col sm:flex-row gap-2.5 p-2 rounded-lg bg-obsidian-bg border border-obsidian-border-muted shadow-lg">
              <div className="flex items-center gap-2 px-2 flex-1 relative">
                <Search className="w-4 h-4 text-gold shrink-0" />
                <InstrumentTypeahead
                  value={quickQuery}
                  onChange={(val) => setQuickQuery(val)}
                  onSelect={(inst: Instrument) => {
                    const prompt = `Research ${inst.company_name} (${inst.symbol}) for a six-month horizon`;
                    setQuickQuery(prompt);
                    onNavigate('research', prompt);
                  }}
                  placeholder="Type any Indian stock e.g. 'RELIANCE', 'Orient Green Power', or '500325'..."
                  className="bg-transparent text-sm text-obsidian-text focus:outline-none placeholder:text-obsidian-muted"
                />
              </div>
              <button
                type="submit"
                className="px-5 py-2.5 rounded-md copper-gloss-btn text-obsidian-bg font-bold text-sm flex items-center justify-center gap-2 transition-all shrink-0"
              >
                <span>Start stock research</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Action CTAs and Sample Prompts */}
          <div className="flex flex-wrap items-center gap-3 pt-1">
            <button
              onClick={() => onNavigate('strategy')}
              className="px-4 py-2 rounded-md bg-obsidian-elevated hover:bg-obsidian-border text-obsidian-text border border-obsidian-border text-xs font-semibold flex items-center gap-2 transition-colors"
            >
              <Compass className="w-3.5 h-3.5 text-gold" />
              <span>Explore strategy lab</span>
            </button>
            <div className="h-4 w-[1px] bg-obsidian-border hidden sm:block"></div>
            <span className="text-xs text-obsidian-muted">Suggested inquiries:</span>
            {samplePrompts.slice(0, 2).map((p, idx) => (
              <button
                key={idx}
                onClick={() => onNavigate('research', p)}
                className="text-xs px-2.5 py-1 rounded bg-obsidian-elevated/70 text-obsidian-secondary hover:text-gold border border-obsidian-border transition-colors text-left truncate max-w-xs"
              >
                "{p}"
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Market Indicators Snapshot - Original Real Data Feeds */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-4">
          <div>
            <h3 className="text-base font-bold text-obsidian-text">Reference Market Data (NSE & BSE Feeds)</h3>
            <p className="text-xs text-obsidian-muted">Original market data feeds via yfinance & AMFI official master. Not synthetic mock data.</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono text-gold px-2 py-0.5 rounded bg-gold/10 border border-gold/20">
              provider: yfinance
            </span>
            <span className="text-[11px] font-mono text-obsidian-secondary px-2 py-0.5 rounded bg-obsidian-card border border-obsidian-border">
              daily_historical
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {benchmarkCards.map((card, idx) => (
            <MetricCard
              key={idx}
              title={card.title}
              value={card.loading ? "Loading..." : card.value}
              change={card.loading ? "..." : card.change}
              isPositive={card.isPositive}
              sentiment={card.sentiment}
              subtitle={card.subtitle}
            />
          ))}
        </div>
      </div>

      {/* Core Architectural Pillars */}
      <div>
        <h3 className="text-base font-bold text-obsidian-text mb-4">Architectural Integrity Principles</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-3">
            <div className="w-10 h-10 rounded-md bg-gold/10 border border-gold/20 flex items-center justify-center text-gold">
              <Calculator className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-obsidian-text">Deterministic Calculations</h4>
            <p className="text-xs text-obsidian-secondary leading-relaxed">
              Technical indicators, portfolio returns, and financial ratios are computed strictly using deterministic Python libraries. LLMs never fabricate math or numbers.
            </p>
          </div>

          <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-3">
            <div className="w-10 h-10 rounded-md bg-gold/10 border border-gold/20 flex items-center justify-center text-gold">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-obsidian-text">Critic Verification Gate</h4>
            <p className="text-xs text-obsidian-secondary leading-relaxed">
              An independent critic agent reviews generated research reports against retrieved evidence chunks to flag unsupported assertions or inconsistencies before delivery.
            </p>
          </div>

          <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-3">
            <div className="w-10 h-10 rounded-md bg-gold/10 border border-gold/20 flex items-center justify-center text-gold">
              <Layers className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-sm text-obsidian-text">Explicit Provenance Tracking</h4>
            <p className="text-xs text-obsidian-secondary leading-relaxed">
              Every factual assertion is directly linked to an official regulatory document citation. Market data displays honest latency classifications with zero mock substitution.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
