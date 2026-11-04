import React from 'react';
import {
  Compass,
  FileSearch,
  Activity,
  Wallet,
  GitCompare,
  Library,
  History,
  Settings as SettingsIcon,
  ShieldCheck,
  TrendingUp
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  systemReady: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, systemReady }) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: Compass },
    { id: 'research', label: 'Stock Research', icon: FileSearch },
    { id: 'strategy', label: 'Strategy Lab', icon: Activity },
    { id: 'portfolio', label: 'Virtual Portfolio', icon: Wallet },
    { id: 'compare', label: 'Compare Stocks', icon: GitCompare },
    { id: 'library', label: 'Research Library', icon: Library },
    { id: 'experiments', label: 'Experiment History', icon: History },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-obsidian-surface border-r border-obsidian-border flex flex-col justify-between select-none">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-obsidian-border flex items-center gap-3">
          <div className="w-9 h-9 rounded-md copper-gloss-btn flex items-center justify-center text-obsidian-bg font-bold shadow-md">
            <TrendingUp className="w-5 h-5 text-obsidian-bg" />
          </div>
          <div>
            <h1 className="font-semibold text-base text-obsidian-text tracking-tight flex items-center gap-1.5">
              MarketLab <span className="text-gold font-bold">AI</span>
            </h1>
            <p className="text-xs text-obsidian-muted">Indian Equities Lab</p>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="p-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-obsidian-elevated text-gold border border-gold/30 shadow-sm'
                    : 'text-obsidian-secondary hover:text-obsidian-text hover:bg-obsidian-hover/60 border border-transparent'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-gold' : 'text-obsidian-muted'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer & Quick Legal */}
      <div className="p-3 space-y-2">
        <div className="p-3.5 rounded-md bg-obsidian-card border border-obsidian-border">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-obsidian-muted font-medium flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-gold" />
              Verification Engine
            </span>
            <span className="flex h-2 w-2 relative">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${systemReady ? 'bg-market-positive' : 'bg-market-warning'}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${systemReady ? 'bg-market-positive' : 'bg-market-warning'}`}></span>
            </span>
          </div>
          <p className="text-[11px] text-obsidian-secondary leading-relaxed">
            Deterministic python calculations with pgvector grounded citations.
          </p>
        </div>

        <div className="flex items-center justify-between px-2 text-[11px] text-obsidian-muted">
          <button
            onClick={() => setActiveTab('privacy')}
            className="hover:text-gold transition-colors"
          >
            Privacy
          </button>
          <span>•</span>
          <button
            onClick={() => setActiveTab('terms')}
            className="hover:text-gold transition-colors"
          >
            Terms
          </button>
          <span>•</span>
          <span className="font-mono text-[10px]">v1.0.0</span>
        </div>
      </div>
    </aside>
  );
};
