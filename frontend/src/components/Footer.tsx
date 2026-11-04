import React from 'react';
import { ShieldCheck, Database, Cpu, ExternalLink } from 'lucide-react';

interface FooterProps {
  onNavigate: (tab: string) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="mt-16 border-t border-obsidian-border bg-obsidian-surface/60 pt-10 pb-8 text-xs text-obsidian-secondary">
      <div className="max-w-6xl mx-auto px-4 space-y-8">
        {/* Top Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Column 1: Brand & Purpose */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-gold/15 border border-gold/30 flex items-center justify-center">
                <span className="font-mono font-bold text-xs text-gold">M</span>
              </div>
              <span className="font-bold text-sm text-obsidian-text tracking-tight">MarketLab AI</span>
            </div>
            <p className="text-[11px] text-obsidian-muted leading-relaxed">
              Evidence-grounded stock research and strategy validation for Indian equities. Separating deterministic math from probabilistic language models.
            </p>
          </div>

          {/* Column 2: Navigation */}
          <div className="space-y-2.5">
            <span className="font-semibold text-obsidian-text text-[11px] uppercase tracking-wider block">
              Workspace Modules
            </span>
            <ul className="space-y-1.5 text-[11px]">
              <li>
                <button
                  onClick={() => onNavigate('overview')}
                  className="hover:text-gold transition-colors text-left"
                >
                  Overview & Market Status
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('research')}
                  className="hover:text-gold transition-colors text-left"
                >
                  Stock Research Terminal
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('strategy')}
                  className="hover:text-gold transition-colors text-left"
                >
                  Strategy Lab & Backtest
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('library')}
                  className="hover:text-gold transition-colors text-left"
                >
                  Regulatory Filings Library
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('settings')}
                  className="hover:text-gold transition-colors text-left"
                >
                  Provider Integrations
                </button>
              </li>
            </ul>
          </div>

          {/* Column 3: Legal & Regulatory */}
          <div className="space-y-2.5">
            <span className="font-semibold text-obsidian-text text-[11px] uppercase tracking-wider block">
              Legal & Disclosures
            </span>
            <ul className="space-y-1.5 text-[11px]">
              <li>
                <button
                  onClick={() => onNavigate('privacy')}
                  className="hover:text-gold transition-colors text-left"
                >
                  Privacy Policy
                </button>
              </li>
              <li>
                <button
                  onClick={() => onNavigate('terms')}
                  className="hover:text-gold transition-colors text-left"
                >
                  Terms and Conditions
                </button>
              </li>
              <li>
                <a
                  href="https://www.nseindia.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-gold transition-colors inline-flex items-center gap-1"
                >
                  <span>NSE Official Portal</span>
                  <ExternalLink className="w-3 h-3 text-obsidian-muted" />
                </a>
              </li>
              <li>
                <a
                  href="https://www.bseindia.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-gold transition-colors inline-flex items-center gap-1"
                >
                  <span>BSE Corporate Disclosures</span>
                  <ExternalLink className="w-3 h-3 text-obsidian-muted" />
                </a>
              </li>
            </ul>
          </div>

          {/* Column 4: Operational Provenance */}
          <div className="space-y-2.5">
            <span className="font-semibold text-obsidian-text text-[11px] uppercase tracking-wider block">
              Active Technology Stack
            </span>
            <div className="space-y-2 text-[11px]">
              <div className="flex items-center gap-2 p-2 rounded bg-obsidian-card border border-obsidian-border">
                <Database className="w-3.5 h-3.5 text-gold shrink-0" />
                <span className="truncate">Market Data: Yahoo Finance (EOD Daily)</span>
              </div>
              <div className="flex items-center gap-2 p-2 rounded bg-obsidian-card border border-obsidian-border">
                <Cpu className="w-3.5 h-3.5 text-market-info shrink-0" />
                <span className="truncate">Synthesis: Google Gemini 3.5 Flash Lite</span>
              </div>
              <div className="flex items-center gap-2 p-2 rounded bg-obsidian-card border border-obsidian-border">
                <ShieldCheck className="w-3.5 h-3.5 text-market-positive shrink-0" />
                <span className="truncate">Embeddings: Gemini-Embedding-2 (3072d)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Regulatory & Research Disclaimer */}
        <div className="p-4 rounded-lg bg-obsidian-card/60 border border-obsidian-border/80 text-[11px] text-obsidian-muted leading-relaxed space-y-1.5">
          <p className="font-semibold text-obsidian-secondary">
            Statutory Research Notice and Limitation of Liability
          </p>
          <p>
            MarketLab AI is an evidence-backed quantitative stock research and historical strategy validation platform.
            The software is engineered exclusively for informational, analytical, and research decision support.
            MarketLab AI is not a registered investment adviser, broker-dealer, portfolio manager, or research analyst
            under the Securities and Exchange Board of India (SEBI) Regulations or any equivalent securities regulator.
          </p>
          <p>
            Deterministic quantitative calculations and historical backtests evaluate past market data and do not constitute
            guarantees of future performance. Market investments are subject to market risks. Users are solely responsible
            for evaluating investment hypotheses and should consult a licensed financial professional before making financial commitments.
          </p>
        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 border-t border-obsidian-border/50 text-[11px] text-obsidian-muted">
          <span>
            MarketLab AI. Built for evidence-backed financial research.
          </span>
          <div className="flex items-center gap-4">
            <button onClick={() => onNavigate('privacy')} className="hover:text-gold transition-colors">
              Privacy
            </button>
            <span>•</span>
            <button onClick={() => onNavigate('terms')} className="hover:text-gold transition-colors">
              Terms of Use
            </button>
            <span>•</span>
            <button onClick={() => onNavigate('settings')} className="hover:text-gold transition-colors">
              Diagnostics
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
};
