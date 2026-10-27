# MarketLab AI — API Specification

All endpoints are versioned under `/api/v1/`.

## Base URLs
- Development: `http://localhost:8000/api/v1`
- Health check: `http://localhost:8000/health/live` and `/health/ready`

## Authentication
Requests must supply an API key in the `X-API-Key` header or an OAuth Bearer token in `Authorization: Bearer <token>`.
In Development/Demo mode with default settings, local requests authenticate with the developer default key.

---

## 1. Research Endpoints

### `POST /api/v1/research`
Initiates an asynchronous research workflow.
- **Request Body:**
  ```json
  {
    "question": "Research Orient Green Power for a six-month horizon",
    "symbol": "GREENPOWER",
    "exchange": "NSE",
    "horizon_days": 180,
    "include_technical": true,
    "include_fundamental": true,
    "include_rag": true
  }
  ```
- **Response (202 Accepted):**
  ```json
  {
    "run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "status": "queued",
    "message": "Research run queued successfully",
    "created_at": "2026-10-27T12:00:00Z"
  }
  ```

### `GET /api/v1/research/{run_id}`
Retrieves the execution status, current progress step, and summary.
- **Response (200 OK):**
  ```json
  {
    "run_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "status": "completed",
    "current_step": "report_generation",
    "progress_percentage": 100,
    "resolved_instrument": {
      "symbol": "GREENPOWER",
      "company_name": "Orient Green Power Company Limited",
      "exchange": "NSE"
    },
    "verification_status": "verified",
    "created_at": "2026-10-27T12:00:00Z",
    "completed_at": "2026-10-27T12:01:30Z"
  }
  ```

### `GET /api/v1/research/{run_id}/report`
Retrieves the complete cited research report and quantitative findings.
- **Response (200 OK):**
  Returns structured report markdown, evidence cards, citations list, financial facts, and limitation notices.

### `GET /api/v1/research`
Lists historical research runs with pagination and filtering.

---

## 2. Instruments & Market Data

### `GET /api/v1/instruments/search?q={query}`
Searches Indian equities by ticker symbol or company name.

### `GET /api/v1/instruments/{instrument_id}`
Returns authoritative metadata, exchange listing, sector, and industry.

### `GET /api/v1/instruments/{instrument_id}/market-data?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
Returns validated historical OHLCV bars, adjustments, and provider attribution.

---

## 3. Quantitative & Strategy Lab

### `POST /api/v1/experiments`
Runs a deterministic backtest on historical market data.
- **Request Body:**
  ```json
  {
    "instrument_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "strategy_type": "sma_crossover",
    "parameters": {
      "fast_period": 20,
      "slow_period": 50
    },
    "initial_capital": 100000.0,
    "transaction_fee_pct": 0.001,
    "slippage_pct": 0.0005,
    "benchmark_symbol": "^NSEI",
    "start_date": "2023-01-01",
    "end_date": "2025-12-31"
  }
  ```
- **Response (200 OK):**
  Returns performance metrics (CAGR, Sharpe, Max Drawdown, Win Rate), equity curves, trade logs, and look-ahead bias audit verification.

### `GET /api/v1/experiments/{experiment_id}`
Retrieves stored experiment configuration, trade series, and evaluation metrics.

### `POST /api/v1/experiments/{experiment_id}/rerun`
Creates a new versioned experiment run using the stored configuration.

---

## 4. Document Ingestion & RAG

### `POST /api/v1/documents/ingest`
Ingests an approved regulatory filing, quarterly statement, or announcement.
- **Request Body:** multipart/form-data or JSON with text, metadata (title, URL, publisher, date, instrument_id).
- **Response (201 Created):** Document ID and generated chunk count.

---

## 5. Automation & Internal Webhooks

### `POST /api/v1/internal/ingestion-jobs`
Triggered by n8n or scheduled cron jobs to update daily market bars and filing indexes. Protected by `X-Internal-Token`.

### `POST /api/v1/internal/automation-events`
Receives status updates and trigger responses from automated flows.
