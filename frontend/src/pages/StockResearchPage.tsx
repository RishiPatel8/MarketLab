import React, { useState, useEffect } from 'react';
import {
  FileSearch,
  ArrowRight,
  Loader2,
  AlertTriangle,
  Building2,
  Calendar,
  Sparkles,
  RefreshCw
} from 'lucide-react';
import { createResearch, getResearchStatus, getResearchReport } from '../services/api';
import { WorkflowStepper } from '../components/WorkflowStepper';
import { ReportViewer } from '../components/ReportViewer';
import { ResearchReport } from '../types';

interface StockResearchPageProps {
  initialPrompt?: string;
}

export const StockResearchPage: React.FC<StockResearchPageProps> = ({ initialPrompt = '' }) => {
  const [question, setQuestion] = useState(initialPrompt || 'Research Orient Green Power for a six-month horizon');
  const [horizonDays, setHorizonDays] = useState(180);
  const [loading, setLoading] = useState(false);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<string>('planner');
  const [workflowStatus, setWorkflowStatus] = useState<string>('idle');
  const [errorMessage, setErrorMessage] = useState<string | undefined>();
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [clarificationCandidates, setClarificationCandidates] = useState<any[]>([]);

  useEffect(() => {
    if (initialPrompt) {
      setQuestion(initialPrompt);
    }
  }, [initialPrompt]);

  // Polling loop for active research run
  useEffect(() => {
    if (!activeRunId || (workflowStatus !== 'queued' && workflowStatus !== 'running')) return;

    const interval = setInterval(async () => {
      try {
        const statusData = await getResearchStatus(activeRunId);
        setCurrentStep(statusData.current_step);
        setWorkflowStatus(statusData.status);

        if (statusData.status === 'completed' || statusData.status === 'completed_with_limitations') {
          clearInterval(interval);
          setLoading(false);
          const rep = await getResearchReport(activeRunId);
          setReport(rep);
        } else if (statusData.status === 'needs_clarification') {
          clearInterval(interval);
          setLoading(false);
          setErrorMessage(statusData.error_message || 'Please clarify your company query.');
        } else if (statusData.status === 'failed') {
          clearInterval(interval);
          setLoading(false);
          setErrorMessage(statusData.error_message || 'Research run encountered an unrecoverable failure.');
        }
      } catch (err: any) {
        console.error('Polling error:', err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [activeRunId, workflowStatus]);

  const handleLaunchResearch = async (promptOverride?: string) => {
    const q = promptOverride || question;
    if (!q.trim()) return;

    setLoading(true);
    setReport(null);
    setErrorMessage(undefined);
    setClarificationCandidates([]);
    setCurrentStep('planner');
    setWorkflowStatus('running');

    try {
      const res = await createResearch(q, undefined, horizonDays);
      setActiveRunId(res.run_id);
    } catch (err: any) {
      setLoading(false);
      setWorkflowStatus('failed');
      setErrorMessage(err.message || 'Failed to initialize research execution');
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Workspace Header */}
      <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-obsidian-text flex items-center gap-2">
              <FileSearch className="w-5 h-5 text-gold" />
              Stock Research Workspace
            </h2>
            <p className="text-xs text-obsidian-secondary mt-1">
              Submit any stock query in natural language. The system resolves company identity, ingests regulatory filings,
              runs deterministic quantitative analysis, verifies evidence with a critic agent, and compiles a cited report.
            </p>
          </div>
        </div>

        {/* Input Form */}
        <div className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-2.5">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Research Orient Green Power for a six-month horizon..."
              className="flex-1 px-4 py-3 rounded-xl bg-obsidian-bg border border-obsidian-border text-sm text-obsidian-text focus:outline-none focus:border-gold transition-colors"
            />
            <div className="flex items-center gap-2">
              <select
                value={horizonDays}
                onChange={(e) => setHorizonDays(Number(e.target.value))}
                className="px-3 py-3 rounded-xl bg-obsidian-bg border border-obsidian-border text-xs text-obsidian-secondary focus:outline-none focus:border-gold"
              >
                <option value={90}>90 Days Horizon</option>
                <option value={180}>180 Days Horizon</option>
                <option value={365}>1 Year Horizon</option>
              </select>
              <button
                onClick={() => handleLaunchResearch()}
                disabled={loading}
                className="px-5 py-3 rounded-xl bg-gold hover:bg-gold-hover text-obsidian-bg font-bold text-sm flex items-center gap-2 transition-all disabled:opacity-50 shrink-0"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
                <span>{loading ? 'Executing...' : 'Start Research'}</span>
              </button>
            </div>
          </div>

          {/* Quick Prompts */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-obsidian-muted">Quick inputs:</span>
            <button
              onClick={() => {
                setQuestion('Research Orient Green Power for a six-month horizon');
                handleLaunchResearch('Research Orient Green Power for a six-month horizon');
              }}
              className="px-2 py-0.5 rounded bg-obsidian-elevated text-obsidian-secondary hover:text-gold border border-obsidian-border"
            >
              Orient Green Power (Renewable)
            </button>
            <button
              onClick={() => {
                setQuestion('Analyze Reliance Industries capital expenditure and margins');
                handleLaunchResearch('Analyze Reliance Industries capital expenditure and margins');
              }}
              className="px-2 py-0.5 rounded bg-obsidian-elevated text-obsidian-secondary hover:text-gold border border-obsidian-border"
            >
              Reliance Industries (Oil/Telecom)
            </button>
            <button
              onClick={() => {
                setQuestion('Analyze Tata Motors EV volume and leverage');
                handleLaunchResearch('Analyze Tata Motors EV volume and leverage');
              }}
              className="px-2 py-0.5 rounded bg-obsidian-elevated text-obsidian-secondary hover:text-gold border border-obsidian-border"
            >
              Tata Motors (Automotive)
            </button>
            <button
              onClick={() => {
                setQuestion('Analyze Tata');
                handleLaunchResearch('Analyze Tata');
              }}
              className="px-2 py-0.5 rounded bg-obsidian-elevated text-market-warning hover:text-gold border border-market-warning/30"
            >
              Test Ambiguity: "Analyze Tata"
            </button>
          </div>
        </div>
      </div>

      {/* Workflow Stepper State */}
      {workflowStatus !== 'idle' && (
        <WorkflowStepper
          currentStep={currentStep}
          status={workflowStatus}
          errorMessage={errorMessage}
        />
      )}

      {/* Clarification Handler If Ambiguous Company */}
      {workflowStatus === 'needs_clarification' && (
        <div className="p-6 rounded-card bg-obsidian-card border border-market-warning/40 space-y-4">
          <div className="flex items-center gap-2 text-market-warning">
            <AlertTriangle className="w-5 h-5" />
            <h3 className="font-bold text-sm">Company Name Resolution Clarification Required</h3>
          </div>
          <p className="text-xs text-obsidian-secondary">
            Multiple companies matched your search query. Please select the specific Indian equity instrument you wish to investigate:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { symbol: 'TATAMOTORS', name: 'Tata Motors Limited', sector: 'Automotive' },
              { symbol: 'TATASTEEL', name: 'Tata Steel Limited', sector: 'Metals & Mining' },
              { symbol: 'TATAPOWER', name: 'Tata Power Company Limited', sector: 'Electric Utilities' }
            ].map((cand) => (
              <button
                key={cand.symbol}
                onClick={() => {
                  const clarified = `Research ${cand.name} (${cand.symbol}) for a six-month horizon`;
                  setQuestion(clarified);
                  handleLaunchResearch(clarified);
                }}
                className="p-4 rounded-xl bg-obsidian-bg hover:bg-obsidian-hover border border-obsidian-border hover:border-gold text-left transition-all group"
              >
                <div className="font-bold text-sm text-obsidian-text group-hover:text-gold">{cand.name}</div>
                <div className="text-xs text-obsidian-muted mt-1">NSE:{cand.symbol} • {cand.sector}</div>
                <span className="text-xs text-gold mt-2 block font-medium">Select This Instrument →</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Finalized Cited Report Viewer */}
      {report && <ReportViewer report={report} />}
    </div>
  );
};
