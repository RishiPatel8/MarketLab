import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { OverviewPage } from './pages/OverviewPage';
import { StockResearchPage } from './pages/StockResearchPage';
import { StrategyLabPage } from './pages/StrategyLabPage';
import { VirtualPortfolioPage } from './pages/VirtualPortfolioPage';
import { CompareStocksPage } from './pages/CompareStocksPage';
import { ResearchLibraryPage } from './pages/ResearchLibraryPage';
import { ExperimentHistoryPage } from './pages/ExperimentHistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { PrivacyPolicyPage } from './pages/PrivacyPolicyPage';
import { TermsPage } from './pages/TermsPage';
import { Footer } from './components/Footer';
import { InstrumentSearchModal } from './components/InstrumentSearchModal';
import { getHealth } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [researchPromptHint, setResearchPromptHint] = useState<string>('');
  const [systemReady, setSystemReady] = useState<boolean>(true);
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false);

  useEffect(() => {
    // Health check
    getHealth().then((res) => {
      setSystemReady(res.status === 'ready');
    }).catch(() => setSystemReady(false));

    // Keyboard shortcut Cmd+K or Ctrl+K for search
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleNavigate = (tab: string, promptHint?: string) => {
    if (promptHint) {
      setResearchPromptHint(promptHint);
    }
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectInstrumentFromSearch = (symbol: string) => {
    setResearchPromptHint(`Research ${symbol} for a six-month horizon`);
    setActiveTab('research');
  };

  return (
    <div className="flex h-screen w-screen bg-obsidian-bg text-obsidian-text overflow-hidden">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemReady={systemReady}
      />

      {/* Main Workspace Layout */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <Navbar
          onSearchClick={() => setIsSearchOpen(true)}
          systemReady={systemReady}
        />

        {/* Scrollable Page Body */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 flex flex-col justify-between">
          <div className="flex-1">
            {activeTab === 'overview' && (
              <OverviewPage onNavigate={handleNavigate} />
            )}
            {activeTab === 'research' && (
              <StockResearchPage initialPrompt={researchPromptHint} />
            )}
            {activeTab === 'strategy' && <StrategyLabPage />}
            {activeTab === 'portfolio' && <VirtualPortfolioPage />}
            {activeTab === 'compare' && <CompareStocksPage />}
            {activeTab === 'library' && <ResearchLibraryPage />}
            {activeTab === 'experiments' && <ExperimentHistoryPage />}
            {activeTab === 'settings' && <SettingsPage />}
            {activeTab === 'privacy' && <PrivacyPolicyPage onNavigate={handleNavigate} />}
            {activeTab === 'terms' && <TermsPage onNavigate={handleNavigate} />}
          </div>

          {/* Persistent Credible Footer with Legal Navigation */}
          <Footer onNavigate={handleNavigate} />
        </main>
      </div>

      {/* Global Quick Search Modal */}
      <InstrumentSearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onSelectInstrument={handleSelectInstrumentFromSearch}
      />
    </div>
  );
};

export default App;
