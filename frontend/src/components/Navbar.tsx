import React from 'react';
import { Search, Bell, Database, CheckCircle2, AlertCircle } from 'lucide-react';

interface NavbarProps {
  onSearchClick: () => void;
  systemReady: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onSearchClick, systemReady }) => {
  return (
    <header className="h-16 bg-obsidian-surface/80 backdrop-blur-md border-b border-obsidian-border px-8 flex items-center justify-between sticky top-0 z-20">
      {/* Quick Search Bar */}
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <button
          onClick={onSearchClick}
          className="w-full flex items-center gap-3 px-3.5 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-muted hover:border-obsidian-border-muted transition-colors text-left"
        >
          <Search className="w-4 h-4 text-obsidian-secondary" />
          <span>Search symbol e.g. GREENPOWER, RELIANCE, TATAMOTORS...</span>
          <kbd className="ml-auto px-1.5 py-0.5 rounded bg-obsidian-card border border-obsidian-border text-[10px] text-obsidian-secondary font-mono">
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Badges & System Diagnostics */}
      <div className="flex items-center gap-4">
        {/* Market Scope Badge */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-border text-xs text-obsidian-secondary">
          <span className="w-1.5 h-1.5 rounded-full bg-gold"></span>
          <span>NSE / BSE Indian Equities</span>
        </div>

        {/* Data Status Indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-border text-xs text-obsidian-secondary">
          <Database className="w-3.5 h-3.5 text-obsidian-muted" />
          <span>Validated Daily EOD</span>
          {systemReady ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-market-positive" />
          ) : (
            <AlertCircle className="w-3.5 h-3.5 text-market-warning" />
          )}
        </div>

        {/* Non-advisory Disclaimer Pill */}
        <span className="text-[11px] px-2.5 py-1 rounded bg-gold/10 text-gold border border-gold/20 font-medium">
          Decision Support
        </span>
      </div>
    </header>
  );
};
