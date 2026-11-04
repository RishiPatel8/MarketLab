import React, { useState, useEffect, useRef } from 'react';
import { Search, Loader2, Building2, TrendingUp, Layers, Check } from 'lucide-react';
import { Instrument } from '../types';
import { searchInstruments } from '../services/api';

interface InstrumentTypeaheadProps {
  value: string;
  onChange: (val: string) => void;
  onSelect: (instrument: Instrument) => void;
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
}

export const InstrumentTypeahead: React.FC<InstrumentTypeaheadProps> = ({
  value,
  onChange,
  onSelect,
  placeholder = "Search 20,000+ Indian stocks, ETFs, mutual funds (NSE & BSE)...",
  className = "",
  autoFocus = false
}) => {
  const [recommendations, setRecommendations] = useState<Instrument[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch recommendations as user types
  useEffect(() => {
    const trimmed = value.trim();
    if (!trimmed || trimmed.length < 1) {
      setRecommendations([]);
      setIsOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await searchInstruments(trimmed, 'ALL', 'ALL', 1, 8);
        setRecommendations(res.items || []);
        setIsOpen(res.items && res.items.length > 0);
        setHighlightedIndex(-1);
      } catch (err) {
        console.error('Typeahead search error:', err);
      } finally {
        setLoading(false);
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || recommendations.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev + 1) % recommendations.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev - 1 + recommendations.length) % recommendations.length);
    } else if (e.key === 'Enter') {
      if (highlightedIndex >= 0 && highlightedIndex < recommendations.length) {
        e.preventDefault();
        handleSelect(recommendations[highlightedIndex]);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  const handleSelect = (instrument: Instrument) => {
    onSelect(instrument);
    setIsOpen(false);
  };

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
      return <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-market-warning/10 text-market-warning border border-market-warning/30">BSE</span>;
    }
    if (exch === 'AMFI') {
      return <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-market-info/10 text-market-info border border-market-info/30">AMFI</span>;
    }
    return <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-obsidian-elevated text-obsidian-secondary border border-obsidian-border">NSE</span>;
  };

  return (
    <div ref={containerRef} className="relative flex-1">
      <div className="relative flex items-center">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => {
            if (recommendations.length > 0) setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className={`w-full ${className}`}
        />
        {loading && (
          <div className="absolute right-3.5 flex items-center pointer-events-none">
            <Loader2 className="w-4 h-4 text-gold animate-spin" />
          </div>
        )}
      </div>

      {/* Floating Recommendation Dropdown */}
      {isOpen && recommendations.length > 0 && (
        <div className="absolute left-0 right-0 top-full mt-1.5 bg-obsidian-card border border-obsidian-border rounded-xl shadow-2xl overflow-hidden z-50 divide-y divide-obsidian-border/30 max-h-80 overflow-y-auto">
          <div className="px-3 py-1.5 bg-obsidian-surface/90 border-b border-obsidian-border/40 flex items-center justify-between text-[11px] text-obsidian-muted font-mono">
            <span>RECOMMENDED INSTRUMENTS (OFFICIAL MASTER)</span>
            <span>Use ↑↓ to navigate • Enter to select</span>
          </div>
          {recommendations.map((inst, index) => {
            const isHighlighted = index === highlightedIndex;
            return (
              <div
                key={inst.id}
                onMouseDown={(e) => {
                  e.preventDefault();
                  handleSelect(inst);
                }}
                onMouseEnter={() => setHighlightedIndex(index)}
                className={`p-3 cursor-pointer flex items-center justify-between gap-3 transition-colors ${
                  isHighlighted ? 'bg-gold/15 border-l-2 border-gold' : 'hover:bg-obsidian-elevated'
                }`}
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-sm text-gold">
                      {inst.symbol}
                    </span>
                    {getExchangeBadge(inst.exchange)}
                    {getTypeBadge(inst.instrument_type)}
                    {inst.bse_code && (
                      <span className="text-[10px] font-mono text-obsidian-muted">
                        BSE: {inst.bse_code}
                      </span>
                    )}
                    {inst.scheme_code && (
                      <span className="text-[10px] font-mono text-obsidian-muted">
                        Scheme: {inst.scheme_code}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-obsidian-text truncate mt-0.5">
                    {inst.company_name}
                  </div>
                  {inst.isin && (
                    <div className="text-[10px] font-mono text-obsidian-muted">
                      ISIN: {inst.isin} {inst.plan_type ? `• Plan: ${inst.plan_type}` : ''} {inst.option_type ? `• Option: ${inst.option_type}` : ''}
                    </div>
                  )}
                </div>

                <div className="text-right shrink-0">
                  {inst.latest_nav ? (
                    <div>
                      <span className="text-xs font-mono font-bold text-market-positive">
                        NAV: ₹{inst.latest_nav.toFixed(2)}
                      </span>
                      <span className="block text-[10px] text-obsidian-muted">Official AMFI</span>
                    </div>
                  ) : (
                    <div>
                      <span className="text-[11px] font-mono text-obsidian-secondary">
                        {inst.status === 'ACTIVE' ? 'Active Listed' : inst.status}
                      </span>
                      <span className="block text-[10px] text-obsidian-muted font-mono">
                        {inst.exchange.includes('NSE') ? 'NSE Tradable' : 'BSE Tradable'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
