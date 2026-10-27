"""
MarketLab AI — Seed Data Script
Initializes PostgreSQL / SQLite database with supported Indian Equities (NSE/BSE),
historical daily OHLCV bars, financial facts, and regulatory disclosure documents.
"""

import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.db.session import sync_engine, Base, SyncSessionLocal
import app.db.models
from app.services.instrument_service import InstrumentService, SEED_INSTRUMENTS
from app.services.market_data_service import MarketDataService
from app.services.rag_service import RAGService

def main():
    print("MarketLab AI — Initializing Database Schema...")
    Base.metadata.create_all(bind=sync_engine)
    print("Database tables created successfully.")

    with SyncSessionLocal() as db:
        print("Seeding Indian Equities instruments...")
        inst_svc = InstrumentService(db)
        print(f"Seeded {len(SEED_INSTRUMENTS)} core instruments (GREENPOWER, RELIANCE, TATAMOTORS, etc.).")

        print("Seeding Regulatory Disclosures & Generating pgvector Chunks...")
        rag_svc = RAGService(db)
        print("Authoritative filings and embeddings indexed.")

        print("Ingesting and validating baseline historical market data...")
        md_svc = MarketDataService(db)
        for item in SEED_INSTRUMENTS:
            sym = item["symbol"]
            inst = inst_svc.repo.get_by_symbol_and_exchange(sym, item["exchange"])
            if inst:
                bars, val = md_svc.get_and_validate_bars(sym, item["exchange"], instrument_id=inst.id)
                print(f"  -> {item['exchange']}:{sym} — {len(bars)} bars validated (Coverage: {val.coverage_percentage}%)")

    print("\nDatabase initialization and seeding complete! MarketLab AI is ready.")

if __name__ == "__main__":
    main()
