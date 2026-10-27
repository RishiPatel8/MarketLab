import React, { useState } from 'react';
import { Settings as SettingsIcon, Database, Cpu, Key, ShieldCheck, Save, Check } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [marketProvider, setMarketProvider] = useState('fixture');
  const [llmProvider, setLlmProvider] = useState('mock');
  const [openaiKey, setOpenaiKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
        <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-gold" />
          System Settings & Provider Configuration
        </h2>
        <p className="text-xs text-obsidian-secondary mt-1">
          Configure market data adapters, LLM orchestration providers, and automation credentials.
        </p>
      </div>

      {/* Market Data Provider Card */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-gold" />
          <h3 className="text-sm font-semibold text-obsidian-text">Market Data Provider Adapter</h3>
        </div>
        <p className="text-xs text-obsidian-secondary">
          Select data ingestion mode. Fixture mode uses audited daily historical bars for Indian equities; NSE/BSE adapter integrates official exchange APIs.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <label
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              marketProvider === 'fixture'
                ? 'bg-gold/10 border-gold text-obsidian-text'
                : 'bg-obsidian-bg border-obsidian-border text-obsidian-muted hover:border-obsidian-border-muted'
            }`}
          >
            <input
              type="radio"
              name="market_provider"
              value="fixture"
              checked={marketProvider === 'fixture'}
              onChange={() => setMarketProvider('fixture')}
              className="sr-only"
            />
            <div className="font-bold text-sm text-gold">Deterministic Fixture Mode (Offline)</div>
            <div className="text-xs text-obsidian-secondary mt-1">
              Deterministic historical series for GREENPOWER, RELIANCE, TATAMOTORS, INFY and Nifty 50.
            </div>
          </label>

          <label
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              marketProvider === 'nse_bse'
                ? 'bg-gold/10 border-gold text-obsidian-text'
                : 'bg-obsidian-bg border-obsidian-border text-obsidian-muted hover:border-obsidian-border-muted'
            }`}
          >
            <input
              type="radio"
              name="market_provider"
              value="nse_bse"
              checked={marketProvider === 'nse_bse'}
              onChange={() => setMarketProvider('nse_bse')}
              className="sr-only"
            />
            <div className="font-bold text-sm text-gold">NSE / BSE Live Adapter</div>
            <div className="text-xs text-obsidian-secondary mt-1">
              Direct connection to authorized Indian exchange Bhavcopy feeds with automatic rate limiting.
            </div>
          </label>
        </div>
      </div>

      {/* LLM Provider Card */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-gold" />
          <h3 className="text-sm font-semibold text-obsidian-text">LLM Orchestration Provider</h3>
        </div>
        <p className="text-xs text-obsidian-secondary">
          Select LLM backend for research planning, citation verification, and report synthesis.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {['mock', 'openai', 'gemini'].map((p) => (
            <label
              key={p}
              className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                llmProvider === p
                  ? 'bg-gold/10 border-gold text-obsidian-text'
                  : 'bg-obsidian-bg border-obsidian-border text-obsidian-muted'
              }`}
            >
              <input
                type="radio"
                name="llm_provider"
                value={p}
                checked={llmProvider === p}
                onChange={() => setLlmProvider(p)}
                className="sr-only"
              />
              <span className="font-bold text-xs uppercase text-gold block">{p} Mode</span>
              <span className="text-[11px] text-obsidian-secondary">
                {p === 'mock'
                  ? 'Deterministic offline testing'
                  : p === 'openai'
                  ? 'GPT-4o Mini structured adapter'
                  : 'Gemini 2.5 Flash adapter'}
              </span>
            </label>
          ))}
        </div>

        {llmProvider === 'openai' && (
          <div className="pt-2">
            <label className="text-xs text-obsidian-muted block mb-1">OpenAI API Key</label>
            <input
              type="password"
              placeholder="sk-..."
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold font-mono"
            />
          </div>
        )}

        {llmProvider === 'gemini' && (
          <div className="pt-2">
            <label className="text-xs text-obsidian-muted block mb-1">Google Gemini API Key</label>
            <input
              type="password"
              placeholder="AIzaSy..."
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold font-mono"
            />
          </div>
        )}
      </div>

      {/* Automation Credentials */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
        <div className="flex items-center gap-2">
          <Key className="w-4 h-4 text-gold" />
          <h3 className="text-sm font-semibold text-obsidian-text">Internal Automation & n8n Token</h3>
        </div>
        <p className="text-xs text-obsidian-secondary">
          Authorization secret used by n8n workflows for scheduled market ingestion and research execution.
        </p>
        <div className="p-3 rounded-xl bg-obsidian-bg border border-obsidian-border flex items-center justify-between font-mono text-xs text-obsidian-muted">
          <span>X-Internal-Token: ••••••••••••••••••••••••••••••••</span>
          <span className="text-gold font-sans font-medium text-[11px]">Active</span>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="px-6 py-2.5 rounded-xl bg-gold hover:bg-gold-hover text-obsidian-bg font-bold text-xs flex items-center gap-2 transition-all shadow-md"
        >
          {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          <span>{saved ? 'Saved Successfully' : 'Save Settings'}</span>
        </button>
      </div>
    </div>
  );
};
