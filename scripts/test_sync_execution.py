import os
import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.db.session import Base
from app.db.models.instrument import Instrument
from app.services.instrument_sync_service import InstrumentSyncService

def test_sync():
    test_db_url = "sqlite:///backend/marketlab.db"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    print("--- Starting Full Evidence-Based Synchronization ---")
    start = time.time()
    sync_service = InstrumentSyncService(db)
    result = sync_service.sync_all()
    duration = time.time() - start

    print(f"\n--- Synchronization Finished in {duration:.2f} seconds ---")
    for src, t in result["sources"].items():
        print(f"\nSource: {src}")
        print(f"  URL: {t['source_url']}")
        print(f"  Provenance: {t['provenance']} (Live: {t['is_live']})")
        print(f"  Bytes: {t['downloaded_bytes']:,}")
        print(f"  Source Records: {t['source_record_count']:,}")
        print(f"  Accepted: {t['accepted_record_count']:,}")
        print(f"  Inserted: {t['inserted_count']:,}")
        print(f"  Updated: {t['updated_count']:,}")
        print(f"  Duplicates Merged: {t['duplicate_count']:,}")
        print(f"  Rejected: {t['rejected_record_count']:,} ({t['rejection_reasons']})")
        print(f"  Validation Status: {t['validation_status']}")

    status = sync_service.get_sync_status()
    print("\n--- Final Master Universe Metrics ---")
    print(f"  Total Instruments: {status.total_instruments:,}")
    print(f"  Active Instruments: {status.active_instruments:,}")
    print(f"  Distinct Canonical Entities: {status.distinct_canonical_entities:,}")
    print(f"  Exchange-Specific Listings: {status.exchange_specific_listings:,}")
    print(f"  NSE Listed: {status.nse_listed_count:,}")
    print(f"  BSE Listed: {status.bse_listed_count:,}")
    print(f"  Dual-Listed (NSE+BSE): {status.dual_listed_count:,}")
    print(f"  BSE Exclusive: {status.bse_exclusive_count:,}")
    print(f"  ETFs Total: {status.etf_count:,} (NSE: {status.etf_nse_count:,}, BSE: {status.etf_bse_count:,})")
    print(f"  Mutual Funds: {status.mutual_fund_count:,}")
    print(f"  SME Listed: {status.sme_count:,}")
    print(f"  Records with Verified ISIN: {status.records_with_isin:,}")
    print(f"  Records with BSE Code: {status.records_with_bse_code:,}")
    print(f"  Records with AMFI Scheme Code: {status.records_with_scheme_code:,}")
    print(f"  Unverified Status: {status.records_unverified_status:,}")

if __name__ == "__main__":
    test_sync()
