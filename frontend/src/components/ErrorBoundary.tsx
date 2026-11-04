import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('MarketLab UI Uncaught Error:', error, errorInfo);
  }

  public handleReset = () => {
    this.setState({ hasError: false, error: undefined });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen w-screen bg-obsidian-bg text-obsidian-text flex items-center justify-center p-6">
          <div className="max-w-md w-full p-8 rounded-card bg-obsidian-card border border-gold/30 shadow-2xl space-y-5 text-center">
            <div className="w-12 h-12 rounded-xl bg-market-warning/15 border border-market-warning/30 flex items-center justify-center text-market-warning mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-obsidian-text tracking-tight">
                MarketLab AI Interface Interruption
              </h2>
              <p className="text-xs text-obsidian-secondary mt-1.5 leading-relaxed">
                An unexpected interface rendering issue occurred. Your data and backtests remain preserved on the backend server.
              </p>
            </div>
            {this.state.error && (
              <div className="p-3 rounded-lg bg-obsidian-bg border border-obsidian-border text-left">
                <span className="text-[10px] text-obsidian-muted block uppercase mb-1 font-mono">Error Detail</span>
                <p className="text-xs text-market-negative font-mono truncate">{this.state.error.message}</p>
              </div>
            )}
            <button
              onClick={this.handleReset}
              className="w-full py-2.5 rounded-xl bg-gold hover:bg-gold-hover text-obsidian-bg font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-md"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reload Workspace</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
