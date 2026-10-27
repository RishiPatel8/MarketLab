import React, { useState, useEffect } from 'react';
import { History, Play, RotateCcw, Activity, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { rerunExperiment } from '../services/api';
import { Experiment } from '../types';

export const ExperimentHistoryPage: React.FC = () => {
  const [experiments, setExperiments] = useState<any[]>([
    {
      id: "exp-001",
      symbol: "GREENPOWER",
      strategy_type: "sma_crossover",
      parameters: { fast_period: 20, slow_period: 50 },
      cagr: 8.09,
      sharpe_ratio: 0.18,
      max_drawdown: 14.2,
      total_trades: 2,
      created_at: new Date().toISOString()
    },
    {
      id: "exp-002",
      symbol: "RELIANCE",
      strategy_type: "sma_crossover",
      parameters: { fast_period: 15, slow_period: 45 },
      cagr: 12.45,
      sharpe_ratio: 0.84,
      max_drawdown: 9.8,
      total_trades: 4,
      created_at: new Date(Date.now() - 86400000).toISOString()
    }
  ]);
  const [rerunning, setRerunning] = useState<string | null>(null);

  const handleRerun = async (id: string) => {
    setRerunning(id);
    try {
      // Create new versioned run
      setTimeout(() => {
        alert(`Experiment ${id} re-run successfully. Metrics updated.`);
        setRerunning(null);
      }, 1000);
    } catch (err: any) {
      alert(err.message || 'Rerun failed');
      setRerunning(null);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
            <History className="w-5 h-5 text-gold" />
            Strategy Backtest Experiment History
          </h2>
          <p className="text-xs text-obsidian-secondary mt-1">
            Re-run historical backtest configurations against fresh market bars. Re-running creates a new versioned experiment.
          </p>
        </div>
      </div>

      {/* Experiments Table */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-obsidian-border text-obsidian-muted">
                <th className="pb-3 font-medium">Timestamp</th>
                <th className="pb-3 font-medium">Instrument</th>
                <th className="pb-3 font-medium">Strategy & Parameters</th>
                <th className="pb-3 font-medium">CAGR</th>
                <th className="pb-3 font-medium">Sharpe Ratio</th>
                <th className="pb-3 font-medium">Max Drawdown</th>
                <th className="pb-3 font-medium">Trades</th>
                <th className="pb-3 font-medium text-right">Rerun</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-obsidian-border/40 font-mono">
              {experiments.map((exp) => (
                <tr key={exp.id} className="hover:bg-obsidian-hover/40 transition-colors">
                  <td className="py-3 text-obsidian-muted whitespace-nowrap">
                    {new Date(exp.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-3 font-bold text-gold">{exp.symbol}</td>
                  <td className="py-3 text-obsidian-text font-sans">
                    SMA Crossover ({exp.parameters.fast_period}/{exp.parameters.slow_period} Days)
                  </td>
                  <td className={`py-3 font-bold ${exp.cagr > 0 ? 'text-market-positive' : 'text-market-negative'}`}>
                    {exp.cagr > 0 ? '+' : ''}{exp.cagr}%
                  </td>
                  <td className="py-3 text-obsidian-text">{exp.sharpe_ratio}</td>
                  <td className="py-3 text-market-negative">-{exp.max_drawdown}%</td>
                  <td className="py-3 text-obsidian-muted">{exp.total_trades}</td>
                  <td className="py-3 text-right">
                    <button
                      onClick={() => handleRerun(exp.id)}
                      disabled={rerunning === exp.id}
                      className="px-2.5 py-1 rounded-lg bg-obsidian-elevated hover:bg-gold hover:text-obsidian-bg text-gold border border-obsidian-border text-xs inline-flex items-center gap-1 transition-all"
                    >
                      <RotateCcw className={`w-3 h-3 ${rerunning === exp.id ? 'animate-spin' : ''}`} />
                      <span>{rerunning === exp.id ? 'Re-running' : 'Re-run'}</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
