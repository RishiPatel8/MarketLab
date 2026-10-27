# MarketLab AI

> **AI-Powered Stock Research and Quantitative Strategy Validation Platform for Indian Equities**

[![Tests](https://img.shields.io/badge/tests-20%20passed-success)](scripts/run_tests.py)
[![Architecture](https://img.shields.io/badge/orchestrator-LangGraph-gold)](docs/ARCHITECTURE.md)
[![Database](https://img.shields.io/badge/storage-PostgreSQL%20%2B%20pgvector-blue)](docs/DATA_SOURCES.md)
[![Design](https://img.shields.io/badge/theme-Obsidian%20Gold-amber)](frontend/tailwind.config.js)
[![Compliance](https://img.shields.io/badge/SEBI-Non--Advisory%20Decision%20Support-lightgrey)](PRD.md)

---

## 1. Executive Summary

MarketLab AI is an agentic stock research and strategy backtesting platform tailored for publicly listed Indian equities (NSE & BSE).

Instead of relying on a generic chatbot to guess calculations or make unsupported predictions, MarketLab AI enforces a strict boundary between probabilistic LLM agent orchestration and deterministic quantitative execution:
1. **Instrument Resolution**: Resolves natural language queries (e.g., *"Research Orient Green Power for a six-month horizon"*) to authoritative identifiers (`NSE:GREENPOWER`), detecting ambiguity (e.g. distinguishing Tata Motors, Tata Steel, and Tata Power).
2. **Deterministic Math**: Metrics (Moving Averages, RSI, MACD, Volatility, Sharpe, Drawdown) and backtest mechanics (next-bar open execution, slippage, STT/brokerage fees) are executed strictly in verified Python code.
3. **Traceable Citations**: Qualitative assertions link directly to audited regulatory filings, annual reports, and corporate announcements stored in pgvector with SHA-256 content hashes.
4. **Adversarial Verification**: A Critic / Verification Agent audits evidence coverage, data freshness, and look-ahead bias before finalizing reports.
5. **Obsidian Gold SaaS Identity**: Clean, dark premium interface (`#09090B` background, `#D4AF37` gold accents) with tabular financial figures and responsive charts.

---

## 2. System Architecture

```mermaid
graph TD
    User([User / Browser]) <--> FE[React + TypeScript + Vite\nObsidian Gold Theme]
    FE <--> API[FastAPI Modular Monolith\nREST Endpoints]
    
    API <--> DB[(PostgreSQL + pgvector)]
    API <--> Redis[(Redis Broker / Cache)]
    
    API --> Worker[Async Background Worker\nTasks Runner]
    Worker <--> LG[LangGraph Orchestrator]
    
    subgraph Agentic Research Workflow
        LG --> Planner[Supervisor / Planner Node]
        LG --> MarketData[Market Data Ingestion Node]
        LG --> Filings[Financial Research Node]
        LG --> RAG[RAG Evidence Retrieval Node]
        LG --> Quant[Deterministic Quant Engine Node]
        LG --> Verifier[Critic Verification Audit Node]
        LG --> Reporter[Cited Report Assembly Node]
    end
    
    Quant --> QuantEngine[NumPy / pandas Backtester\nNext-Bar Open Execution]
    RAG --> VectorStore[pgvector Document Embeddings]
    n8n[n8n Automation Engine] -->|Authenticated API| API
```

---

## 3. Repository Structure

```
MarketLab/
├── .env.example                # Configured environment variables template
├── .gitignore                  # Git exclusions
├── docker-compose.yml          # Multi-container stack (Postgres, Redis, Backend, Worker, Frontend, n8n)
├── README.md                   # System documentation & setup guide
├── PRD.md                      # Product Requirements Document
├── docs/
│   ├── ARCHITECTURE.md         # Detailed architectural design & boundaries
│   ├── API.md                  # REST API contract and endpoint specifications
│   ├── DATA_SOURCES.md         # Market data licensing & governance for Indian equities
│   ├── EVALUATION.md           # Evaluation suite & adversarial quality gates
│   └── PRD.md                  # Architectural PRD copy
├── automation/
│   └── workflows/
│       ├── market_data_ingestion.json      # n8n scheduled Bhavcopy daily ingestion
│       ├── research_execution.json         # n8n authenticated research trigger
│       └── completion_notification.json    # n8n report completion alerts
├── backend/
│   ├── Dockerfile              # Backend container specification
│   ├── requirements.txt        # Pinned Python dependencies
│   ├── alembic.ini             # Database migration configuration
│   ├── app/
│   │   ├── main.py             # FastAPI entry point & lifespan handler
│   │   ├── api/v1/             # REST endpoints (research, instruments, experiments, documents, internal)
│   │   ├── core/               # Settings, security dependencies, logging, exceptions
│   │   ├── db/                 # SQLAlchemy models & repositories
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   ├── services/           # Quantitative engine, instrument resolver, market data, RAG
│   │   ├── providers/          # Market data adapters, LLM adapters (OpenAI, Gemini, Mock)
│   │   ├── agents/             # LangGraph state machine & specialized workflow nodes
│   │   ├── rag/                # Semantic chunker, embeddings, and vector retriever
│   │   └── worker/             # Background research execution engine
│   └── tests/                  # 20 automated pytest unit, integration, and AI eval tests
├── frontend/
│   ├── Dockerfile              # Production Nginx frontend container
│   ├── package.json            # Vite, React 18, Tailwind CSS, Lucide icons
│   ├── tailwind.config.js      # Obsidian Gold design token definitions
│   └── src/
│       ├── components/         # Navbar, Sidebar, MetricCard, WorkflowStepper, ReportViewer, EquityChart
│       ├── pages/              # Overview, Stock Research, Strategy Lab, Compare, Library, Experiments, Settings
│       └── services/           # Typed API service client
└── scripts/
    ├── seed_data.py            # Database initializer & instrument seeder
    └── run_tests.py            # Master test runner (Backend pytest + Frontend build)
```

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ and npm
- Docker and Docker Compose (for containerized deployment)

### 4.1 Running with Docker Compose
To start the entire platform (PostgreSQL with pgvector, Redis, FastAPI Backend, Background Worker, React Frontend, and n8n):
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Launch all services
docker-compose up --build
```
- **Web Application**: `http://localhost:3000`
- **FastAPI Swagger Docs**: `http://localhost:8000/docs`
- **n8n Automation Console**: `http://localhost:5678` (Credentials: `admin` / `marketlab_admin`)

### 4.2 Running Locally for Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 5. Verification & Test Suite

MarketLab AI includes a comprehensive test suite covering:
1. **Deterministic Indicators**: SMA, RSI, MACD, and Annualized Volatility calculations.
2. **Backtest Mechanics**: Moving average crossover execution, cash allocation, STT/brokerage fees, and execution slippage.
3. **Look-Ahead Bias Prevention**: Verification that signals generated at bar $t$ execute strictly at bar $t+1$ Open.
4. **Data Sanity & Anomaly Detection**: Rejecting negative prices, corrupted High/Low bounds, duplicate timestamps, and gaps.
5. **RAG Citations & Prompt Injection Defense**: Quarantining untrusted document text and ensuring SHA-256 hash traceability.
6. **AI Evaluation**: Ambiguous entity disambiguation (e.g. clarifying *"Tata"* into Tata Motors, Tata Steel, or Tata Power).

To run the master test runner:
```bash
python scripts/run_tests.py
```
Output:
```
============================================================
1. Running Backend Unit, Integration & AI Evaluation Tests...
============================================================
collected 20 items: 20 passed in 1.15s
[OK] Backend tests passed successfully!

============================================================
2. Verifying Frontend TypeScript Compilation and Production Bundle...
============================================================
✓ 1591 modules transformed.
dist/index.html                   1.22 kB
dist/assets/index-DX4iJ6rx.css   23.10 kB
dist/assets/index-BdeXRbbE.js   234.63 kB
[OK] Frontend build passed successfully!

============================================================
[SUCCESS] ALL TEST SUITES PASSED! MarketLab AI IS 100% OPERATIONAL.
```

---

## 6. n8n Automation Workflows

Import the pre-configured workflow JSON files in `automation/workflows/` directly into your n8n console (`http://localhost:5678`):
1. **`market_data_ingestion.json`**: Scheduled daily trigger at 16:30 IST calling `/api/v1/internal/ingestion-jobs` with authentication headers and retry backoff.
2. **`research_execution.json`**: Authenticated webhook trigger to queue research requests and log queue status.
3. **`completion_notification.json`**: Dispatches notifications with sentiment badges, executive summaries, risk factors, and citation links upon report completion.

---

## 7. Legal & Regulatory Disclaimer

**MarketLab AI is an evidence-backed decision-support and educational research tool.**
- It is **not** a SEBI-registered Investment Adviser, Research Analyst, or Portfolio Manager.
- It does **not** provide personalized financial advice, guarantee profitability, or execute live stock market orders.
- Historical backtest results reflect theoretical performance with specified fee and slippage assumptions; past performance is never a guarantee of future returns.
