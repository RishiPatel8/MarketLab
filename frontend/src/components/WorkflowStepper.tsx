import React from 'react';
import {
  Compass,
  Database,
  FileText,
  Search,
  Calculator,
  ShieldCheck,
  CheckCircle2,
  Clock,
  AlertTriangle,
  XCircle,
  Loader2
} from 'lucide-react';

interface Step {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
}

const STEPS: Step[] = [
  { id: 'planner', name: 'Request Interpretation', icon: Compass },
  { id: 'market_data_retrieval', name: 'Market Data Ingestion', icon: Database },
  { id: 'financial_research', name: 'Regulatory Filings', icon: FileText },
  { id: 'rag_evidence_retrieval', name: 'RAG Evidence Retrieval', icon: Search },
  { id: 'quantitative_analysis', name: 'Deterministic Quant Toolchain', icon: Calculator },
  { id: 'verification', name: 'Critic Verification Audit', icon: ShieldCheck },
  { id: 'report_generation', name: 'Cited Report Assembly', icon: CheckCircle2 },
];

interface WorkflowStepperProps {
  currentStep: string;
  status: string;
  errorMessage?: string;
}

export const WorkflowStepper: React.FC<WorkflowStepperProps> = ({ currentStep, status, errorMessage }) => {
  const currentIndex = STEPS.findIndex((s) => s.id === currentStep);

  return (
    <div className="p-6 rounded-card bg-obsidian-card border border-obsidian-border mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-obsidian-text flex items-center gap-2">
            Agentic Research Workflow (LangGraph)
            {status === 'running' && (
              <span className="flex items-center gap-1.5 text-xs text-gold font-normal px-2 py-0.5 rounded bg-gold/10 border border-gold/20">
                <Loader2 className="w-3 h-3 animate-spin" /> In Progress
              </span>
            )}
            {status === 'completed' && (
              <span className="flex items-center gap-1.5 text-xs text-market-positive font-normal px-2 py-0.5 rounded bg-market-positive/10 border border-market-positive/20">
                <CheckCircle2 className="w-3 h-3" /> Verified Completed
              </span>
            )}
            {status === 'completed_with_limitations' && (
              <span className="flex items-center gap-1.5 text-xs text-market-warning font-normal px-2 py-0.5 rounded bg-market-warning/10 border border-market-warning/20">
                <AlertTriangle className="w-3 h-3" /> Completed with Limitations
              </span>
            )}
            {status === 'needs_clarification' && (
              <span className="flex items-center gap-1.5 text-xs text-market-warning font-normal px-2 py-0.5 rounded bg-market-warning/10 border border-market-warning/20">
                <AlertTriangle className="w-3 h-3" /> Clarification Required
              </span>
            )}
            {status === 'failed' && (
              <span className="flex items-center gap-1.5 text-xs text-market-negative font-normal px-2 py-0.5 rounded bg-market-negative/10 border border-market-negative/20">
                <XCircle className="w-3 h-3" /> Execution Halted
              </span>
            )}
          </h3>
          <p className="text-xs text-obsidian-secondary mt-0.5">
            Strictly bounded execution graph. Deterministic calculations are separated from LLM generation.
          </p>
        </div>
      </div>

      {/* Stepper bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
        {STEPS.map((step, idx) => {
          const Icon = step.icon;
          const isDone = status === 'completed' || status === 'completed_with_limitations' || idx < currentIndex;
          const isCurrent = idx === currentIndex && status === 'running';
          const isFailed = idx === currentIndex && (status === 'failed' || status === 'needs_clarification');

          let cardStyle = 'border-obsidian-border bg-obsidian-bg text-obsidian-muted';
          let iconStyle = 'text-obsidian-muted';

          if (isDone) {
            cardStyle = 'border-market-positive/30 bg-market-positive/5 text-obsidian-text';
            iconStyle = 'text-market-positive';
          } else if (isCurrent) {
            cardStyle = 'border-gold bg-gold/10 text-gold shadow-sm gold-glow-sm';
            iconStyle = 'text-gold';
          } else if (isFailed) {
            cardStyle = 'border-market-warning bg-market-warning/10 text-market-warning';
            iconStyle = 'text-market-warning';
          }

          return (
            <div
              key={step.id}
              className={`p-3 rounded-xl border flex flex-col justify-between transition-all ${cardStyle}`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-obsidian-muted">0{idx + 1}</span>
                {isDone ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-market-positive" />
                ) : isCurrent ? (
                  <Loader2 className="w-3.5 h-3.5 text-gold animate-spin" />
                ) : isFailed ? (
                  <AlertTriangle className="w-3.5 h-3.5 text-market-warning" />
                ) : (
                  <Clock className="w-3.5 h-3.5 text-obsidian-muted/50" />
                )}
              </div>
              <div className="flex items-center gap-2">
                <Icon className={`w-3.5 h-3.5 shrink-0 ${iconStyle}`} />
                <span className="text-[11px] font-medium leading-tight">{step.name}</span>
              </div>
            </div>
          );
        })}
      </div>

      {errorMessage && (
        <div className="mt-4 p-3 rounded-xl bg-market-negative/10 border border-market-negative/20 text-xs text-market-negative flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Notice:</p>
            <p>{errorMessage}</p>
          </div>
        </div>
      )}
    </div>
  );
};
