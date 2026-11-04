# MarketLab AI — System Architecture

## 1. System Overview

MarketLab AI is an agentic stock research and strategy validation platform designed for Indian equities. It enforces a strict boundary between probabilistic LLM agent orchestration and deterministic quantitative execution.

```mermaid
graph TD
    User([User / Browser]) <--> FE[React + Vite Frontend\nObsidian Gold Theme]
    FE <--> API[FastAPI Application\nModular Monolith]
    
    API <--> DB[(PostgreSQL + pgvector)]
    API <--> Redis[(Redis Broker / Cache)]
    
    API --> Worker[Async Research Worker / Engine]
    Worker <--> LG[LangGraph Orchestrator]
    
    subgraph Agentic Workflow
        LG --> Supervisor[Supervisor / Planner Node]
        LG --> MarketNode[Market Data Node]
        LG --> DocNode[Financial Doc Node]
        LG --> RAGNode[RAG Evidence Node]
        LG --> QuantNode[Deterministic Quant Node]
        LG --> CriticNode[Verification / Critic Node]
        LG --> ReportNode[Report Generator Node]
    end
    
    QuantNode --> QuantEngine[Deterministic Quant & Backtest Engine\nNumPy / Pandas]
    RAGNode --> VectorStore[pgvector Document Embeddings]
    MarketNode --> MarketAdapters[Market Data Provider Adapters]
    DocNode --> DocAdapters[Filings & Regulatory Source Adapters]
    
    n8n[n8n Automation Engine] -->|Authenticated API| API
```

## 2. Core Architectural Principles

1. **No LLM Hallucinated Calculations**: LLMs interpret intent, formulate research plans, coordinate nodes, and synthesize narratives. All numerical indicators (SMA, EMA, RSI, MACD, Sharpe, Drawdown) and backtest mechanics (fill price, slippage, brokerage, cash balance) are calculated exclusively in deterministic Python code.
2. **Compact Graph State**: Large OHLCV series and bulk text are stored in database records or memory caches. LangGraph state carries instrument metadata, references, validated metrics, and retrieved evidence snippets.
3. **Traceable Citations**: Every factual claim in the generated research report must reference an ingested document with source identifier, timestamp, publication date, and page/section where available.
4. **Adversarial Verification**: Before any research report is finalized, a Critic / Verification agent checks source freshness, calculation consistency, benchmark appropriateness, and look-ahead bias risk.
5. **Obsidian Gold SaaS Aesthetics**: Dark mode palette (#09090B background, #111114 surface, #18181B cards, #D4AF37 gold accents) optimized for financial readability with tabular figures and responsive layout.

## 3. Component Details

### 3.1 Backend Architecture (`backend/app/`)
- `api/v1/`: REST endpoints for research, market data, instruments, experiments, documents, and health checks.
- `core/`: Application settings (Pydantic Settings), security (API keys, JWT), logging, and custom exceptions.
- `db/models/`: SQLAlchemy 2.0 ORM models for instruments, market bars, financial facts, documents, chunks, research runs, reports, experiments, and automation events.
- `db/repositories/`: Data access layer separating database operations from business logic.
- `schemas/`: Pydantic models for strict request/response validation and LangGraph typed state.
- `providers/`:
  - `market_data/`: Provider abstraction (`BaseMarketDataProvider`) with fixture fallback and Indian equities adapters (NSE/BSE).
  - `llm/`: Configurable LLM adapter (OpenAI, Gemini, or Mock for deterministic testing).
  - `document_source/`: Ingestion for exchange disclosures, annual reports, and investor filings.
- `agents/`: LangGraph state machine with typed state, dedicated workflow nodes (`planner`, `market_data`, `financial_research`, `rag`, `quantitative`, `verifier`, `report`), prompts, and structured output parsers.
- `rag/`: Text chunker, embedding generator, pgvector retriever, and evaluation harness.
- `worker/`: Background job execution engine for long-running research runs and backtests.

### 3.2 Required Quantitative, Research, and Simulation Engines

1. **Market Data Engine (`backend/app/services/market_data_service.py`)**:
   - Authoritative NSE/BSE resolution, daily OHLCV candles, corporate actions (splits, dividends), and financial fundamentals.
   - Rigorous data validation: high/low sanity checks, duplicate timestamp pruning, and truthful latency tagging (`daily_historical` vs `fixture`).

2. **Fundamental Analysis Engine (`backend/app/analytics/fundamental_engine.py`)**:
   - Deterministic Discounted Cash Flow (DCF) model with WACC vs Terminal Growth sensitivity matrix.
   - 3-Stage DuPont ROE Decomposition: Net Profit Margin × Asset Turnover × Financial Leverage.
   - Comprehensive ratio synthesis: P/E, P/B, Debt/Equity, Operating Margin, and ROCE.

3. **Technical Analysis Engine (`backend/app/analytics/technical_engine.py`)**:
   - Trend indicators: SMA (20, 50, 200), EMA (9, 21, 50, 200), Multi-timeframe trend alignment.
   - Momentum & Oscillators: RSI(14), MACD (12, 26, 9) + Histogram, ADX(14).
   - Volatility & Range: Bollinger Bands (20, 2σ, %B, Bandwidth), ATR(14).
   - Execution & Levels: Cumulative VWAP, Classical Floor Pivots (P, S1-S3, R1-R3), and 20-day swing support/resistance.

4. **Strategy Engine & Registry (`backend/app/analytics/strategy_engine.py`)**:
   - 10 registered quantitative algorithms: `sma_crossover`, `ema_crossover`, `rsi_threshold`, `macd_momentum`, `bollinger_bands`, `mean_reversion`, `momentum_breakout`, `volume_breakout`, `fundamental_value`, and `risk_parity`.
   - Multi-Strategy Consensus Engine: Executes the 10-algorithm ensemble and aggregates votes into an actionable consensus rating (BUY/HOLD/SELL/INSUFFICIENT_EVIDENCE) with percentage agreement.

5. **Backtesting Engine (`backend/app/services/quantitative_engine.py`)**:
   - Historical replay with strict next-bar Open execution to eliminate look-ahead bias.
   - Explicit Indian market friction: 0.1% STT/brokerage fees and 0.05% slippage deductions.
   - Out-of-sample partitioning and benchmark alpha calculation against NIFTY 50 (`^NSEI`).

6. **Virtual Investment Environment (`backend/app/services/portfolio_service.py`)**:
   - Risk-free paper trading: Virtual portfolio creation, cash balances, and position averaging.
   - Simulated order routing: BUY/SELL market and limit orders with cash overdraft rejection.
   - Mark-to-market valuations and real-time realized/unrealized P&L calculations.
   - What-If Scenario Stress Testing: Simulates systemic market shocks (-15% correction, +20% rally, etc.) without contacting real brokerages.

7. **Risk & Decision Intelligence Engine (`backend/app/analytics/decision_engine.py`)**:
   - Synthesizes technical, fundamental, and consensus findings into BUY, HOLD, SELL, or INSUFFICIENT_EVIDENCE ratings.
   - Formulates potential entry price bands, DCF fair-value ranges, 2.0x ATR downside stop-loss levels, and probabilistic Bull/Base/Bear scenario projections.
   - Mandates SEBI non-advisory compliance notices on all outputs.

### 3.3 Frontend Architecture (`frontend/src/`)
- React 18 with TypeScript and Vite.
- Tailwind CSS configured with the Obsidian Gold design system.
- Modules:
  - **Overview**: Market snapshot, real data feeds, natural language entry bar.
  - **Stock Research**: Interactive research workspace, capital/horizon/risk selectors, stage stepper, cited report viewer with Decision Intelligence cards.
  - **Strategy Lab**: Dual-mode workbench with single strategy deep dives (all 10 algorithms) and 10-model multi-strategy consensus matrix.
  - **Virtual Portfolio**: Complete paper trading dashboard with KPI metrics, simulated order console, open holdings mark-to-market table, and what-if stress tests.
  - **Compare Stocks**: Side-by-side financial and technical comparison.
  - **Research Library**: Historical research reports with verified citation inspection.
  - **Experiment History**: Re-runnable strategy backtests with audit trails.
  - **Settings**: Provider keys, demo mode toggles, risk parameters.
