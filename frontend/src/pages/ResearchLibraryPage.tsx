import React, { useState, useEffect } from 'react';
import { Library, FileText, CheckCircle2, AlertTriangle, Clock, ArrowRight, Eye } from 'lucide-react';
import { listResearchRuns, getResearchReport } from '../services/api';
import { ResearchRunSummary, ResearchReport } from '../types';
import { ReportViewer } from '../components/ReportViewer';

export const ResearchLibraryPage: React.FC = () => {
  const [runs, setRuns] = useState<ResearchRunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<ResearchReport | null>(null);
  const [fetchingReport, setFetchingReport] = useState(false);

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    setLoading(true);
    const data = await listResearchRuns();
    setRuns(data);
    setLoading(false);
  };

  const handleOpenReport = async (runId: string) => {
    setFetchingReport(true);
    try {
      const rep = await getResearchReport(runId);
      setSelectedReport(rep);
    } catch (err: any) {
      alert(err.message || 'Report not yet available');
    } finally {
      setFetchingReport(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
            <Library className="w-5 h-5 text-gold" />
            Research Library & Historical Audits
          </h2>
          <p className="text-xs text-obsidian-secondary mt-1">
            Access previous research runs, inspect source citations, and re-examine deterministic calculations.
          </p>
        </div>
        <button
          onClick={loadRuns}
          className="px-3 py-1.5 rounded-xl bg-obsidian-elevated hover:bg-obsidian-hover text-obsidian-text text-xs border border-obsidian-border"
        >
          Refresh Library
        </button>
      </div>

      {/* Selected Report Modal or View */}
      {selectedReport && (
        <div className="p-6 rounded-card bg-obsidian-surface border border-gold/40 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-obsidian-border">
            <h3 className="font-bold text-sm text-gold">Viewing Archived Report: {selectedReport.report_id}</h3>
            <button
              onClick={() => setSelectedReport(null)}
              className="px-3 py-1 rounded-lg bg-obsidian-card hover:bg-obsidian-hover text-obsidian-text text-xs border border-obsidian-border"
            >
              Close Report
            </button>
          </div>
          <ReportViewer report={selectedReport} />
        </div>
      )}

      {/* Runs Table */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border">
        {loading ? (
          <div className="p-8 text-center text-xs text-obsidian-muted">Loading research library...</div>
        ) : runs.length === 0 ? (
          <div className="p-8 text-center text-xs text-obsidian-muted space-y-2">
            <FileText className="w-8 h-8 mx-auto text-obsidian-muted/40" />
            <p>No research reports recorded yet. Launch your first research in Stock Research.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-obsidian-border text-obsidian-muted">
                  <th className="pb-3 font-medium">Date</th>
                  <th className="pb-3 font-medium">Research Question</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium">Verification</th>
                  <th className="pb-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-obsidian-border/40">
                {runs.map((r) => {
                  const isComplete = r.status === 'completed' || r.status === 'completed_with_limitations';
                  return (
                    <tr key={r.id} className="hover:bg-obsidian-hover/40 transition-colors">
                      <td className="py-3 text-obsidian-muted font-mono whitespace-nowrap">
                        {new Date(r.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 font-medium text-obsidian-text max-w-md truncate">
                        "{r.research_question}"
                      </td>
                      <td className="py-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[11px] font-mono border ${
                            r.status === 'completed'
                              ? 'bg-market-positive/10 text-market-positive border-market-positive/20'
                              : r.status === 'completed_with_limitations'
                              ? 'bg-market-warning/10 text-market-warning border-market-warning/20'
                              : r.status === 'running'
                              ? 'bg-gold/10 text-gold border-gold/20'
                              : 'bg-obsidian-elevated text-obsidian-secondary border-obsidian-border'
                          }`}
                        >
                          {r.status}
                        </span>
                      </td>
                      <td className="py-3 text-obsidian-secondary">
                        {r.verification_status === 'verified' ? (
                          <span className="flex items-center gap-1 text-market-positive">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Verified
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-obsidian-muted">
                            <Clock className="w-3.5 h-3.5" /> {r.verification_status}
                          </span>
                        )}
                      </td>
                      <td className="py-3 text-right">
                        {isComplete ? (
                          <button
                            onClick={() => handleOpenReport(r.id)}
                            disabled={fetchingReport}
                            className="px-3 py-1 rounded-lg bg-obsidian-elevated hover:bg-gold hover:text-obsidian-bg text-gold border border-obsidian-border text-xs inline-flex items-center gap-1 transition-all"
                          >
                            <Eye className="w-3 h-3" />
                            <span>View Report</span>
                          </button>
                        ) : (
                          <span className="text-obsidian-muted text-xs">In Progress</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
