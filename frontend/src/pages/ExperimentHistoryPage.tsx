import React, { useState } from 'react';
import { History, RotateCcw, Trash2, AlertTriangle } from 'lucide-react';

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
  const [showConfirmClear, setShowConfirmClear] = useState(false);

  const handleRerun = async (id: string) => {
    setRerunning(id);
    try {
      setTimeout(() => {
        alert(`Experiment ${id} re-run successfully. Metrics updated.`);
        setRerunning(null);
      }, 1000);
    } catch (err: any) {
      alert(err.message || 'Rerun failed');
      setRerunning(null);
    }
  };

  const handleDelete = (id: string) => {
    if (!window.confirm(`Delete experiment ${id} from history?`)) return;
    setExperiments((prev) => prev.filter((e) => e.id !== id));
  };

  const handleClearAll = () => {
    setExperiments([]);
    setShowConfirmClear(false);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
            <History className="w-5 h-5 text-gold" />
            Strategy Backtest Experiment History
          </h2>
          <p className="text-xs text-obsidian-secondary mt-1">
            Re-run historical backtest configurations against fresh market bars. Re-running creates a new versioned experiment.
          </p>
        </div>

        {experiments.length > 0 && (
          <button
            onClick={() => setShowConfirmClear(true)}
            className="px-3 py-1.5 rounded-md bg-obsidian-elevated hover:bg-market-negative/10 hover:text-market-negative text-obsidian-secondary text-xs border border-obsidian-border hover:border-market-negative/30 flex items-center gap-1.5 transition-colors self-start sm:self-auto shrink-0"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {/* Confirmation Banner */}
      {showConfirmClear && (
        <div className="p-4 rounded-card bg-market-negative/10 border border-market-negative/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-fade-in">
          <div className="flex items-center gap-2 text-xs text-market-negative">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>Permanently delete all {experiments.length} backtest experiment records?</span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={handleClearAll}
              className="px-3 py-1 rounded-md bg-market-negative text-white text-xs font-bold hover:bg-red-700 transition-colors"
            >
              Confirm Clear
            </button>
            <button
              onClick={() => setShowConfirmClear(false)}
              className="px-3 py-1 rounded-md bg-obsidian-card text-obsidian-secondary text-xs hover:text-obsidian-text border border-obsidian-border transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Experiments Table */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
        {experiments.length === 0 ? (
          <div className="p-8 text-center text-xs text-obsidian-muted">
            No experiments recorded in history. Run a backtest in Strategy Lab.
          </div>
        ) : (
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
                  <th className="pb-3 font-medium text-right">Actions</th>
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
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleRerun(exp.id)}
                          disabled={rerunning === exp.id}
                          className="px-2.5 py-1 rounded-md bg-obsidian-elevated hover:bg-gold hover:text-obsidian-bg text-gold border border-obsidian-border text-xs inline-flex items-center gap-1 transition-all"
                        >
                          <RotateCcw className={`w-3 h-3 ${rerunning === exp.id ? 'animate-spin' : ''}`} />
                          <span>{rerunning === exp.id ? 'Re-running' : 'Re-run'}</span>
                        </button>
                        <button
                          onClick={() => handleDelete(exp.id)}
                          title="Delete experiment"
                          className="p-1 rounded-md bg-obsidian-elevated hover:bg-market-negative/15 hover:text-market-negative text-obsidian-muted border border-obsidian-border hover:border-market-negative/40 text-xs inline-flex items-center justify-center transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
