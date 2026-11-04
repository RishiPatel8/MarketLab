import React, { useState, useEffect } from 'react';
import {
  FileSearch,
  ArrowRight,
  Loader2,
  AlertTriangle,
  Building2,
  Calendar,
  Sparkles,
  RefreshCw,
  Search
} from 'lucide-react';
import { createResearch, getResearchStatus, getResearchReport } from '../services/api';
import { WorkflowStepper } from '../components/WorkflowStepper';
import { ReportViewer } from '../components/ReportViewer';
import { ResearchReport, Instrument } from '../types';
import { InstrumentSearchModal } from '../components/InstrumentSearchModal';
import { InstrumentTypeahead } from '../components/InstrumentTypeahead';

interface StockResearchPageProps {
  initialPrompt?: string;
}

export const StockResearchPage: React.FC<StockResearchPageProps> = ({ initialPrompt = '' }) => {
  const [question, setQuestion] = useState(initialPrompt || 'I want to invest ₹50,000 in Reliance Industries for six months. Analyze the stock, run multiple strategies, simulate different scenarios, and tell me whether the current price is suitable for entering.');
  const [horizonDays, setHorizonDays] = useState(180);
  const [investmentAmount, setInvestmentAmount] = useState(50000);
  const [horizonCategory, setHorizonCategory] = useState<'short_term' | 'medium_term' | 'long_term'>('medium_term');
  const [riskTolerance, setRiskTolerance] = useState<'conservative' | 'moderate' | 'aggressive'>('moderate');
  const [loading, setLoading] = useState(false);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<string>('planner');
  const [workflowStatus, setWorkflowStatus] = useState<string>('idle');
  const [errorMessage, setErrorMessage] = useState<string | undefined>();
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [clarificationCandidates, setClarificationCandidates] = useState<any[]>([]);
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);

  const handleSelectInstrument = (symbol: string, inst?: Instrument) => {
    setIsSearchModalOpen(false);
    if (inst) {
      const idDesc = inst.symbol || inst.nse_symbol || inst.bse_code || inst.id;
      const name = inst.canonical_name || inst.display_name || symbol;
      const newQ = `I want to invest ₹${investmentAmount.toLocaleString('en-IN')} in ${name} (${idDesc}) for a ${horizonDays}-day horizon with ${riskTolerance} risk. Analyze the stock, run multiple strategies, simulate different scenarios, and tell me whether the current price is suitable for entering.`;
      setQuestion(newQ);
    } else {
      setQuestion(`I want to invest ₹${investmentAmount.toLocaleString('en-IN')} in ${symbol} for a ${horizonDays}-day horizon with ${riskTolerance} risk.`);
    }
  };

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
          setClarificationCandidates(statusData.clarification_candidates || []);
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
      const res = await createResearch(
        q,
        undefined,
        horizonDays,
        investmentAmount,
        horizonCategory,
        riskTolerance
      );
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
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-2.5">
            <InstrumentTypeahead
              value={question}
              onChange={(val) => setQuestion(val)}
              onSelect={(inst) => {
                const prompt = `I want to invest ₹${investmentAmount.toLocaleString('en-IN')} in ${inst.company_name} (${inst.symbol}) for a ${horizonDays}-day horizon with ${riskTolerance} risk. Analyze the stock, run multiple strategies, simulate different scenarios, and tell me whether the current price is suitable for entering.`;
                setQuestion(prompt);
                handleLaunchResearch(prompt);
              }}
              placeholder="Type any Indian stock name, NSE/BSE symbol, or ISIN to get instant recommendations..."
              className="px-4 py-3 rounded-xl bg-obsidian-bg border border-obsidian-border text-sm text-obsidian-text focus:outline-none focus:border-gold transition-colors"
            />
            <button
              onClick={() => handleLaunchResearch()}
              disabled={loading}
              className="px-6 py-3 rounded-md copper-gloss-btn text-obsidian-bg font-bold text-sm flex items-center justify-center gap-2 transition-all disabled:opacity-50 shrink-0"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
              <span>{loading ? 'Executing...' : 'Run Analysis'}</span>
            </button>
          </div>

          {/* Investment Parameters Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-xl bg-obsidian-bg/80 border border-obsidian-border text-xs">
            <div>
              <label className="text-obsidian-muted block mb-1 font-medium">Investment Amount (INR)</label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-obsidian-muted font-semibold">₹</span>
                <input
                  type="number"
                  value={investmentAmount}
                  onChange={(e) => setInvestmentAmount(Number(e.target.value))}
                  step={5000}
                  min={1000}
                  className="w-full pl-7 pr-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold tabular-nums"
                />
              </div>
            </div>

            <div>
              <label className="text-obsidian-muted block mb-1 font-medium">Research Horizon</label>
              <select
                value={horizonDays}
                onChange={(e) => {
                  const days = Number(e.target.value);
                  setHorizonDays(days);
                  if (days <= 90) setHorizonCategory('short_term');
                  else if (days <= 180) setHorizonCategory('medium_term');
                  else setHorizonCategory('long_term');
                }}
                className="w-full px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold"
              >
                <option value={90}>Short-Term (90 Days / 3 Months)</option>
                <option value={180}>Medium-Term (180 Days / 6 Months)</option>
                <option value={365}>Long-Term (365 Days / 1 Year)</option>
              </select>
            </div>

            <div>
              <label className="text-obsidian-muted block mb-1 font-medium">Risk Tolerance Profile</label>
              <select
                value={riskTolerance}
                onChange={(e) => setRiskTolerance(e.target.value as any)}
                className="w-full px-3 py-1.5 rounded-lg bg-obsidian-card border border-obsidian-border text-xs text-obsidian-text focus:outline-none focus:border-gold"
              >
                <option value="conservative">Conservative (Capital Preservation)</option>
                <option value="moderate">Moderate (Balanced Risk/Reward)</option>
                <option value="aggressive">Aggressive (High Alpha Seeking)</option>
              </select>
            </div>
          </div>

          {/* Quick Prompts */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-obsidian-muted">Quick Presets:</span>
            <button
              onClick={() => {
                const masterPrompt = 'I want to invest ₹50,000 in Reliance Industries for six months. Analyze the stock, run multiple strategies, simulate different scenarios, and tell me whether the current price is suitable for entering.';
                setQuestion(masterPrompt);
                setInvestmentAmount(50000);
                setHorizonDays(180);
                setHorizonCategory('medium_term');
                setRiskTolerance('moderate');
                handleLaunchResearch(masterPrompt);
              }}
              className="px-3 py-1 rounded bg-gold/15 text-gold hover:bg-gold/25 border border-gold/40 flex items-center gap-1.5 font-bold transition-colors"
            >
              <Sparkles className="w-3.5 h-3.5 text-gold" />
              <span>₹50,000 Reliance (6 Months) Master Directive</span>
            </button>
            <button
              onClick={() => setIsSearchModalOpen(true)}
              className="px-2.5 py-1 rounded bg-obsidian-elevated text-obsidian-secondary hover:text-gold border border-obsidian-border flex items-center gap-1 transition-colors"
            >
              <Search className="w-3 h-3 text-gold" />
              <span>Browse 20,000+ Universe</span>
            </button>
            <button
              onClick={() => {
                const q = 'Research Orient Green Power for a six-month horizon';
                setQuestion(q);
                handleLaunchResearch(q);
              }}
              className="px-2.5 py-1 rounded bg-obsidian-elevated text-obsidian-secondary hover:text-gold border border-obsidian-border"
            >
              Orient Green Power
            </button>
            <button
              onClick={() => {
                const q = 'Analyze Tata Motors EV volume and leverage for long term';
                setQuestion(q);
                setHorizonDays(365);
                setHorizonCategory('long_term');
                handleLaunchResearch(q);
              }}
              className="px-2.5 py-1 rounded bg-obsidian-elevated text-obsidian-secondary hover:text-gold border border-obsidian-border"
            >
              Tata Motors (1 Year)
            </button>
            <button
              onClick={() => {
                setQuestion('Analyze Tata');
                handleLaunchResearch('Analyze Tata');
              }}
              className="px-2.5 py-1 rounded bg-obsidian-elevated text-market-warning hover:text-gold border border-market-warning/30"
            >
              Test Ambiguity ("Analyze Tata")
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
            {(clarificationCandidates.length > 0 ? clarificationCandidates : [
              { symbol: 'TATAMOTORS', company_name: 'Tata Motors Limited', sector: 'Automotive' },
              { symbol: 'TATASTEEL', company_name: 'Tata Steel Limited', sector: 'Metals & Mining' },
              { symbol: 'TATAPOWER', company_name: 'Tata Power Company Limited', sector: 'Electric Utilities' }
            ]).map((cand: any) => {
              const name = cand.company_name || cand.name || cand.symbol;
              const sym = cand.symbol;
              return (
                <button
                  key={sym}
                  onClick={() => {
                    const clarified = `I want to invest ₹${investmentAmount.toLocaleString('en-IN')} in ${name} (${sym}) for a ${horizonDays}-day horizon with ${riskTolerance} risk.`;
                    setQuestion(clarified);
                    handleLaunchResearch(clarified);
                  }}
                  className="p-4 rounded-xl bg-obsidian-bg hover:bg-obsidian-hover border border-obsidian-border hover:border-gold text-left transition-all group"
                >
                  <div className="font-bold text-sm text-obsidian-text group-hover:text-gold">{name}</div>
                  <div className="text-xs text-obsidian-muted mt-1">{cand.exchange || 'NSE'}:{sym} • {cand.sector || cand.instrument_type || 'Equity'}</div>
                  <span className="text-xs text-gold mt-2 block font-medium">Select This Instrument →</span>
                </button>
              );
            })}
          </div>
          <div className="pt-2 flex items-center justify-between border-t border-obsidian-border/50">
            <span className="text-xs text-obsidian-muted">Cannot find your entity above?</span>
            <button
              onClick={() => setIsSearchModalOpen(true)}
              className="text-xs text-gold font-semibold hover:underline flex items-center gap-1"
            >
              <span>Browse All 20,000+ Instruments</span> →
            </button>
          </div>
        </div>
      )}

      {/* Finalized Cited Report Viewer */}
      {report && <ReportViewer report={report} />}

      <InstrumentSearchModal
        isOpen={isSearchModalOpen}
        onClose={() => setIsSearchModalOpen(false)}
        onSelectInstrument={handleSelectInstrument}
        title="Select Any Instrument from the Indian Universe"
      />
    </div>
  );
};
