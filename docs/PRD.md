# MarketLab AI
## Product Requirements Document (PRD)

**Version:** 1.0  
**Status:** Proposed — Ready for technical planning  
**Product type:** AI-powered stock research and strategy validation platform  
**Initial market:** Indian equities  
**Primary use case:** Evidence-backed stock research and historical strategy testing

---

## 1. Executive Summary

MarketLab AI is an agentic stock-market research platform that helps users investigate publicly listed companies, evaluate investment hypotheses, and validate trading strategies using real market data and documented evidence.

Instead of providing a generic chatbot response to a question such as “Should I buy Orient Green Power?”, MarketLab AI executes a structured research workflow.

The system identifies the company, retrieves available market data and financial documents, performs quantitative analysis, consults relevant research through Retrieval-Augmented Generation (RAG), checks the quality of its evidence, and generates a research report with citations, risks, assumptions, and limitations.

The platform also allows users to express trading strategies in natural language and test them through a deterministic backtesting engine.

### Product vision

Build a transparent AI research assistant that explains not only what the evidence suggests, but also how the conclusion was reached, which data supports it, and what could invalidate it.

### Core differentiator

MarketLab AI does not rely on an LLM to invent financial calculations or make unsupported predictions. Language models coordinate the research process and explain the results, while dedicated Python services calculate metrics and validate historical experiments.

---

## 2. Problem Statement

Individual investors and independent researchers often face several challenges:

- Financial information is scattered across market feeds, company filings, financial statements, and news sources.
- Understanding financial ratios, technical indicators, valuation, and business risks requires significant research.
- Generic AI chatbots may use outdated information, omit citations, or produce unsupported conclusions.
- Backtests can appear profitable because of look-ahead bias, survivorship bias, unrealistic transaction costs, or data leakage.
- Comparing different investment hypotheses requires repeatable experiments and consistent evaluation.
- Manually monitoring companies and reviewing updated reports is time-consuming.

MarketLab AI addresses these problems through a coordinated, auditable research workflow.

---

## 3. Goals and Non-Goals

### 3.1 Product goals

1. Convert natural-language stock questions into structured research plans.
2. Retrieve current or appropriately timestamped market data and authoritative company information.
3. Provide quantitative analysis using deterministic calculations.
4. Use RAG to retrieve relevant documents and provide traceable citations.
5. Coordinate specialized agents through LangGraph.
6. Evaluate historical trading hypotheses using realistic backtesting assumptions.
7. Detect incomplete, inconsistent, stale, or insufficient evidence.
8. Generate readable reports with supporting evidence, opposing evidence, risks, and limitations.
9. Automate recurring research tasks using n8n.
10. Provide a reproducible history of research runs.

### 3.2 Non-goals for the initial release

- Executing real stock-market orders.
- Guaranteeing profits or predicting future prices with certainty.
- Replacing a registered financial adviser.
- Providing personalized investment advice or claiming suitability without the necessary regulated process.
- Supporting every global stock exchange.
- Building a proprietary foundation model.
- Training an LLM from scratch.
- Using reinforcement learning as a prerequisite for the first release.

---

## 4. Target Users

### Primary users

**Retail investors**
- Want to research a stock before making their own decisions.
- Need an understandable explanation of financial and technical information.
- Want to compare bullish and bearish evidence.

**Quantitative finance learners**
- Want to express strategy ideas in natural language.
- Need reproducible backtests, benchmark comparisons, and performance metrics.

**Independent financial researchers**
- Need source-backed company research and saved experiment histories.
- Want to automate repeated analysis.

### Initial user persona

A user asks: “I want to research Orient Green Power for a six-month investment horizon.”

The user expects a structured research report, not merely a conversational opinion. The report should show what information was available, which calculations were performed, the relevant risks, and where uncertainty remains.

---

## 5. Core Product Use Cases

### Use case A: Research a stock

**Input:** “Analyze Orient Green Power and help me understand whether it merits further research.”

Expected workflow:
1. Resolve the company and exchange listing.
2. Retrieve available price history and financial information.
3. Retrieve relevant filings, announcements, and industry material.
4. Calculate relevant financial and technical metrics.
5. Compare evidence supporting and opposing the research thesis.
6. Validate sources, timestamps, and calculations.
7. Generate a cited research report.

### Use case B: Test a trading hypothesis

**Input:** “Test a 20-day and 50-day moving-average crossover strategy on a defined universe of Indian equities.”

Expected workflow:
1. Parse the strategy into a structured specification.
2. Ask for missing parameters or disclose explicit defaults.
3. Retrieve and validate historical data.
4. Run the strategy in the deterministic backtesting engine.
5. Include transaction costs and a suitable benchmark.
6. Evaluate out-of-sample performance.
7. Generate performance charts and a reproducible report.

### Use case C: Compare two companies

**Input:** “Compare two renewable-energy companies based on financial performance, valuation, leverage, and business risks.”

Expected workflow:
1. Resolve both companies.
2. Retrieve comparable reporting periods and metrics.
3. Identify missing or non-comparable information.
4. Compare the available evidence.
5. Explain meaningful differences and uncertainty.
6. Produce a side-by-side report with source citations.

### Use case D: Automate recurring research

**Input:** A user saves a research task and requests a weekly refresh.

Expected workflow:
1. n8n triggers the scheduled workflow.
2. FastAPI validates the request.
3. MarketLab AI refreshes the available data.
4. Agents run the relevant analysis.
5. The report is saved and compared with the previous run.
6. A notification is sent if configured conditions are met.

---

## 6. Product Scope

### MVP — Must-have features

- Stock search and company resolution.
- Natural-language research requests.
- Structured research-plan generation.
- Market data ingestion and validation.
- Basic company and financial analysis.
- Technical indicators and historical performance metrics.
- Document retrieval and RAG with citations.
- LangGraph-based agent orchestration.
- Deterministic Python calculation services.
- Research verification and failure handling.
- Report generation.
- Experiment and report history.
- Basic dashboard and visualizations.
- Docker Compose deployment.
- Automated tests and structured logging.

### Phase 2 — Advanced research

- Multi-company comparisons.
- More valuation metrics and financial statement analysis.
- Advanced strategy testing and walk-forward evaluation.
- Parameter sensitivity and market-regime analysis.
- Saved watchlists and scheduled research.
- n8n notifications and automated report delivery.
- Improved document ingestion and retrieval evaluation.

### Phase 3 — Expansion

- Additional markets and data providers.
- More sophisticated portfolio-level analysis.
- Expanded financial document coverage.
- Advanced experiment comparison and collaboration.
- More extensive monitoring, access controls, and production operations.

---

## 7. Functional Requirements

### FR-01: Stock identification

The system shall accept company names, ticker symbols, and supported exchange identifiers.

Requirements:
- Resolve the company to an authoritative instrument identifier.
- Handle ambiguous company names.
- Display the exchange and symbol used.
- Ask for clarification when multiple instruments match.
- Never silently substitute a different company.

**Acceptance criteria:** An ambiguous or unresolved stock request does not proceed to company-specific analysis until the identity is sufficiently established.

### FR-02: Natural-language request interpretation

The system shall convert user requests into structured research specifications.

A research specification may contain:
- Instrument or company identifiers.
- Research objective.
- Investment horizon, if supplied.
- Requested analysis categories.
- Historical date range, where applicable.
- Benchmark.
- Strategy parameters.
- Cost assumptions.
- Required evidence sources.

The specification shall distinguish user-provided parameters from system defaults.

**Acceptance criteria:** Valid requests produce schema-validated specifications. Missing essential information triggers clarification or a clearly disclosed default where appropriate.

### FR-03: Market data ingestion

The system shall retrieve supported market data through configured data providers.

Supported data may include:
- Historical open, high, low, close, and volume.
- Adjusted price data where available and appropriate.
- Corporate actions where supported.
- Instrument metadata.
- Data timestamps and provider attribution.

The ingestion service shall detect missing dates, duplicate rows, invalid values, unexpected gaps, and inconsistent price records.

**Acceptance criteria:** Invalid data is rejected or explicitly flagged. The system does not silently treat missing values as valid market observations.

### FR-04: Company research

The system shall retrieve available company information from approved sources, such as:
- Exchange filings and corporate announcements.
- Published financial statements and annual reports.
- Official company disclosures.
- Relevant industry and policy publications.

It shall distinguish reported facts from calculated metrics and LLM-generated interpretations.

**Acceptance criteria:** Material factual claims in the report include supporting citations when the source is available.

### FR-05: Financial analysis

The analysis service shall calculate supported financial metrics from validated source data.

Potential metrics include:
- Revenue and earnings growth.
- Operating margins.
- Debt and leverage measures.
- Cash flow.
- Return on equity and return on capital, where inputs support them.
- Valuation ratios, where reliable inputs are available.

The system shall display the reporting period and relevant calculation definitions.

**Acceptance criteria:** Missing or incomparable financial inputs produce an unavailable or qualified result, not an invented value.

### FR-06: Technical analysis

The system shall support common indicators, including:
- Simple and exponential moving averages.
- RSI.
- MACD.
- Historical returns.
- Volatility.
- Maximum drawdown.
- Trading volume analysis.

Indicators shall be calculated in code from validated market data.

**Acceptance criteria:** Indicator values are reproducible from the stored data, calculation parameters, and specified timestamp.

### FR-07: RAG research engine

The RAG pipeline shall:
1. Ingest approved documents.
2. Extract text and metadata.
3. Split documents into meaningful chunks.
4. Generate embeddings.
5. Store embeddings and metadata in a vector database.
6. Retrieve relevant passages for research questions.
7. Return source identifiers, document dates, and page or section information where available.
8. Ground report claims in retrieved evidence.

The initial implementation should use PostgreSQL with pgvector, subject to deployment constraints.

**Acceptance criteria:** Retrieved passages can be traced to their source documents. The system reports insufficient evidence rather than fabricating citations.

### FR-08: Agent orchestration

LangGraph shall coordinate the research workflow.

The graph shall support:
- Request interpretation.
- Research planning.
- Parallel market and document research where appropriate.
- Tool execution.
- Result aggregation.
- Independent verification.
- Bounded retries.
- Error and timeout handling.
- Report generation.

Agents must use explicit inputs and outputs. They shall not be allowed to invent or overwrite authoritative market data.

**Acceptance criteria:** Each run records the stages executed, tool results or references, failures, and final status.

### FR-09: Quantitative strategy testing

The platform shall provide a deterministic backtesting engine separate from LLM orchestration.

The initial strategy shall be a moving-average crossover strategy with configurable parameters.

The engine shall support:
- Entry and exit rules.
- Position and capital assumptions.
- Benchmark comparison.
- Transaction costs and slippage assumptions.
- Chronological training and test periods.
- Out-of-sample evaluation.
- Reproducible configuration and results.

The engine must prevent future information from being used to make past trading decisions.

**Acceptance criteria:** A completed experiment stores its exact strategy configuration, dataset reference, benchmark, cost assumptions, code or engine version, and metrics.

### FR-10: Research verification

A Critic or Verification Agent shall assess:
- Source availability and relevance.
- Data freshness.
- Contradictory evidence.
- Calculation consistency.
- Unsupported claims.
- Citation completeness.
- Backtest methodology.
- Potential look-ahead bias and data leakage.
- Missing information that could change the conclusion.

The verifier shall be able to flag a report as incomplete or insufficiently supported.

**Acceptance criteria:** A failed verification prevents the report from presenting unverified conclusions as established facts.

### FR-11: Research report generation

The report shall include:
- Company and exchange identity.
- Research question and timestamp.
- Data coverage and source information.
- Business and financial analysis.
- Technical analysis, when requested.
- Positive and negative evidence.
- Key risks and uncertainty.
- Quantitative results, where applicable.
- Relevant benchmark comparisons.
- Citations and methodology.
- Limitations and conditions that could change the conclusion.

The interface may summarize evidence as bullish, neutral, bearish, or inconclusive, but these labels must be grounded in documented rules and supporting evidence. They must not be presented as guaranteed predictions or personalized financial advice.

**Acceptance criteria:** A report can be reopened later with its source references and experiment configuration intact.

### FR-12: Experiment history

Users shall be able to:
- View previous research runs.
- Inspect run status.
- Open generated reports.
- Compare experiment results.
- Re-run a research specification.
- Identify changes in input data or configuration.

**Acceptance criteria:** Re-running an experiment creates a new run record rather than overwriting the historical result.

### FR-13: n8n automation

n8n shall coordinate external workflows through authenticated API calls.

Initial workflows:
1. Scheduled market-data ingestion.
2. Manual or scheduled experiment execution.
3. Completion notifications.
4. Scheduled research refreshes.

n8n shall not independently calculate authoritative financial metrics or bypass backend validation.

**Acceptance criteria:** Failed workflows are logged and can be retried safely without unintentionally creating duplicate research runs.

### FR-14: User interface

The web application shall provide:
- A landing page explaining the product.
- A research workspace with a natural-language input.
- A company overview.
- A research progress view.
- A report dashboard.
- Charts and metric cards.
- A source and citation viewer.
- Experiment history.
- Error, loading, and incomplete-data states.

The interface shall clearly distinguish live or recently retrieved data from historical and cached data.

---

## 8. Agent Architecture

The initial implementation shall use a bounded, stateful LangGraph workflow.

### Agent 1: Supervisor / Planner

Responsibilities:
- Interpret the request.
- Identify required research tasks.
- Create the structured research plan.
- Route tasks to relevant agents.
- Track workflow state and completion.

### Agent 2: Market Data Agent

Responsibilities:
- Call approved market-data tools.
- Retrieve price history and instrument metadata.
- Request validation from the data service.
- Report missing or stale data.

The agent may explain results but shall not calculate authoritative metrics by guessing.

### Agent 3: Financial Research Agent

Responsibilities:
- Retrieve company filings and financial information.
- Identify relevant periods and definitions.
- Extract source-backed facts.
- Flag conflicting or incomplete information.

### Agent 4: RAG Research Agent

Responsibilities:
- Search the document index.
- Retrieve relevant passages.
- Return evidence with source metadata.
- Identify gaps in available research.

This can initially be implemented as a specialized node rather than a separate autonomous agent.

### Agent 5: Quantitative Analysis Toolchain

Responsibilities:
- Calculate financial ratios and technical indicators.
- Execute backtests.
- Compare results with benchmarks.
- Produce reproducible numerical outputs.

**Implementation rule:** This component is a deterministic Python service, not an LLM agent.

### Agent 6: Critic / Verification Agent

Responsibilities:
- Check evidence coverage.
- Identify contradictions and unsupported statements.
- Validate methodology and calculations.
- Recommend bounded re-retrieval or mark the report incomplete.

### Report Generator

Responsibilities:
- Assemble verified findings.
- Generate readable summaries and visualizations.
- Preserve citations, timestamps, assumptions, and limitations.

The report generator shall not alter verified metrics.

---

## 9. Technical Architecture

### Frontend
- React
- TypeScript
- Tailwind CSS
- Charting library for historical prices and quantitative results

### Backend
- Python
- FastAPI
- Pydantic for schema validation
- SQLAlchemy for persistence

### AI and orchestration
- LangGraph for stateful workflow orchestration
- LangChain for model integrations, tools, and retrievers
- Configurable LLM provider with structured outputs
- Embedding model for document retrieval

### Quantitative engine
- pandas
- NumPy
- SciPy and scikit-learn where appropriate
- A tested backtesting implementation, such as a custom event-driven engine or a suitable existing framework

### Data and storage
- PostgreSQL for users, instruments, market-data metadata, runs, metrics, and reports
- pgvector for document embeddings
- Object storage or a managed document store if needed for larger source files

### Automation and deployment
- n8n for scheduled and event-driven workflows
- Docker Compose for local and initial server deployment
- pytest for backend testing
- Structured application logs and workflow tracing

### High-level data flow

User interface  
→ FastAPI  
→ Request validation  
→ LangGraph research workflow  
→ Market-data tools + document retrieval  
→ Deterministic analysis services  
→ Verification  
→ Report generation  
→ PostgreSQL and document storage  
→ Dashboard and optional n8n notifications

---

## 10. Data Sources and Data Governance

The initial market scope is Indian equities.

Potential sources include:
- NSE and BSE disclosures and published market information.
- Official company annual reports and investor disclosures.
- Approved financial-data APIs.
- Relevant public research and regulatory publications.

Provider access, licensing, redistribution, historical coverage, and rate limits must be reviewed before production use. Public availability does not automatically grant unrestricted commercial reuse.

Each data record should retain:
- Provider or source.
- Instrument identifier.
- Observation or reporting date.
- Retrieval timestamp.
- Adjustment status, where applicable.
- Validation status.
- Relevant version or source reference.

The system must distinguish missing data from zero values and must not present delayed data as real-time data.

---

## 11. Initial Database Model

### users
- id
- email
- authentication_provider
- created_at

### instruments
- id
- exchange
- symbol
- company_name
- instrument_type
- currency
- provider_identifier

### market_data
- id
- instrument_id
- timestamp
- open
- high
- low
- close
- adjusted_close, where available
- volume
- provider
- validation_status

### research_runs
- id
- user_id
- research_question
- structured_specification
- status
- started_at
- completed_at
- model_configuration
- workflow_version

### research_sources
- id
- research_run_id
- source_type
- source_url_or_identifier
- title
- publication_date
- retrieved_at
- citation_metadata

### experiment_runs
- id
- research_run_id
- strategy_configuration
- dataset_reference
- benchmark
- cost_assumptions
- engine_version
- metrics
- validation_status

### reports
- id
- research_run_id
- report_content
- report_version
- generated_at
- verification_status

### automation_events
- id
- workflow_name
- related_run_id
- status
- attempt_count
- error_summary
- created_at

The final schema may evolve as authentication, access control, document storage, and data-retention requirements become clearer.

---

## 12. API Requirements

The following endpoints define the initial API contract.

### Research
- `POST /api/v1/research` — Create a research run.
- `GET /api/v1/research/{run_id}` — Retrieve status and summary.
- `GET /api/v1/research/{run_id}/report` — Retrieve the generated report.
- `GET /api/v1/research` — List research history.

### Instruments and market data
- `GET /api/v1/instruments/search?q=...` — Search supported instruments.
- `GET /api/v1/instruments/{instrument_id}` — Retrieve instrument metadata.
- `GET /api/v1/market-data/{instrument_id}` — Retrieve available market data.

### Experiments
- `POST /api/v1/experiments` — Create a strategy experiment.
- `GET /api/v1/experiments/{experiment_id}` — Retrieve experiment status and results.
- `POST /api/v1/experiments/{experiment_id}/rerun` — Create a new run from a saved configuration.

### Automation
- `POST /api/v1/internal/ingestion-jobs` — Trigger an authorized ingestion job.
- `POST /api/v1/internal/automation-events` — Accept trusted workflow events where required.

API requests must be authenticated and validated. Internal endpoints must not be exposed without appropriate access controls.

---

## 13. Non-Functional Requirements

### Reliability
- Workflow failures must be explicit and observable.
- External API calls must have timeouts and bounded retries.
- Long-running research must support asynchronous status tracking.
- Duplicate requests must be handled safely where appropriate.

### Performance
Initial targets, to be validated in testing:
- Basic instrument search: p95 response time under 2 seconds.
- Research request acknowledgement: under 2 seconds for a normal, healthy request.
- Standard research report: target completion within 60–180 seconds, depending on data-provider and LLM latency.
- Long-running experiments must execute asynchronously and report progress.

These are engineering targets, not guaranteed service-level commitments.

### Security
- Store secrets in environment configuration or a secrets manager, never in source control.
- Authenticate user requests.
- Enforce user-level authorization on saved reports and experiments.
- Validate all tool inputs and external responses.
- Apply rate limits to costly endpoints.
- Protect against prompt injection contained in retrieved documents.
- Restrict agent tools to approved operations.
- Never execute arbitrary generated code as part of a research request.

### Observability
Each run should record:
- Run identifier.
- Workflow stage.
- Timestamps and duration.
- Tool and provider errors.
- Model and prompt versions where appropriate.
- Data references.
- Validation results.
- Final status.

Sensitive content and credentials must not be written to logs.

### Reproducibility
Store sufficient configuration, source references, assumptions, and engine versions to reproduce or explain historical results. Exact reproduction may depend on source-data retention and external provider availability.

---

## 14. Financial Research and Backtesting Safety

MarketLab AI must not present historical performance as proof of future returns.

Backtesting must account for:
- Look-ahead bias.
- Survivorship bias where relevant.
- Data leakage.
- Corporate actions and price adjustments.
- Trading costs and slippage.
- Liquidity and execution assumptions.
- Chronological train/test separation.
- Parameter overfitting.
- Benchmark selection.
- Missing or inconsistent data.

Strategy reports should include out-of-sample results and disclose methodological limitations. A strategy should not be described as robust solely because it performed well on the data used to develop it.

The initial release shall be a research and decision-support product. Real-money order execution is outside scope.

---

## 15. User Experience Requirements

### Research workspace

The user enters a natural-language request, selects a supported company if necessary, and submits the request.

### Research progress

The interface displays meaningful stages, such as:
1. Understanding the request.
2. Retrieving market data.
3. Researching company disclosures.
4. Running quantitative analysis.
5. Verifying findings.
6. Preparing the report.

The interface must not imply that a stage succeeded until the backend confirms its result.

### Report dashboard

The report should prioritize:
- Research summary.
- Key supporting and opposing evidence.
- Financial and technical metrics.
- Risk factors.
- Historical performance, where relevant.
- Citations and source dates.
- Assumptions and limitations.

### Failure states

If a provider is unavailable, a source cannot be verified, or evidence is insufficient, the interface should display a clear limitation and indicate which parts of the analysis remain incomplete.

---

## 16. Success Metrics

Product success shall be measured through functional, technical, and research-quality metrics.

### Functional metrics
- Percentage of valid research requests that complete successfully.
- Percentage of reports that preserve valid source references.
- Percentage of experiments that can be reproduced from stored configurations.
- Percentage of invalid or ambiguous requests correctly blocked or clarified.

### Quality metrics
- Citation precision and source relevance.
- Numerical agreement between report values and deterministic calculation outputs.
- Data-validation failure detection rate on a labelled test set.
- Rate of unsupported claims in an independently reviewed sample.
- Backtest correctness against known test cases.

### Performance metrics
- Median and p95 research completion time.
- Failure rate by data provider and workflow stage.
- Cost per completed research run.
- Retry rate and workflow recovery rate.

Targets should be established after a baseline evaluation. Do not claim accuracy or performance percentages without measured results.

---

## 17. Testing Strategy

### Unit tests
- Financial metric calculations.
- Technical indicators.
- Strategy entry and exit rules.
- Cost calculations.
- Data validation.
- Schema validation.

### Integration tests
- FastAPI endpoints.
- Database persistence.
- Market-data provider adapters.
- RAG retrieval and citation metadata.
- LangGraph workflow transitions.
- n8n-to-FastAPI integration.

### End-to-end tests
- Submit a stock research request.
- Resolve the intended instrument.
- Retrieve fixture or approved data.
- Generate a research report.
- Verify citations and metric consistency.
- Reopen the saved report.

### Financial correctness tests
Use synthetic fixtures and known expected outputs to test:
- Moving-average calculations.
- Portfolio returns.
- Transaction costs.
- Drawdown.
- Benchmark comparisons.
- Prevention of future-data leakage.

Synthetic fixtures are for software testing only; they must not be presented as actual market evidence.

### AI evaluation
Create a fixed evaluation set containing:
- Clear research requests.
- Ambiguous stock names.
- Missing parameters.
- Conflicting source information.
- Prompt injection inside retrieved documents.
- Unsupported financial claims.
- Requests with unavailable data.

Evaluate structured-output validity, tool selection, citation quality, verification behaviour, and workflow completion.

---

## 18. Four-Week MVP Roadmap

### Week 1 — Data and quantitative foundation
- Set up the repository and Docker Compose.
- Build the FastAPI application and PostgreSQL schema.
- Implement instrument resolution and one approved market-data provider.
- Add data-quality checks.
- Implement moving-average crossover backtesting.
- Test returns, transaction costs, and benchmark calculations.

**Deliverable:** A working quantitative engine with reproducible test cases.

### Week 2 — AI and agent orchestration
- Integrate an LLM provider.
- Build structured research specifications.
- Implement the LangGraph supervisor and research nodes.
- Add market-data and document-research tools.
- Add error handling and run-state persistence.

**Deliverable:** A natural-language request can trigger a controlled research workflow.

### Week 3 — RAG and verification
- Build document ingestion and chunking.
- Add embeddings and pgvector retrieval.
- Preserve source metadata and citations.
- Implement verification checks.
- Add research-report generation.
- Add an evaluation dataset and tests.

**Deliverable:** An evidence-backed research report with reproducible numerical results.

### Week 4 — Dashboard and automation
- Build the React research workspace.
- Add progress tracking and report visualizations.
- Add research history.
- Integrate initial n8n workflows.
- Complete Docker configuration and deployment documentation.
- Run end-to-end tests and fix critical issues.

**Deliverable:** A demonstrable end-to-end MVP.

The schedule assumes a focused scope, accessible data sources, and sufficient development time. Production hardening may require additional iterations.

---

## 19. Risks and Mitigations

### Inaccurate or incomplete market data
**Mitigation:** Provider adapters, source timestamps, validation, explicit data-coverage reporting, and rejection of invalid inputs.

### Hallucinated financial claims
**Mitigation:** Require source-backed claims, use deterministic calculations, verify numerical outputs, and report insufficient evidence.

### Backtest overfitting
**Mitigation:** Chronological splits, out-of-sample testing, sensitivity analysis, realistic costs, and explicit limitations.

### LLM or provider outages
**Mitigation:** Timeouts, bounded retries, status tracking, and clear incomplete-run states.

### Excessive LLM cost
**Mitigation:** Use structured outputs, cache reusable retrieval results, limit unnecessary agent loops, and track per-run costs.

### Licensing and provider restrictions
**Mitigation:** Review data terms before use, respect rate limits, and avoid redistributing data without permission.

### Scope expansion
**Mitigation:** Complete the single-stock research workflow and one tested strategy before adding portfolios, execution, or advanced forecasting.

---

## 20. Definition of Done

The MVP is ready for demonstration when:

- A user can submit a natural-language stock research request.
- The application resolves the correct supported instrument.
- Market data and research sources are retrieved and validated.
- The AI workflow runs through LangGraph with observable stages.
- Financial calculations are performed by deterministic code.
- RAG provides traceable source references.
- The verification stage flags missing or unsupported evidence.
- The generated report includes methodology, assumptions, risks, and limitations.
- Research runs and configurations persist in PostgreSQL.
- At least one strategy can be tested with costs and a benchmark.
- Core unit, integration, and end-to-end tests pass.
- The application runs through the documented Docker setup.
- n8n can trigger at least one authenticated workflow successfully.
- The README documents setup, environment variables, data-source limitations, and evaluation results.

---

## 21. Final Product Principle

**MarketLab AI must be able to explain its evidence, calculations, and uncertainty—not just produce a convincing answer.**

The first release should prove that a natural-language research question can reliably become a validated, reproducible, source-backed report. Every advanced capability should build on that foundation.
