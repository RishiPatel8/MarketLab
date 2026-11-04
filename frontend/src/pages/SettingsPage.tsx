import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Database, Cpu, Layers, RefreshCw, Check, AlertCircle, ShieldAlert } from 'lucide-react';
import { getSystemStatus, triggerReindex } from '../services/api';
import { SystemStatusResponse } from '../types';

export const SettingsPage: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatusResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [reindexMessage, setReindexMessage] = useState<string | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    const data = await getSystemStatus();
    setSystemStatus(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleReindex = async () => {
    setReindexing(true);
    setReindexMessage(null);
    try {
      const res = await triggerReindex();
      setReindexMessage(`Successfully re-indexed ${res.reindexed_count} chunks using ${res.model} (${res.dimension} dim) in ${res.duration_seconds}s.`);
      await fetchStatus();
    } catch (err: any) {
      setReindexMessage(`Re-indexing error: ${err.message}`);
    } finally {
      setReindexing(false);
    }
  };

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'REACHABLE':
      case 'VERIFIED':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-market-positive/10 text-market-positive border border-market-positive/30">
            {status}
          </span>
        );
      case 'CONFIGURED':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-market-info/10 text-market-info border border-market-info/30">
            {status}
          </span>
        );
      case 'MOCK':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-gold/10 text-gold border border-gold/30">
            MOCK / OFFLINE
          </span>
        );
      case 'BLOCKED':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-market-negative/10 text-market-negative border border-market-negative/30">
            BLOCKED
          </span>
        );
      case 'DEGRADED':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-market-warning/10 text-market-warning border border-market-warning/30">
            DEGRADED
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-obsidian-elevated text-obsidian-muted border border-obsidian-border">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
            <SettingsIcon className="w-5 h-5 text-gold" />
            System Integrations & Provider Observability
          </h2>
          <p className="text-xs text-obsidian-secondary mt-1">
            Real-time status of external market-data feeds, live LLM orchestration, and vector embedding collections.
          </p>
        </div>
        <button
          onClick={fetchStatus}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-obsidian-elevated hover:bg-obsidian-hover border border-obsidian-border text-xs text-gold flex items-center gap-1.5 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Health</span>
        </button>
      </div>

      {/* Market Data Provider Card */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-gold" />
            <h3 className="text-sm font-semibold text-obsidian-text">Market Data Feed</h3>
          </div>
          {systemStatus && renderStatusBadge(systemStatus.market_data.status)}
        </div>
        <p className="text-xs text-obsidian-secondary">
          Controls whether the platform ingests live historical bars via Yahoo Finance, direct exchange API feeds, or deterministic audited fixtures.
        </p>

        <div className="p-4 rounded-xl bg-obsidian-bg border border-obsidian-border space-y-2 text-xs">
          <div className="flex justify-between items-center">
            <span className="text-obsidian-muted">Active Ingestion Provider:</span>
            <span className="font-mono text-obsidian-text uppercase font-semibold">
              {systemStatus?.market_data.provider || 'Loading...'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-obsidian-muted">Data Latency Classification:</span>
            <span className="font-mono text-gold uppercase">
              {systemStatus?.market_data.latency_type || 'N/A'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-obsidian-muted">Diagnostics:</span>
            <span className="text-obsidian-secondary">
              {systemStatus?.market_data.message || 'No messages'}
            </span>
          </div>
        </div>

        <div className="p-3 rounded-xl bg-obsidian-elevated border border-obsidian-border text-[11px] text-obsidian-secondary">
          <span className="text-gold font-semibold">Switch Feed:</span> Set <code className="text-obsidian-text font-mono">MARKET_DATA_PROVIDER=yfinance</code> in <code className="text-obsidian-text font-mono">.env</code> for live historical NSE/BSE bars, or <code className="text-obsidian-text font-mono">fixture</code> for offline tests.
        </div>
      </div>

      {/* LLM Orchestrator Card */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-gold" />
            <h3 className="text-sm font-semibold text-obsidian-text">LLM Synthesis Provider</h3>
          </div>
          {systemStatus && renderStatusBadge(systemStatus.llm.status)}
        </div>
        <p className="text-xs text-obsidian-secondary">
          Orchestrates multi-agent research planning, source document verification, and evidence synthesis.
        </p>

        <div className="p-4 rounded-xl bg-obsidian-bg border border-obsidian-border space-y-2 text-xs">
          <div className="flex justify-between items-center">
            <span className="text-obsidian-muted">Configured Provider:</span>
            <span className="font-mono text-obsidian-text uppercase font-semibold">
              {systemStatus?.llm.provider || 'Loading...'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-obsidian-muted">Target Model:</span>
            <span className="font-mono text-gold">
              {systemStatus?.llm.model || 'N/A'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-obsidian-muted">Provider State:</span>
            <span className="text-obsidian-secondary">
              {systemStatus?.llm.message || 'No messages'}
            </span>
          </div>
        </div>

        <div className="p-3 rounded-xl bg-obsidian-elevated border border-obsidian-border text-[11px] text-obsidian-secondary">
          <span className="text-gold font-semibold">Live Mode Configuration:</span> Set <code className="text-obsidian-text font-mono">LLM_PROVIDER=gemini</code> and configure <code className="text-obsidian-text font-mono">GEMINI_API_KEY</code> in backend <code className="text-obsidian-text font-mono">.env</code>. Silent fallback to mock is forbidden in live mode.
        </div>
      </div>

      {/* Embeddings & Document Vector Store Card */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-gold" />
            <h3 className="text-sm font-semibold text-obsidian-text">Embedding Model & Document Vectors</h3>
          </div>
          {systemStatus && renderStatusBadge(systemStatus.embeddings.status)}
        </div>
        <p className="text-xs text-obsidian-secondary">
          Generates semantic dense vectors for company disclosures and performs similarity search in pgvector / SQLite.
        </p>

        <div className="p-4 rounded-xl bg-obsidian-bg border border-obsidian-border space-y-2 text-xs">
          <div className="flex justify-between items-center">
            <span className="text-obsidian-muted">Embedding Provider & Model:</span>
            <span className="font-mono text-obsidian-text font-semibold">
              {systemStatus?.embeddings.provider.toUpperCase()} ({systemStatus?.embeddings.model}, {systemStatus?.embeddings.dimensions} dims)
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-obsidian-muted">Indexed Documents:</span>
            <span className="font-mono text-gold">
              {systemStatus?.documents.total_documents} documents ({systemStatus?.documents.total_chunks} chunks)
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-obsidian-muted">Collection Vector Provenance:</span>
            <span className="font-mono text-obsidian-secondary">
              {systemStatus?.documents.mock_embedding_chunks} mock chunks | {systemStatus?.documents.real_embedding_chunks} real chunks
            </span>
          </div>
          {systemStatus?.documents.is_collection_mixed && (
            <div className="flex items-center gap-2 text-market-warning pt-1">
              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
              <span>Collection contains mixed mock and real embeddings. Re-index recommended.</span>
            </div>
          )}
        </div>

        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2">
          <div className="text-[11px] text-obsidian-muted">
            Re-indexes all stored document passages with the active embedding model.
          </div>
          <button
            onClick={handleReindex}
            disabled={reindexing}
            className="px-4 py-2 rounded-xl bg-gold hover:bg-gold-hover text-obsidian-bg font-bold text-xs flex items-center gap-2 transition-all disabled:opacity-50 shrink-0"
          >
            {reindexing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Layers className="w-3.5 h-3.5" />}
            <span>{reindexing ? 'Re-indexing...' : 'Rebuild Vector Index'}</span>
          </button>
        </div>

        {reindexMessage && (
          <div className="p-3 rounded-xl bg-obsidian-elevated border border-gold/40 text-xs text-gold">
            {reindexMessage}
          </div>
        )}
      </div>

      {/* Secret Safety Assurance */}
      <div className="p-4 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-muted flex items-start gap-2.5">
        <ShieldAlert className="w-4 h-4 text-gold shrink-0 mt-0.5" />
        <div>
          <span className="text-obsidian-text font-semibold block mb-0.5">Strict Security Assurance</span>
          API keys, tokens, and credentials are never transmitted to or displayed in the browser. Configure them securely in the backend <code className="text-gold font-mono">.env</code> file.
        </div>
      </div>
    </div>
  );
};
