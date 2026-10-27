# MarketLab AI — Data Sources & Governance

## 1. Primary Market: Indian Equities (NSE & BSE)

MarketLab AI is specifically configured for companies listed on the National Stock Exchange of India (NSE) and Bombay Stock Exchange (BSE).

### 1.1 Market Data Providers
- **Live / Integration Mode**: Permitted market data APIs and official exchange public Bhavcopy files.
- **Fixture / Offline Mode**: Deterministic historical OHLCV fixtures stored in `backend/app/providers/market_data/fixtures/` covering major Indian benchmark equities (e.g., Orient Green Power `GREENPOWER`, Reliance Industries `RELIANCE`, Tata Motors `TATAMOTORS`, Infosys `INFY`, and Nifty 50 benchmark `NIFTY50`).
- **Data Quality & Validation Rules**:
  - `High >= max(Open, Close)` and `Low <= min(Open, Close)`
  - `Volume >= 0`
  - Detection of trading holidays and weekend gaps
  - Unadjusted vs split/bonus adjusted close distinctions
  - Clear labelling of timestamp latency (never label delayed data as real-time)

### 1.2 Regulatory & Filings Sources
- **Corporate Filings**: Official BSE/NSE corporate disclosures and quarterly financial results.
- **Annual Reports**: Ingested PDF and clean text extracts stored with cryptographic content hashes (`SHA-256`), publication dates, and section identifiers.
- **Disclaimer**: MarketLab AI strictly cites authoritative sources and does not permit agents to fabricate citations or use unverified internet blogs as financial ground truth.
