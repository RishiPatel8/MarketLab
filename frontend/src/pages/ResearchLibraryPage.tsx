import React, { useState, useEffect } from 'react';
import { Library, FileText, CheckCircle2, Clock, Eye, Trash2, RefreshCw, AlertTriangle } from 'lucide-react';
import { listResearchRuns, getResearchReport, deleteResearchRun, clearAllResearchRuns } from '../services/api';
import { ResearchRunSummary, ResearchReport } from '../types';
import { ReportViewer } from '../components/ReportViewer';

export const ResearchLibraryPage: React.FC = () => {
  const [runs, setRuns] = useState<ResearchRunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<ResearchReport | null>(null);
  const [fetchingReport, setFetchingReport] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [showConfirmClear, setShowConfirmClear] = useState(false);
  const [clearingAll, setClearingAll] = useState(false);

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

  const handleDeleteRun = async (runId: string) => {
    if (!window.confirm('Delete this research run from library?')) return;
    setDeletingId(runId);
    try {
      await deleteResearchRun(runId);
      setRuns((prev) => prev.filter((item) => item.id !== runId));
      if (selectedReport?.run_id === runId) {
        setSelectedReport(null);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to delete research run');
    } finally {
      setDeletingId(null);
    }
  };

  const handleClearAll = async () => {
    setClearingAll(true);
    try {
      await clearAllResearchRuns();
      setRuns([]);
      setSelectedReport(null);
      setShowConfirmClear(false);
    } catch (err: any) {
      alert(err.message || 'Failed to clear research library');
    } finally {
      setClearingAll(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
            <Library className="w-5 h-5 text-gold" />
            Research Library & Historical Audits
          </h2>
          <p className="text-xs text-obsidian-secondary mt-1">
            Access previous research runs, inspect source citations, and re-examine deterministic calculations.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={loadRuns}
            disabled={loading}
            className="px-3 py-1.5 rounded-md bg-obsidian-elevated hover:bg-obsidian-hover text-obsidian-text text-xs border border-obsidian-border flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-gold ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Library</span>
          </button>

          {runs.length > 0 && (
            <button
              onClick={() => setShowConfirmClear(true)}
              disabled={clearingAll}
              className="px-3 py-1.5 rounded-md bg-obsidian-elevated hover:bg-market-negative/10 hover:text-market-negative text-obsidian-secondary text-xs border border-obsidian-border hover:border-market-negative/30 flex items-center gap-1.5 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>
          )}
        </div>
      </div>

      {/* Confirmation Banner for Clear All */}
      {showConfirmClear && (
        <div className="p-4 rounded-card bg-market-negative/10 border border-market-negative/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-fade-in">
          <div className="flex items-center gap-2 text-xs text-market-negative">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>Permanently delete all {runs.length} historical research records and cached reports?</span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={handleClearAll}
              disabled={clearingAll}
              className="px-3 py-1 rounded-md bg-market-negative text-white text-xs font-bold hover:bg-red-700 transition-colors"
            >
              {clearingAll ? 'Deleting...' : 'Confirm Clear'}
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

      {/* Selected Report Modal or View */}
      {selectedReport && (
        <div className="p-6 rounded-card bg-obsidian-surface border border-gold/40 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-obsidian-border">
            <h3 className="font-bold text-sm text-gold">Viewing Archived Report: {selectedReport.report_id}</h3>
            <button
              onClick={() => setSelectedReport(null)}
              className="px-3 py-1 rounded-md bg-obsidian-card hover:bg-obsidian-hover text-obsidian-text text-xs border border-obsidian-border"
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
                  const isDeleting = deletingId === r.id;

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
                        <div className="flex items-center justify-end gap-1.5">
                          {isComplete ? (
                            <button
                              onClick={() => handleOpenReport(r.id)}
                              disabled={fetchingReport}
                              className="px-2.5 py-1 rounded-md bg-obsidian-elevated hover:bg-gold hover:text-obsidian-bg text-gold border border-obsidian-border text-xs inline-flex items-center gap-1 transition-all"
                            >
                              <Eye className="w-3 h-3" />
                              <span>View Report</span>
                            </button>
                          ) : (
                            <span className="text-obsidian-muted text-xs mr-2">In Progress</span>
                          )}

                          <button
                            onClick={() => handleDeleteRun(r.id)}
                            disabled={isDeleting}
                            title="Delete this record"
                            className="p-1 rounded-md bg-obsidian-elevated hover:bg-market-negative/15 hover:text-market-negative text-obsidian-muted border border-obsidian-border hover:border-market-negative/40 text-xs inline-flex items-center justify-center transition-colors"
                          >
                            <Trash2 className={`w-3.5 h-3.5 ${isDeleting ? 'animate-pulse' : ''}`} />
                          </button>
                        </div>
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
