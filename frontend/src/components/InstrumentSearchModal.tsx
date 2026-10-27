import React, { useState, useEffect } from 'react';
import { Search, Building2, TrendingUp, X } from 'lucide-react';
import { Instrument } from '../types';
import { searchInstruments } from '../services/api';

interface InstrumentSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectInstrument: (symbol: string) => void;
}

export const InstrumentSearchModal: React.FC<InstrumentSearchModalProps> = ({
  isOpen,
  onClose,
  onSelectInstrument
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Instrument[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      const res = await searchInstruments(query);
      setResults(res);
      setLoading(false);
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-obsidian-bg/80 backdrop-blur-sm z-50 flex items-start justify-center pt-24 p-4">
      <div className="bg-obsidian-card border border-obsidian-border rounded-card max-w-lg w-full p-4 space-y-4 shadow-2xl">
        <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border">
          <Search className="w-4 h-4 text-obsidian-muted" />
          <input
            type="text"
            placeholder="Type company name or ticker (e.g. GREENPOWER, RELIANCE)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="w-full bg-transparent text-sm text-obsidian-text focus:outline-none placeholder:text-obsidian-muted"
          />
          <button onClick={onClose} className="text-obsidian-muted hover:text-obsidian-text">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto space-y-1 divide-y divide-obsidian-border/30">
          {loading && (
            <div className="p-4 text-center text-xs text-obsidian-muted">Searching Indian Equities...</div>
          )}
          {!loading && results.length === 0 && query && (
            <div className="p-4 text-center text-xs text-obsidian-muted">No instruments matched "{query}"</div>
          )}
          {!loading && results.length === 0 && !query && (
            <div className="p-3 text-xs text-obsidian-muted">
              Suggested: <span className="text-gold">GREENPOWER</span>, <span className="text-gold">RELIANCE</span>, <span className="text-gold">TATAMOTORS</span>, <span className="text-gold">INFY</span>
            </div>
          )}
          {results.map((inst) => (
            <button
              key={inst.id}
              onClick={() => {
                onSelectInstrument(inst.symbol);
                onClose();
              }}
              className="w-full text-left p-3 hover:bg-obsidian-hover rounded-xl flex items-center justify-between transition-colors group"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-obsidian-elevated flex items-center justify-center text-gold group-hover:bg-gold group-hover:text-obsidian-bg transition-colors">
                  <Building2 className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-obsidian-text">{inst.company_name}</h4>
                  <p className="text-xs text-obsidian-muted">{inst.exchange}:{inst.symbol} • {inst.industry || inst.sector || 'Equities'}</p>
                </div>
              </div>
              <span className="text-xs text-gold font-mono opacity-0 group-hover:opacity-100 transition-opacity">
                Select →
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
