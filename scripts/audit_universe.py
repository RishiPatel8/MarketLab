import sqlite3
import json
from datetime import datetime, timezone

def generate_audit_report():
    conn = sqlite3.connect("backend/marketlab.db")
    c = conn.cursor()

    total = c.execute("SELECT COUNT(*) FROM instruments").fetchone()[0]
    active = c.execute("SELECT COUNT(*) FROM instruments WHERE status = 'ACTIVE'").fetchone()[0]
    nse_count = c.execute("SELECT COUNT(*) FROM instruments WHERE exchange LIKE '%NSE%'").fetchone()[0]
    bse_count = c.execute("SELECT COUNT(*) FROM instruments WHERE exchange LIKE '%BSE%'").fetchone()[0]
    dual_listed = c.execute("SELECT COUNT(*) FROM instruments WHERE exchange = 'NSE,BSE'").fetchone()[0]
    bse_exclusive = c.execute("SELECT COUNT(*) FROM instruments WHERE exchange = 'BSE'").fetchone()[0]
    
    etf_count = c.execute("SELECT COUNT(*) FROM instruments WHERE instrument_type = 'ETF'").fetchone()[0]
    etf_nse = c.execute("SELECT COUNT(*) FROM instruments WHERE instrument_type = 'ETF' AND exchange LIKE '%NSE%'").fetchone()[0]
    etf_bse = c.execute("SELECT COUNT(*) FROM instruments WHERE instrument_type = 'ETF' AND exchange LIKE '%BSE%'").fetchone()[0]

    mf_count = c.execute("SELECT COUNT(*) FROM instruments WHERE instrument_type = 'MUTUAL_FUND'").fetchone()[0]
    sme_count = c.execute("SELECT COUNT(*) FROM instruments WHERE instrument_type = 'SME_EQUITY'").fetchone()[0]
    equity_count = c.execute("SELECT COUNT(*) FROM instruments WHERE instrument_type = 'EQUITY'").fetchone()[0]
    index_count = c.execute("SELECT COUNT(*) FROM instruments WHERE instrument_type = 'INDEX'").fetchone()[0]
    
    isin_count = c.execute("SELECT COUNT(*) FROM instruments WHERE isin IS NOT NULL").fetchone()[0]
    bse_code_count = c.execute("SELECT COUNT(*) FROM instruments WHERE bse_code IS NOT NULL").fetchone()[0]
    scheme_code_count = c.execute("SELECT COUNT(*) FROM instruments WHERE scheme_code IS NOT NULL").fetchone()[0]
    unverified_count = c.execute("SELECT COUNT(*) FROM instruments WHERE status NOT IN ('ACTIVE', 'SUSPENDED', 'DELISTED', 'INACTIVE')").fetchone()[0]

    # Definition of exchange-specific listings:
    # NSE listings (2,986) + BSE listings (5,392) + AMFI registered schemes (14,400) = 22,778 listings
    # representing 20,534 distinct canonical entities (since 2,244 entities are dual-listed on both NSE & BSE).
    exchange_listings = nse_count + bse_count + mf_count

    # Sample checks
    sample_bse_only = c.execute("SELECT symbol, canonical_name, bse_code, isin FROM instruments WHERE exchange = 'BSE' LIMIT 5").fetchall()
    sample_etfs = c.execute("SELECT symbol, canonical_name, isin FROM instruments WHERE instrument_type = 'ETF' LIMIT 5").fetchall()
    sample_mfs = c.execute("SELECT scheme_code, canonical_name, latest_nav, latest_nav_date FROM instruments WHERE instrument_type = 'MUTUAL_FUND' LIMIT 5").fetchall()

    report = {
        "report_generated_utc": datetime.now(timezone.utc).isoformat(),
        "coverage_summary": {
            "1_distinct_canonical_entities": total,
            "2_exchange_specific_listings": exchange_listings,
            "3_nse_listings": nse_count,
            "4_bse_listings": bse_count,
            "5_dual_listed_entities": dual_listed,
            "6_bse_exclusive_entities": bse_exclusive,
            "7_etfs": {
                "total": etf_count,
                "nse_listed": etf_nse,
                "bse_listed": etf_bse
            },
            "8_mutual_fund_schemes": mf_count,
            "9_sme_listings": sme_count,
            "10_records_with_valid_official_identifiers": {
                "with_isin": isin_count,
                "with_bse_code": bse_code_count,
                "with_scheme_code": scheme_code_count
            },
            "11_records_unverified_status": unverified_count
        },
        "additional_breakdown": {
            "active_instruments": active,
            "mainboard_equities": equity_count,
            "market_indices": index_count
        },
        "sample_records": {
            "bse_exclusive": sample_bse_only,
            "etfs": sample_etfs,
            "mutual_funds": sample_mfs
        }
    }

    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    generate_audit_report()
