import React, { useState, useEffect } from 'react';
import { Search, Building2, Layers, Compass, TrendingUp, X, Filter, CheckCircle2, AlertCircle } from 'lucide-react';
import { Instrument } from '../types';
import { searchInstruments } from '../services/api';

interface InstrumentSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectInstrument: (symbol: string, instrument?: Instrument) => void;
  title?: string;
}

export const InstrumentSearchModal: React.FC<InstrumentSearchModalProps> = ({
  isOpen,
  onClose,
  onSelectInstrument,
  title = "Search Indian Equities, ETFs & Mutual Funds"
}) => {
  const [query, setQuery] = useState('');
  const [instrumentType, setInstrumentType] = useState('ALL');
  const [exchange, setExchange] = useState('ALL');
  const [results, setResults] = useState<Instrument[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  const fetchResults = async (q: string, type: string, exch: string) => {
    setLoading(true);
    const data = await searchInstruments(q, type, exch, 1, 25);
    setResults(data.items);
    setTotalCount(data.total);
    setHighlightedIndex(-1);
    setLoading(false);
  };

  useEffect(() => {
    if (!isOpen) return;

    const timer = setTimeout(() => {
      fetchResults(query, instrumentType, exchange);
    }, 120);

    return () => clearTimeout(timer);
  }, [query, instrumentType, exchange, isOpen]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (results.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev + 1) % results.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev - 1 + results.length) % results.length);
    } else if (e.key === 'Enter') {
      if (highlightedIndex >= 0 && highlightedIndex < results.length) {
        e.preventDefault();
        onSelectInstrument(results[highlightedIndex].symbol, results[highlightedIndex]);
        onClose();
      } else if (results.length > 0) {
        e.preventDefault();
        onSelectInstrument(results[0].symbol, results[0]);
        onClose();
      }
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  if (!isOpen) return null;

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'ETF':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-gold/15 text-gold border border-gold/30">ETF</span>;
      case 'MUTUAL_FUND':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-market-info/15 text-market-info border border-market-info/30">MUTUAL FUND</span>;
      case 'SME_EQUITY':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-market-warning/15 text-market-warning border border-market-warning/30">SME</span>;
      default:
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-obsidian-elevated text-obsidian-secondary border border-obsidian-border">EQUITY</span>;
    }
  };

  const getExchangeBadge = (exch: string) => {
    if (exch === 'NSE,BSE') {
      return <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-market-positive/10 text-market-positive border border-market-positive/30">NSE+BSE</span>;
    }
    if (exch === 'BSE') {
      return <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-market-warning/10 text-market-warning border border-market-warning/30">BSE ONLY</span>;
    }
    if (exch === 'AMFI') {
      return <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-market-info/10 text-market-info border border-market-info/30">AMFI NAV</span>;
    }
    return <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-obsidian-elevated text-obsidian-secondary border border-obsidian-border">NSE</span>;
  };

  return (
    <div className="fixed inset-0 bg-obsidian-bg/80 backdrop-blur-sm z-50 flex items-start justify-center pt-16 p-4">
      <div className="bg-obsidian-card border border-obsidian-border rounded-card max-w-2xl w-full p-5 space-y-4 shadow-2xl">
        {/* Modal Title Bar */}
        <div className="flex items-center justify-between pb-1 border-b border-obsidian-border/50">
          <span className="text-xs font-bold text-gold uppercase tracking-wider">{title}</span>
          <span className="text-[11px] text-obsidian-muted font-mono">{totalCount > 0 ? `${totalCount.toLocaleString()} matches` : 'NSE • BSE • AMFI Master'}</span>
        </div>

        {/* Search Input Bar */}
        <div className="flex items-center gap-3 px-3.5 py-2.5 rounded-md bg-obsidian-bg border border-obsidian-border">
          <Search className="w-4 h-4 text-gold shrink-0" />
          <input
            type="text"
            placeholder="Search by company name, NSE symbol, BSE code, ISIN, or mutual fund scheme..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
            className="w-full bg-transparent text-sm text-obsidian-text focus:outline-none placeholder:text-obsidian-muted"
          />
          {query && (
            <button onClick={() => setQuery('')} className="text-obsidian-muted hover:text-obsidian-text">
              <X className="w-4 h-4" />
            </button>
          )}
          <button onClick={onClose} className="text-obsidian-muted hover:text-obsidian-text pl-2 border-l border-obsidian-border">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Filter Toolbar */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-b border-obsidian-border/60 pb-3 text-xs">
          {/* Instrument Type Tabs */}
          <div className="flex items-center gap-1.5">
            {[
              { id: 'ALL', label: 'All Instruments' },
              { id: 'EQUITY', label: 'Stocks' },
              { id: 'ETF', label: 'ETFs' },
              { id: 'MUTUAL_FUND', label: 'Mutual Funds' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setInstrumentType(tab.id)}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                  instrumentType === tab.id
                    ? 'bg-gold text-obsidian-bg font-bold shadow-sm'
                    : 'bg-obsidian-elevated text-obsidian-secondary hover:text-obsidian-text'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Exchange Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-obsidian-muted text-[11px]">Exchange:</span>
            {[
              { id: 'ALL', label: 'All' },
              { id: 'NSE', label: 'NSE' },
              { id: 'BSE', label: 'BSE' }
            ].map((ex) => (
              <button
                key={ex.id}
                onClick={() => setExchange(ex.id)}
                className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
                  exchange === ex.id
                    ? 'bg-obsidian-border text-gold font-bold'
                    : 'text-obsidian-muted hover:text-obsidian-text'
                }`}
              >
                {ex.label}
              </button>
            ))}
          </div>
        </div>

        {/* Results Metadata Bar */}
        <div className="flex items-center justify-between text-xs text-obsidian-muted px-1">
          <span>
            {loading ? 'Searching universe...' : `Showing ${results.length} of ${totalCount} matching instruments`}
          </span>
          <span className="text-[11px]">
            Press Enter or click to select
          </span>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto space-y-1 divide-y divide-obsidian-border/20 pr-1">
          {loading && (
            <div className="p-8 text-center text-xs text-obsidian-muted">
              Scanning 20,000+ Indian stocks, ETFs, and mutual funds...
            </div>
          )}

          {!loading && results.length === 0 && (
            <div className="p-8 text-center space-y-2">
              <div className="text-sm font-semibold text-obsidian-text">No instruments matched your criteria</div>
              <p className="text-xs text-obsidian-muted max-w-sm mx-auto">
                Try searching by NSE symbol (e.g. <span className="text-gold">RELIANCE</span>), BSE code (e.g. <span className="text-gold">532215</span>), ISIN, or ETF name (e.g. <span className="text-gold">NIFTYBEES</span>).
              </p>
            </div>
          )}

          {!loading && results.map((inst) => (
            <button
              key={inst.id}
              onClick={() => {
                onSelectInstrument(inst.symbol, inst);
                onClose();
              }}
              className="w-full text-left p-3 hover:bg-obsidian-elevated/70 rounded-md flex items-center justify-between transition-colors group"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-8 h-8 rounded bg-obsidian-surface border border-obsidian-border flex items-center justify-center text-gold group-hover:border-gold/50 transition-colors shrink-0">
                  <Building2 className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-obsidian-text truncate group-hover:text-gold transition-colors">
                      {inst.company_name}
                    </h4>
                    {getTypeBadge(inst.instrument_type)}
                    {getExchangeBadge(inst.exchange)}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-obsidian-muted mt-1 font-mono">
                    <span className="text-gold font-bold">{inst.symbol}</span>
                    {inst.bse_code && <span>BSE:{inst.bse_code}</span>}
                    {inst.isin && <span>ISIN:{inst.isin}</span>}
                    {inst.latest_nav && (
                      <span className="text-market-positive font-bold">NAV: ₹{inst.latest_nav.toFixed(2)}</span>
                    )}
                    {inst.scheme_category && <span className="font-sans text-[11px] truncate max-w-xs">{inst.scheme_category}</span>}
                  </div>
                </div>
              </div>
              <div className="text-right shrink-0 pl-3">
                <span className="text-xs text-gold font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                  Select →
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
