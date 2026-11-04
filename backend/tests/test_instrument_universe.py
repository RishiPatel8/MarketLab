import os
import io
import pytest
from app.services.instrument_sync_service import InstrumentSyncService
from app.services.instrument_service import InstrumentService
from app.db.models.instrument import Instrument
from app.schemas.instrument import SourceSyncTelemetry

def test_instrument_sync_service_execution(db_session):
    """Test that synchronization executes idempotently and populates instrument universe."""
    sync_service = InstrumentSyncService(db_session)
    stats = sync_service.sync_all()

    assert stats["status"] == "COMPLETED"
    assert stats["nse"]["added"] + stats["nse"]["updated"] >= 2600
    assert stats["bse"]["added"] + stats["bse"]["updated"] >= 5000
    assert stats["amfi"]["added"] + stats["amfi"]["updated"] >= 14000
    assert stats["nse"]["errors"] == 0
    assert stats["bse"]["errors"] == 0
    assert stats["amfi"]["errors"] == 0

    status = sync_service.get_sync_status()
    assert status.total_instruments >= 20000
    assert status.bse_listed_count >= 5000
    assert status.etf_count >= 300
    assert status.mutual_fund_count >= 14000
    assert status.dual_listed_count >= 2000
    assert status.bse_exclusive_count >= 2500
    assert status.records_with_isin >= 18000
    assert status.records_unverified_status == 0

    # Test idempotence - running sync again leaves unchanged without duplicate key errors
    repeat_stats = sync_service.sync_all()
    assert repeat_stats["nse"]["errors"] == 0
    assert repeat_stats["bse"]["errors"] == 0
    assert repeat_stats["amfi"]["errors"] == 0

def test_search_nse_equity_and_exact_ranking(client, db_session):
    """Test searching by NSE symbol with exact ranking priority."""
    response = client.get("/api/v1/instruments/search?q=RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    # First item must be the exact symbol match
    first = data["items"][0]
    assert first["symbol"] == "RELIANCE"
    assert first["instrument_type"] == "EQUITY"
    assert "INE002A01018" in first["isin"]

def test_search_by_isin(client, db_session):
    """Test searching directly by ISIN identifier."""
    response = client.get("/api/v1/instruments/search?q=INE002A01018")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["isin"] == "INE002A01018"

def test_search_bse_exclusive_instruments(client, db_session):
    """Test that BSE-exclusive instruments and BSE scrip codes resolve correctly."""
    # Search by BSE scrip code for Bombay Dyeing (500020) or Reliance (500325)
    response = client.get("/api/v1/instruments/search?q=500020")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    item = data["items"][0]
    assert item["bse_code"] == "500020" or "BOMDYEING" in item["canonical_name"]

def test_search_etfs(client, db_session):
    """Test filtering and searching ETFs across categories."""
    response = client.get("/api/v1/instruments/search?q=BEES&instrument_type=ETF")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["instrument_type"] == "ETF"

def test_search_mutual_funds_by_scheme_code_and_name(client, db_session):
    """Test discovering mutual funds via AMFI scheme code and category."""
    # Search for Parag Parikh Flexi Cap Fund scheme code 122639
    response = client.get("/api/v1/instruments/search?q=122639&instrument_type=MUTUAL_FUND")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    mf = data["items"][0]
    assert mf["scheme_code"] == "122639"
    assert mf["instrument_type"] == "MUTUAL_FUND"
    assert mf["exchange"] == "AMFI"
    assert mf["latest_nav"] is not None
    assert mf["latest_nav"] > 0

def test_search_type_and_exchange_filters(client, db_session):
    """Test filtering by instrument type and exchange."""
    # Filter only BSE instruments
    bse_res = client.get("/api/v1/instruments/search?exchange=BSE&limit=10")
    assert bse_res.status_code == 200
    bse_data = bse_res.json()
    assert len(bse_data["items"]) > 0
    for item in bse_data["items"]:
        assert "BSE" in item["exchange"] or item["bse_code"] is not None

    # Filter only Mutual Funds
    mf_res = client.get("/api/v1/instruments/search?instrument_type=MUTUAL_FUND&limit=10")
    assert mf_res.status_code == 200
    mf_data = mf_res.json()
    assert len(mf_data["items"]) > 0
    for item in mf_data["items"]:
        assert item["instrument_type"] == "MUTUAL_FUND"
        assert item["exchange"] == "AMFI"

def test_pagination_and_limits(client, db_session):
    """Test search pagination and limits."""
    res_p1 = client.get("/api/v1/instruments/search?page=1&limit=5")
    assert res_p1.status_code == 200
    d1 = res_p1.json()
    assert len(d1["items"]) == 5
    assert d1["page"] == 1
    assert d1["limit"] == 5

    res_p2 = client.get("/api/v1/instruments/search?page=2&limit=5")
    assert res_p2.status_code == 200
    d2 = res_p2.json()
    assert len(d2["items"]) == 5
    assert d2["page"] == 2
    # Ensure page 1 and page 2 items are distinct
    assert d1["items"][0]["id"] != d2["items"][0]["id"]

def test_resolve_instrument_ambiguity(client, db_session):
    """Test that ambiguous queries return candidate disambiguation list."""
    response = client.get("/api/v1/instruments/resolve?q=Tata")
    assert response.status_code == 200
    data = response.json()
    assert data["requires_clarification"] is True
    assert len(data["candidates"]) >= 2
    # Check that candidates have distinct identifiers
    symbols = [c["symbol"] for c in data["candidates"]]
    assert len(symbols) == len(set(symbols))

def test_sync_status_endpoint(client, db_session):
    """Test retrieval of synchronization diagnostics and counts."""
    response = client.get("/api/v1/instruments/sync/status")
    assert response.status_code == 200
    status = response.json()
    assert status["total_instruments"] >= 20000
    assert status["nse_listed_count"] >= 2600
    assert status["bse_listed_count"] >= 5000
    assert status["etf_count"] >= 300
    assert status["mutual_fund_count"] >= 14000
    assert status["last_sync_status"] == "SYNCHRONIZED"

def test_market_data_availability_separation(client, db_session):
    """Test that instrument discovery is separated from price-data availability."""
    search_res = client.get("/api/v1/instruments/search?instrument_type=MUTUAL_FUND&limit=1")
    mf = search_res.json()["items"][0]
    
    md_res = client.get(f"/api/v1/instruments/{mf['id']}/market-data")
    assert md_res.status_code == 200
    md = md_res.json()
    assert md["validation"]["latency_type"] == "nav_observation"
    assert md["validation"]["is_valid"] is True

def test_truncated_file_rejection(db_session):
    """Test that truncated source file is rejected and existing records remain intact."""
    sync_service = InstrumentSyncService(db_session)
    count_before = db_session.query(Instrument).count()

    telemetry = sync_service.sync_nse_equities(raw_override="SYMBOL,NAME OF COMPANY, SERIES, ISIN NUMBER\nINFY,Infosys,EQ,INE009A01021\n")

    assert telemetry.validation_status == "FAILED_VALIDATION"
    assert "below minimum threshold" in telemetry.error_message
    
    count_after = db_session.query(Instrument).count()
    assert count_after == count_before

def test_invalid_header_rejection(db_session):
    """Test that invalid file headers cause validation failure without database corruption."""
    sync_service = InstrumentSyncService(db_session)
    count_before = db_session.query(Instrument).count()

    bad_csv = "COL_A,COL_B,COL_C\n" + ("VAL1,VAL2,VAL3\n" * 1500)
    telemetry = sync_service.sync_nse_equities(raw_override=bad_csv)

    assert telemetry.validation_status == "FAILED_VALIDATION"
    assert "failed header validation" in telemetry.error_message
    assert db_session.query(Instrument).count() == count_before

def test_stale_fallback_reporting(db_session, monkeypatch):
    """Test that when live fetch fails, reference snapshot is labeled STALE_FALLBACK."""
    sync_service = InstrumentSyncService(db_session)
    monkeypatch.setattr(sync_service, "_fetch_url", lambda url, timeout=15: (None, None, "Connection timed out"))

    telemetry = sync_service.sync_nse_equities(allow_fallback=True)
    assert telemetry.validation_status == "PASSED"
    assert telemetry.is_live is False
    assert telemetry.provenance == "STALE_FALLBACK"
    assert telemetry.accepted_record_count >= 2600

def test_dual_listing_resolution(db_session):
    """Test that dual-listed entities correctly resolve to exchange='NSE,BSE' with both codes."""
    inst = db_session.query(Instrument).filter(Instrument.symbol == "RELIANCE").first()
    assert inst is not None
    assert inst.exchange == "NSE,BSE"
    assert inst.bse_code == "500325"
    assert inst.bse_symbol == "RELIANCE"
    assert inst.isin == "INE002A01018"

def test_amfi_scheme_variants_direct_regular(db_session):
    """Test that scheme variants (Direct vs Regular, Growth vs IDCW) are preserved distinctly."""
    direct_schemes = db_session.query(Instrument).filter(
        Instrument.instrument_type == "MUTUAL_FUND",
        Instrument.plan_type == "Direct"
    ).count()
    regular_schemes = db_session.query(Instrument).filter(
        Instrument.instrument_type == "MUTUAL_FUND",
        Instrument.plan_type == "Regular"
    ).count()
    assert direct_schemes > 1000
    assert regular_schemes > 1000

@pytest.mark.skipif(not os.getenv("RUN_LIVE_TESTS"), reason="Opt-in live integration test")
def test_opt_in_live_sources_comparison(db_session):
    """Opt-in live integration test to verify live feeds against reference counts."""
    sync_service = InstrumentSyncService(db_session)
    live_amfi = sync_service.sync_amfi_mutual_funds()
    assert live_amfi.is_live is True
    assert live_amfi.source_record_count >= 14000
