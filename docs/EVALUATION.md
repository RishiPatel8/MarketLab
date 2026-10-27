# MarketLab AI — Evaluation Strategy & Quality Gates

MarketLab AI evaluates research and strategy validation on four rigorous dimensions:

## 1. Quantitative Correctness
- **Synthetic Test Fixtures**: Deterministic sequences with mathematically proven indicator outcomes (e.g., constant values, step functions, known sine waves).
- **Metric Verification**:
  - Exact match of SMA and EMA against reference formulas.
  - Verification of Sharpe and Sortino ratios against known risk-free rates.
  - Drawdown calculation verified on peak-to-trough series.
- **Look-Ahead Leakage Gate**: Assert that signal generation at bar $t$ uses information strictly available at or before bar $t$, and trade execution occurs at bar $t+1$ Open.

## 2. RAG Retrieval & Citation Precision
- **Citation Traceability**: 100% of factual financial statements in generated reports must map to retrieved chunk hashes and source documents.
- **Insufficient Evidence Handling**: When queries target unknown instruments, unlisted dates, or non-existent corporate filings, the system must emit an explicit "Insufficient Evidence" status rather than inventing disclosures.
- **Prompt Injection Defense**: Text extracted from ingested documents is quarantined in structured XML tags `<retrieved_evidence>` with instructions to the LLM to treat the content as untrusted data rather than system directives.

## 3. Workflow State Transition Gates
- LangGraph conditional edges verify:
  1. Instrument is resolved unambiguously.
  2. Market data passes sanity checks (no negative prices, valid OHLC relationships).
  3. Evidence verification critic scores the report above the verification threshold (evidence consistency >= 0.8, citation coverage >= 0.9).
  4. Bounded retry limit (maximum 2 retries) before marking run as `completed_with_limitations`.

## 4. Financial Non-Advisory Compliance
- All outputs contain standardized research disclaimers.
- No algorithmic advice, order placement, or guaranteed return claims.
