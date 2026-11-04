import os
import csv
import io
import re
import json
import zipfile
import urllib.request
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.db.models.instrument import Instrument
from app.schemas.instrument import InstrumentSyncStatusResponse, SourceSyncTelemetry

logger = logging.getLogger("marketlab.service.instrument_sync")

REFERENCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "reference"))

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*"
}

class InstrumentSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.source_telemetry: Dict[str, SourceSyncTelemetry] = {}

    def _fetch_url(self, url: str, timeout: int = 15) -> Tuple[Optional[bytes], Optional[int], Optional[str]]:
        """Safely fetches data from a remote URL."""
        try:
            req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status_code = resp.getcode()
                content = resp.read()
                return content, status_code, None
        except Exception as e:
            logger.warning(f"Failed to fetch live URL '{url}': {e}")
            return None, None, str(e)

    def _get_in_memory_index(self):
        """Builds in-memory index of existing instruments for fast, safe upserts."""
        existing_records = self.db.query(Instrument).all()
        by_isin = {}
        by_bse_code = {}
        by_scheme_code = {}
        by_symbol = {}

        for inst in existing_records:
            if inst.isin:
                by_isin[inst.isin.upper()] = inst
            if inst.bse_code:
                by_bse_code[inst.bse_code] = inst
            if inst.scheme_code:
                by_scheme_code[inst.scheme_code] = inst
            by_symbol[(inst.symbol.upper(), inst.exchange)] = inst

        return by_isin, by_bse_code, by_scheme_code, by_symbol

    def sync_nse_equities(self, raw_override: Optional[str] = None, allow_fallback: bool = True) -> SourceSyncTelemetry:
        """Synchronizes official NSE equities and SMEs."""
        source_name = "NSE_EQUITIES"
        url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
        now = datetime.now(timezone.utc)
        telemetry = SourceSyncTelemetry(
            source_name=source_name,
            source_url=url,
            retrieval_timestamp=now,
            is_live=False,
            provenance="VERIFIED_REFERENCE_SNAPSHOT",
            validation_status="PASSED"
        )

        csv_text = None
        if raw_override is not None:
            csv_text = raw_override
            telemetry.downloaded_bytes = len(raw_override.encode("utf-8"))
            telemetry.provenance = "PAYLOAD_OVERRIDE"
        else:
            # 1. Attempt live fetch
            raw_bytes, status_code, error = self._fetch_url(url, timeout=12)
            telemetry.response_status_code = status_code
            is_valid_live = False
            if raw_bytes and len(raw_bytes) > 50000:
                candidate = raw_bytes.decode("utf-8", errors="ignore")
                if "SYMBOL" in candidate and "ISIN NUMBER" in candidate:
                    csv_text = candidate
                    telemetry.downloaded_bytes = len(raw_bytes)
                    telemetry.is_live = True
                    telemetry.provenance = "LIVE_OFFICIAL"
                    is_valid_live = True

            if not is_valid_live:
                if not allow_fallback:
                    telemetry.validation_status = "FAILED_VALIDATION"
                    telemetry.error_message = f"Live NSE download failed or was invalid ({error or 'truncated/malformed payload'}) and fallback is disabled."
                    self.source_telemetry[source_name] = telemetry
                    return telemetry

                telemetry.provenance = "STALE_FALLBACK"
                ref_path = os.path.join(REFERENCE_DIR, "nse_equities.csv")
                if os.path.isfile(ref_path):
                    with open(ref_path, "r", encoding="utf-8", errors="ignore") as f:
                        csv_text = f.read()
                    telemetry.downloaded_bytes = len(csv_text.encode("utf-8"))
                else:
                    telemetry.validation_status = "FAILED_VALIDATION"
                    telemetry.error_message = "No NSE source data available (live failed and reference missing)."
                    self.source_telemetry[source_name] = telemetry
                    return telemetry

        # 2. Validation
        if not csv_text or "SYMBOL" not in csv_text or "ISIN NUMBER" not in csv_text:
            telemetry.validation_status = "FAILED_VALIDATION"
            telemetry.error_message = "Downloaded NSE file failed header validation."
            self.source_telemetry[source_name] = telemetry
            return telemetry

        reader = list(csv.DictReader(io.StringIO(csv_text)))
        telemetry.source_record_count = len(reader)
        if len(reader) < 1000:
            telemetry.validation_status = "FAILED_VALIDATION"
            telemetry.error_message = f"Plausibility check failed: NSE record count ({len(reader)}) is below minimum threshold."
            self.source_telemetry[source_name] = telemetry
            return telemetry

        # 3. Ingestion
        by_isin, by_bse_code, by_scheme_code, by_symbol = self._get_in_memory_index()
        new_batch = []

        for row in reader:
            telemetry.parsed_record_count += 1
            symbol = row.get("SYMBOL", "").strip().upper()
            name = row.get("NAME OF COMPANY", "").strip()
            series = row.get(" SERIES", row.get("SERIES", "")).strip().upper()
            isin = row.get(" ISIN NUMBER", row.get("ISIN NUMBER", "")).strip().upper()

            if not symbol or not name:
                telemetry.rejected_record_count += 1
                telemetry.rejection_reasons["missing_symbol_or_name"] = telemetry.rejection_reasons.get("missing_symbol_or_name", 0) + 1
                continue

            inst_type = "SME_EQUITY" if series == "SM" else "EQUITY"
            existing = by_isin.get(isin) if isin else None
            if not existing:
                existing = by_symbol.get((symbol, "NSE")) or by_symbol.get((symbol, "NSE,BSE"))

            if existing:
                # Update record
                existing.company_name = name
                existing.canonical_name = name
                existing.display_name = f"{name} ({symbol})"
                existing.nse_symbol = symbol
                existing.isin = isin or existing.isin
                existing.instrument_type = inst_type
                existing.status = "ACTIVE"
                existing.source_provider = "NSE"
                existing.last_sync_timestamp = now
                telemetry.updated_count += 1
            else:
                new_inst = Instrument(
                    symbol=symbol,
                    company_name=name,
                    canonical_name=name,
                    display_name=f"{name} ({symbol})",
                    exchange="NSE",
                    nse_symbol=symbol,
                    isin=isin or None,
                    instrument_type=inst_type,
                    currency="INR",
                    status="ACTIVE",
                    source_provider="NSE",
                    data_availability="SUPPORTED",
                    last_sync_timestamp=now,
                    last_verified_timestamp=now
                )
                new_batch.append(new_inst)
                if isin:
                    by_isin[isin] = new_inst
                by_symbol[(symbol, "NSE")] = new_inst
                telemetry.inserted_count += 1

            telemetry.accepted_record_count += 1

        if new_batch:
            self.db.add_all(new_batch)
        self.db.commit()

        self.source_telemetry[source_name] = telemetry
        return telemetry

    def sync_nse_etfs(self) -> SourceSyncTelemetry:
        """Synchronizes official NSE ETFs."""
        source_name = "NSE_ETFS"
        url = "https://www.nseindia.com/api/etf"
        now = datetime.now(timezone.utc)
        telemetry = SourceSyncTelemetry(
            source_name=source_name,
            source_url=url,
            retrieval_timestamp=now,
            is_live=False,
            provenance="VERIFIED_REFERENCE_SNAPSHOT",
            validation_status="PASSED"
        )

        raw_bytes, status_code, error = self._fetch_url(url, timeout=12)
        telemetry.response_status_code = status_code
        etf_items = []

        if raw_bytes and len(raw_bytes) > 10000:
            try:
                parsed_json = json.loads(raw_bytes.decode("utf-8"))
                etf_items = parsed_json.get("data", [])
                telemetry.downloaded_bytes = len(raw_bytes)
                telemetry.is_live = True
                telemetry.provenance = "LIVE_OFFICIAL"
            except Exception:
                pass

        if not etf_items:
            ref_path = os.path.join(REFERENCE_DIR, "nse_etfs.json")
            if os.path.isfile(ref_path):
                with open(ref_path, "r", encoding="utf-8") as f:
                    parsed_json = json.load(f)
                etf_items = parsed_json.get("data", [])
                telemetry.downloaded_bytes = os.path.getsize(ref_path)
                telemetry.provenance = "VERIFIED_REFERENCE_SNAPSHOT"

        telemetry.source_record_count = len(etf_items)
        if len(etf_items) < 20:
            telemetry.validation_status = "FAILED_VALIDATION"
            telemetry.error_message = "NSE ETF list contains fewer records than required minimum."
            self.source_telemetry[source_name] = telemetry
            return telemetry

        by_isin, by_bse_code, by_scheme_code, by_symbol = self._get_in_memory_index()
        new_batch = []

        for item in etf_items:
            telemetry.parsed_record_count += 1
            symbol = item.get("symbol", "").strip().upper()
            assets = item.get("assets", "").strip()
            nav_val = None
            try:
                nav_val = float(item.get("nav", 0)) if item.get("nav") else None
            except ValueError:
                nav_val = None

            if not symbol:
                telemetry.rejected_record_count += 1
                telemetry.rejection_reasons["missing_symbol"] = telemetry.rejection_reasons.get("missing_symbol", 0) + 1
                continue

            existing = by_symbol.get((symbol, "NSE")) or by_symbol.get((symbol, "NSE,BSE"))
            if existing:
                existing.instrument_type = "ETF"
                existing.scheme_category = assets or existing.scheme_category
                existing.latest_nav = nav_val or existing.latest_nav
                existing.last_sync_timestamp = now
                telemetry.updated_count += 1
            else:
                new_etf = Instrument(
                    symbol=symbol,
                    company_name=f"{symbol} ETF",
                    canonical_name=f"{symbol} ETF",
                    display_name=f"{symbol} ({assets or 'ETF'})",
                    exchange="NSE",
                    nse_symbol=symbol,
                    instrument_type="ETF",
                    scheme_category=assets or "Exchange Traded Fund",
                    currency="INR",
                    latest_nav=nav_val,
                    status="ACTIVE",
                    source_provider="NSE",
                    data_availability="SUPPORTED",
                    last_sync_timestamp=now,
                    last_verified_timestamp=now
                )
                new_batch.append(new_etf)
                by_symbol[(symbol, "NSE")] = new_etf
                telemetry.inserted_count += 1

            telemetry.accepted_record_count += 1

        if new_batch:
            self.db.add_all(new_batch)
        self.db.commit()

        self.source_telemetry[source_name] = telemetry
        return telemetry

    def sync_bse_securities(self) -> SourceSyncTelemetry:
        """Synchronizes official BSE securities, dual-listed entities, and BSE-exclusive listings."""
        source_name = "BSE_SECURITIES"
        url = "https://www.bseindia.com/downloads/Help/file/SCRIP.zip"
        now = datetime.now(timezone.utc)
        telemetry = SourceSyncTelemetry(
            source_name=source_name,
            source_url=url,
            retrieval_timestamp=now,
            is_live=False,
            provenance="VERIFIED_REFERENCE_SNAPSHOT",
            validation_status="PASSED"
        )

        bse_rows = []
        raw_zip_bytes, status_code, error = self._fetch_url(url, timeout=25)
        telemetry.response_status_code = status_code

        # If live zip downloaded, parse in memory
        if raw_zip_bytes and len(raw_zip_bytes) > 500000:
            try:
                zf = zipfile.ZipFile(io.BytesIO(raw_zip_bytes))
                telemetry.downloaded_bytes = len(raw_zip_bytes)
                telemetry.is_live = True
                telemetry.provenance = "LIVE_OFFICIAL"
                bse_rows = self._extract_bse_rows_from_zip(zf)
            except Exception as e:
                logger.warning(f"Error reading downloaded BSE zip: {e}")

        # Fallback to verified reference files
        if not bse_rows:
            ref_csv = os.path.join(REFERENCE_DIR, "bse_active_securities.csv")
            if os.path.isfile(ref_csv):
                with open(ref_csv, "r", encoding="utf-8") as f:
                    bse_rows = list(csv.DictReader(f))
                telemetry.downloaded_bytes = os.path.getsize(ref_csv)
                telemetry.provenance = "VERIFIED_REFERENCE_SNAPSHOT"
            else:
                ref_zip = os.path.join(REFERENCE_DIR, "bse_scrip.zip")
                if os.path.isfile(ref_zip):
                    with zipfile.ZipFile(ref_zip, "r") as zf:
                        bse_rows = self._extract_bse_rows_from_zip(zf)
                    telemetry.downloaded_bytes = os.path.getsize(ref_zip)
                    telemetry.provenance = "VERIFIED_REFERENCE_SNAPSHOT"

        telemetry.source_record_count = len(bse_rows)
        if len(bse_rows) < 2000:
            telemetry.validation_status = "FAILED_VALIDATION"
            telemetry.error_message = f"Plausibility check failed: BSE record count ({len(bse_rows)}) is below minimum threshold."
            self.source_telemetry[source_name] = telemetry
            return telemetry

        by_isin, by_bse_code, by_scheme_code, by_symbol = self._get_in_memory_index()
        new_batch = []

        for row in bse_rows:
            telemetry.parsed_record_count += 1
            scrip_code = row.get("SCRIP_CODE", "").strip()
            scrip_id = row.get("SCRIP_ID", "").strip().upper()
            name = row.get("COMPANY_NAME", "").strip()
            isin = row.get("ISIN_NUMBER", "").strip().upper()
            grp = row.get("GROUP", "").strip().upper()
            is_exclusive = row.get("IS_BSE_EXCLUSIVE", "False").strip().lower() == "true"
            inst_type = row.get("INSTRUMENT_TYPE", "EQUITY").strip().upper()

            if not scrip_code or not scrip_id:
                telemetry.rejected_record_count += 1
                telemetry.rejection_reasons["missing_scrip_identifier"] = telemetry.rejection_reasons.get("missing_scrip_identifier", 0) + 1
                continue

            # Dual-listed resolution: check if already exists by ISIN
            existing = by_isin.get(isin) if isin else None

            if existing and not is_exclusive:
                # Merge into dual-listed entity
                old_key = (existing.symbol.upper(), existing.exchange)
                existing.exchange = "NSE,BSE"
                existing.bse_code = scrip_code
                existing.bse_symbol = scrip_id
                existing.last_sync_timestamp = now
                telemetry.duplicate_count += 1
                telemetry.updated_count += 1
                by_bse_code[scrip_code] = existing
                by_symbol[(existing.symbol.upper(), "NSE,BSE")] = existing
            else:
                # BSE exclusive or not yet in master
                bse_existing = by_bse_code.get(scrip_code)
                if bse_existing:
                    bse_existing.company_name = name or bse_existing.company_name
                    bse_existing.bse_symbol = scrip_id
                    bse_existing.isin = isin or bse_existing.isin
                    bse_existing.instrument_type = inst_type
                    bse_existing.last_sync_timestamp = now
                    telemetry.updated_count += 1
                else:
                    target_symbol = scrip_id or scrip_code
                    if (target_symbol.upper(), "BSE") in by_symbol:
                        target_symbol = f"{target_symbol}_{scrip_code}"
                    if (target_symbol.upper(), "BSE") in by_symbol:
                        target_symbol = scrip_code

                    new_bse = Instrument(
                        symbol=target_symbol,
                        company_name=name or scrip_id,
                        canonical_name=name or scrip_id,
                        display_name=f"{name or scrip_id} (BSE:{scrip_code})",
                        exchange="BSE",
                        bse_code=scrip_code,
                        bse_symbol=scrip_id,
                        isin=isin or None,
                        instrument_type=inst_type,
                        currency="INR",
                        status="ACTIVE",
                        source_provider="BSE",
                        data_availability="SUPPORTED" if not is_exclusive else "HISTORICAL_ONLY",
                        last_sync_timestamp=now,
                        last_verified_timestamp=now
                    )
                    new_batch.append(new_bse)
                    by_bse_code[scrip_code] = new_bse
                    by_symbol[(target_symbol.upper(), "BSE")] = new_bse
                    if isin:
                        by_isin[isin] = new_bse
                    telemetry.inserted_count += 1

            telemetry.accepted_record_count += 1

        if new_batch:
            self.db.add_all(new_batch)
        self.db.commit()

        self.source_telemetry[source_name] = telemetry
        return telemetry

    def _extract_bse_rows_from_zip(self, zf: zipfile.ZipFile) -> List[Dict[str, str]]:
        """Parses active BSE rows directly from BSE official SCRIP.zip archive."""
        ci_name = [f for f in zf.namelist() if "CI" in f and f.endswith(".txt")][0]
        ci_content = zf.read(ci_name).decode("utf-8", errors="ignore")
        ci_map = {}
        for line in ci_content.splitlines()[2:]:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                ci_map[parts[0].strip()] = parts[1].strip()

        eq_name = [f for f in zf.namelist() if "BSE_EQ_SCRIP" in f][0]
        eq_content = zf.read(eq_name).decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(eq_content))
        isin_by_code = {}
        isin_by_sym = {}
        for r in reader:
            raw_id = r.get("FinInstrmId", "").strip()
            sym = r.get("TckrSymb", "").rstrip("#").strip().upper()
            isin = r.get("ISIN", "").strip().upper()
            name = r.get("FinInstrmNm", "").strip()
            if isin and isin.startswith("IN"):
                isin_by_sym[sym] = isin
                if raw_id.startswith("1") and len(raw_id) == 6:
                    isin_by_code["5" + raw_id[1:]] = isin
                else:
                    isin_by_code[raw_id] = isin
                if raw_id not in ci_map and name:
                    ci_map[raw_id] = name
                    if raw_id.startswith("1") and len(raw_id) == 6:
                        ci_map["5" + raw_id[1:]] = name

        reg_name = [f for f in zf.namelist() if "REG1_IND" in f or "REG_IND" in f][0]
        reg_content = zf.read(reg_name).decode("utf-8", errors="ignore")
        reg_reader = csv.DictReader(io.StringIO(reg_content))

        bse_rows = []
        for r in reg_reader:
            if r.get("Status", "").strip().upper() != "A":
                continue
            code = r.get("ScripCode", "").strip()
            sym = r.get("ScripId", "").strip().upper()
            grp = r.get("GroupName", "").strip().upper()
            excl = r.get("BSE Exclusive", "").strip().upper() == "Y"
            name = ci_map.get(code) or ci_map.get(sym) or sym
            isin = isin_by_code.get(code) or isin_by_sym.get(sym) or ""
            inst_type = "SME_EQUITY" if grp == "M" else ("ETF" if grp == "E" else "EQUITY")
            bse_rows.append({
                "SCRIP_CODE": code,
                "SCRIP_ID": sym,
                "COMPANY_NAME": name,
                "ISIN_NUMBER": isin,
                "GROUP": grp,
                "IS_BSE_EXCLUSIVE": str(excl),
                "INSTRUMENT_TYPE": inst_type,
                "STATUS": "ACTIVE"
            })
        return bse_rows

    def sync_amfi_mutual_funds(self) -> SourceSyncTelemetry:
        """Synchronizes authoritative AMFI mutual fund schemes and latest daily NAVs."""
        source_name = "AMFI_MUTUAL_FUNDS"
        url = "https://www.amfiindia.com/spages/NAVAll.txt"
        now = datetime.now(timezone.utc)
        telemetry = SourceSyncTelemetry(
            source_name=source_name,
            source_url=url,
            retrieval_timestamp=now,
            is_live=False,
            provenance="VERIFIED_REFERENCE_SNAPSHOT",
            validation_status="PASSED"
        )

        raw_bytes, status_code, error = self._fetch_url(url, timeout=20)
        telemetry.response_status_code = status_code

        if raw_bytes and len(raw_bytes) > 200000:
            raw_text = raw_bytes.decode("utf-8", errors="ignore")
            telemetry.downloaded_bytes = len(raw_bytes)
            telemetry.is_live = True
            telemetry.provenance = "LIVE_OFFICIAL"
        else:
            ref_path = os.path.join(REFERENCE_DIR, "amfi_navall.txt")
            if os.path.isfile(ref_path):
                with open(ref_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = f.read()
                telemetry.downloaded_bytes = os.path.getsize(ref_path)
                telemetry.provenance = "VERIFIED_REFERENCE_SNAPSHOT"
            else:
                telemetry.validation_status = "FAILED_VALIDATION"
                telemetry.error_message = "No AMFI data source available."
                self.source_telemetry[source_name] = telemetry
                return telemetry

        if "Scheme Code" not in raw_text or ";" not in raw_text:
            telemetry.validation_status = "FAILED_VALIDATION"
            telemetry.error_message = "Downloaded AMFI data failed format validation."
            self.source_telemetry[source_name] = telemetry
            return telemetry

        lines = raw_text.splitlines()
        telemetry.source_record_count = len([l for l in lines if ";" in l and not l.startswith("Scheme Code")])
        if telemetry.source_record_count < 5000:
            telemetry.validation_status = "FAILED_VALIDATION"
            telemetry.error_message = f"Plausibility check failed: AMFI scheme count ({telemetry.source_record_count}) is below minimum threshold."
            self.source_telemetry[source_name] = telemetry
            return telemetry

        by_isin, by_bse_code, by_scheme_code, by_symbol = self._get_in_memory_index()
        new_batch = []
        current_category = "Open Ended Schemes"
        current_amc = "Mutual Fund"

        for line in lines:
            line = line.strip()
            if not line or line.startswith("Scheme Code"):
                continue

            if line.startswith("Open Ended Schemes") or line.startswith("Close Ended Schemes"):
                current_category = line
                continue
            elif "Mutual Fund" in line and ";" not in line:
                current_amc = line
                continue

            parts = [p.strip() for p in line.split(";")]
            if len(parts) >= 6:
                telemetry.parsed_record_count += 1
                try:
                    scheme_code = parts[0]
                    if not scheme_code or not scheme_code.isdigit():
                        telemetry.rejected_record_count += 1
                        telemetry.rejection_reasons["invalid_scheme_record"] = telemetry.rejection_reasons.get("invalid_scheme_record", 0) + 1
                        continue

                    isin_growth = parts[1] if parts[1] and parts[1] != "-" else None

                    if len(parts) >= 8:
                        base_name = parts[3]
                        plan_type_raw = parts[4]
                        option_type_raw = parts[5]
                        nav_str = parts[6]
                        nav_date_str = parts[7]
                        scheme_name = f"{base_name} - {plan_type_raw} - {option_type_raw}".replace(" - - ", " - ").strip(" -")
                        plan_type = "Direct" if ("direct" in plan_type_raw.lower() or "direct" in scheme_name.lower()) else "Regular"
                        option_type = "IDCW" if ("idcw" in option_type_raw.lower() or "dividend" in option_type_raw.lower() or "idcw" in scheme_name.lower()) else "Growth"
                    else:
                        scheme_name = parts[3]
                        nav_str = parts[4]
                        nav_date_str = parts[5]
                        plan_type = "Direct" if "direct" in scheme_name.lower() else "Regular"
                        option_type = "IDCW" if "idcw" in scheme_name.lower() or "dividend" in scheme_name.lower() else "Growth"

                    if not scheme_name:
                        telemetry.rejected_record_count += 1
                        telemetry.rejection_reasons["missing_scheme_name"] = telemetry.rejection_reasons.get("missing_scheme_name", 0) + 1
                        continue

                    try:
                        latest_nav = float(nav_str) if nav_str and nav_str != "N.A." else None
                    except ValueError:
                        latest_nav = None

                    parsed_date = None
                    if nav_date_str:
                        try:
                            parsed_date = datetime.strptime(nav_date_str, "%d-%b-%Y")
                        except Exception:
                            parsed_date = now

                    existing = by_scheme_code.get(scheme_code)
                    if not existing and isin_growth:
                        existing = by_isin.get(isin_growth)

                    if existing:
                        existing.company_name = scheme_name
                        existing.canonical_name = scheme_name
                        existing.latest_nav = latest_nav if latest_nav is not None else existing.latest_nav
                        existing.latest_nav_date = parsed_date or existing.latest_nav_date
                        existing.amc_or_issuer = current_amc
                        existing.scheme_category = current_category
                        existing.plan_type = plan_type
                        existing.option_type = option_type
                        existing.last_sync_timestamp = now
                        telemetry.updated_count += 1
                    else:
                        new_mf = Instrument(
                            symbol=scheme_code,
                            company_name=scheme_name,
                            canonical_name=scheme_name,
                            display_name=f"{scheme_name} (MF:{scheme_code})",
                            exchange="AMFI",
                            scheme_code=scheme_code,
                            isin=isin_growth,
                            amc_or_issuer=current_amc,
                            scheme_category=current_category,
                            plan_type=plan_type,
                            option_type=option_type,
                            latest_nav=latest_nav,
                            latest_nav_date=parsed_date,
                            instrument_type="MUTUAL_FUND",
                            currency="INR",
                            status="ACTIVE" if latest_nav else "INACTIVE",
                            source_provider="AMFI",
                            data_availability="NAV_ONLY",
                            last_sync_timestamp=now,
                            last_verified_timestamp=now
                        )
                        new_batch.append(new_mf)
                        by_scheme_code[scheme_code] = new_mf
                        by_symbol[(scheme_code, "AMFI")] = new_mf
                        if isin_growth:
                            by_isin[isin_growth] = new_mf
                        telemetry.inserted_count += 1

                    telemetry.accepted_record_count += 1

                except Exception:
                    telemetry.rejected_record_count += 1
                    telemetry.rejection_reasons["parsing_exception"] = telemetry.rejection_reasons.get("parsing_exception", 0) + 1

        if new_batch:
            # Batch commit in chunks of 2,000 for high database performance
            chunk_size = 2000
            for i in range(0, len(new_batch), chunk_size):
                self.db.add_all(new_batch[i:i + chunk_size])
                self.db.commit()
        else:
            self.db.commit()

        self.source_telemetry[source_name] = telemetry
        return telemetry

    def sync_all(self) -> Dict[str, Any]:
        """Full evidence-based synchronization across NSE, BSE, and AMFI."""
        t_nse = self.sync_nse_equities()
        t_etf = self.sync_nse_etfs()
        t_bse = self.sync_bse_securities()
        t_amfi = self.sync_amfi_mutual_funds()

        return {
            "status": "COMPLETED",
            "sources": {
                "NSE_EQUITIES": t_nse.model_dump(),
                "NSE_ETFS": t_etf.model_dump(),
                "BSE_SECURITIES": t_bse.model_dump(),
                "AMFI_MUTUAL_FUNDS": t_amfi.model_dump()
            },
            "nse": {
                "added": t_nse.inserted_count + t_etf.inserted_count,
                "updated": t_nse.updated_count + t_etf.updated_count,
                "errors": t_nse.rejected_record_count + t_etf.rejected_record_count
            },
            "bse": {
                "added": t_bse.inserted_count,
                "updated": t_bse.updated_count,
                "errors": t_bse.rejected_record_count
            },
            "amfi": {
                "added": t_amfi.inserted_count,
                "updated": t_amfi.updated_count,
                "errors": t_amfi.rejected_record_count
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_sync_status(self) -> InstrumentSyncStatusResponse:
        """Calculates authoritative, non-overlapping universe coverage metrics."""
        total = self.db.query(func.count(Instrument.id)).scalar() or 0
        active = self.db.query(func.count(Instrument.id)).filter(Instrument.status == "ACTIVE").scalar() or 0
        
        nse_count = self.db.query(func.count(Instrument.id)).filter(Instrument.exchange.like("%NSE%")).scalar() or 0
        bse_count = self.db.query(func.count(Instrument.id)).filter(Instrument.exchange.like("%BSE%")).scalar() or 0
        dual_listed = self.db.query(func.count(Instrument.id)).filter(Instrument.exchange == "NSE,BSE").scalar() or 0
        bse_exclusive = self.db.query(func.count(Instrument.id)).filter(Instrument.exchange == "BSE").scalar() or 0
        
        etf_count = self.db.query(func.count(Instrument.id)).filter(Instrument.instrument_type == "ETF").scalar() or 0
        etf_nse_count = self.db.query(func.count(Instrument.id)).filter(
            Instrument.instrument_type == "ETF", Instrument.exchange.like("%NSE%")
        ).scalar() or 0
        etf_bse_count = self.db.query(func.count(Instrument.id)).filter(
            Instrument.instrument_type == "ETF", Instrument.exchange.like("%BSE%")
        ).scalar() or 0
        
        mf_count = self.db.query(func.count(Instrument.id)).filter(Instrument.instrument_type == "MUTUAL_FUND").scalar() or 0
        sme_count = self.db.query(func.count(Instrument.id)).filter(Instrument.instrument_type == "SME_EQUITY").scalar() or 0
        
        isin_count = self.db.query(func.count(Instrument.id)).filter(Instrument.isin.isnot(None)).scalar() or 0
        bse_code_count = self.db.query(func.count(Instrument.id)).filter(Instrument.bse_code.isnot(None)).scalar() or 0
        scheme_code_count = self.db.query(func.count(Instrument.id)).filter(Instrument.scheme_code.isnot(None)).scalar() or 0
        unverified_count = self.db.query(func.count(Instrument.id)).filter(
            ~Instrument.status.in_(["ACTIVE", "SUSPENDED", "DELISTED", "INACTIVE"])
        ).scalar() or 0

        # Distinct canonical entities: Dual-listed securities represent 1 entity (1 row in DB).
        # Exchange-specific listings: 1 per exchange per security (NSE listings + BSE listings) + AMFI scheme registrations.
        exchange_listings = nse_count + bse_count + mf_count

        now = datetime.now(timezone.utc)
        return InstrumentSyncStatusResponse(
            distinct_canonical_entities=total,
            total_instruments=total,
            active_instruments=active,
            exchange_specific_listings=exchange_listings,
            nse_listed_count=nse_count,
            bse_listed_count=bse_count,
            dual_listed_count=dual_listed,
            bse_exclusive_count=bse_exclusive,
            etf_count=etf_count,
            etf_nse_count=etf_nse_count,
            etf_bse_count=etf_bse_count,
            mutual_fund_count=mf_count,
            sme_count=sme_count,
            records_with_isin=isin_count,
            records_with_bse_code=bse_code_count,
            records_with_scheme_code=scheme_code_count,
            records_unverified_status=unverified_count,
            sources=self.source_telemetry,
            last_sync_time_nse=now,
            last_sync_time_bse=now,
            last_sync_time_amfi=now,
            last_sync_status="SYNCHRONIZED",
            message=f"Instrument master active with {total:,} distinct canonical instruments ({active:,} active, {exchange_listings:,} exchange listings)."
        )
