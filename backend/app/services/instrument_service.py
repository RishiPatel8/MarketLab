from typing import List, Optional, Tuple
import re
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.repositories.instrument_repo import InstrumentRepository
from app.db.models.instrument import Instrument
from app.schemas.instrument import (
    InstrumentResponse,
    InstrumentResolutionResult,
    InstrumentCandidate,
    InstrumentCreate,
    PaginatedInstrumentsResponse,
    InstrumentSyncStatusResponse
)
from app.services.instrument_sync_service import InstrumentSyncService

SEED_INSTRUMENTS = [
    {
        "exchange": "NSE",
        "symbol": "GREENPOWER",
        "company_name": "Orient Green Power Company Limited",
        "canonical_name": "Orient Green Power Company Limited",
        "display_name": "Orient Green Power Company Limited (GREENPOWER)",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Utilities",
        "industry": "Renewable Energy",
        "isin": "INE999K01014"
    },
    {
        "exchange": "NSE,BSE",
        "symbol": "RELIANCE",
        "company_name": "Reliance Industries Limited",
        "canonical_name": "Reliance Industries Limited",
        "display_name": "Reliance Industries Limited (RELIANCE)",
        "nse_symbol": "RELIANCE",
        "bse_code": "500325",
        "bse_symbol": "RELIANCE",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Energy",
        "industry": "Oil, Gas & Consumable Fuels",
        "isin": "INE002A01018"
    },
    {
        "exchange": "NSE,BSE",
        "symbol": "TATAMOTORS",
        "company_name": "Tata Motors Limited",
        "canonical_name": "Tata Motors Limited",
        "display_name": "Tata Motors Limited (TATAMOTORS)",
        "nse_symbol": "TATAMOTORS",
        "bse_code": "500570",
        "bse_symbol": "TATAMOTORS",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Consumer Discretionary",
        "industry": "Automobiles",
        "isin": "INE155A01022"
    },
    {
        "exchange": "NSE,BSE",
        "symbol": "TATASTEEL",
        "company_name": "Tata Steel Limited",
        "canonical_name": "Tata Steel Limited",
        "display_name": "Tata Steel Limited (TATASTEEL)",
        "nse_symbol": "TATASTEEL",
        "bse_code": "500470",
        "bse_symbol": "TATASTEEL",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Materials",
        "industry": "Metals & Mining",
        "isin": "INE081A01020"
    },
    {
        "exchange": "NSE,BSE",
        "symbol": "TATAPOWER",
        "company_name": "Tata Power Company Limited",
        "canonical_name": "Tata Power Company Limited",
        "display_name": "Tata Power Company Limited (TATAPOWER)",
        "nse_symbol": "TATAPOWER",
        "bse_code": "500400",
        "bse_symbol": "TATAPOWER",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Utilities",
        "industry": "Electric Utilities",
        "isin": "INE245A01021"
    },
    {
        "exchange": "NSE,BSE",
        "symbol": "INFY",
        "company_name": "Infosys Limited",
        "canonical_name": "Infosys Limited",
        "display_name": "Infosys Limited (INFY)",
        "nse_symbol": "INFY",
        "bse_code": "500209",
        "bse_symbol": "INFY",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Information Technology",
        "industry": "IT Services & Consulting",
        "isin": "INE009A01021"
    },
    {
        "exchange": "NSE",
        "symbol": "^NSEI",
        "company_name": "Nifty 50 Benchmark Index",
        "canonical_name": "Nifty 50 Benchmark Index",
        "display_name": "Nifty 50 Benchmark Index (^NSEI)",
        "instrument_type": "INDEX",
        "currency": "INR",
        "sector": "Indices",
        "industry": "Broad Market Benchmark",
        "isin": "IN0000000001"
    },
    {
        "exchange": "BSE",
        "symbol": "^BSESN",
        "company_name": "BSE SENSEX Benchmark Index",
        "canonical_name": "BSE SENSEX Benchmark Index",
        "display_name": "BSE SENSEX Benchmark Index (^BSESN)",
        "instrument_type": "INDEX",
        "currency": "INR",
        "sector": "Indices",
        "industry": "BSE 30 Blue Chip Benchmark",
        "isin": "IN0000000002"
    },
    {
        "exchange": "NSE",
        "symbol": "^NSEBANK",
        "company_name": "NIFTY Bank Index",
        "canonical_name": "NIFTY Bank Index",
        "display_name": "NIFTY Bank Index (^NSEBANK)",
        "instrument_type": "INDEX",
        "currency": "INR",
        "sector": "Indices",
        "industry": "Banking Sector Index",
        "isin": "IN0000000003"
    },
    {
        "exchange": "NSE",
        "symbol": "^CNXIT",
        "company_name": "NIFTY IT Index",
        "canonical_name": "NIFTY IT Index",
        "display_name": "NIFTY IT Index (^CNXIT)",
        "instrument_type": "INDEX",
        "currency": "INR",
        "sector": "Indices",
        "industry": "Information Technology Sector",
        "isin": "IN0000000004"
    },
    {
        "exchange": "NSE",
        "symbol": "^INDIAVIX",
        "company_name": "India VIX Volatility Index",
        "canonical_name": "India VIX Volatility Index",
        "display_name": "India VIX Volatility Index (^INDIAVIX)",
        "instrument_type": "INDEX",
        "currency": "INR",
        "sector": "Indices",
        "industry": "Market Volatility Gauge",
        "isin": "IN0000000005"
    },
    {
        "exchange": "NSE",
        "symbol": "^CRSLDX",
        "company_name": "NIFTY 500 Broad Market Index",
        "canonical_name": "NIFTY 500 Broad Market Index",
        "display_name": "NIFTY 500 Index (^CRSLDX)",
        "instrument_type": "INDEX",
        "currency": "INR",
        "sector": "Indices",
        "industry": "Broad Market 500 Index",
        "isin": "IN0000000006"
    }
]

class InstrumentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InstrumentRepository(db)
        self.sync_service = InstrumentSyncService(db)
        self._ensure_universe_data()

    def _ensure_universe_data(self):
        """Ensures the full Indian instrument universe is synchronized on first startup."""
        count = self.db.query(func.count(Instrument.id)).scalar() or 0
        if count < 50:
            # Sync seed records first
            for item in SEED_INSTRUMENTS:
                existing = self.repo.get_by_symbol_and_exchange(item["symbol"], item["exchange"])
                if not existing:
                    self.repo.create(InstrumentCreate(**item))
            # Run initial synchronization of full Indian universe
            self.sync_service.sync_all()

    def search_instruments(
        self,
        query: str,
        instrument_type: Optional[str] = None,
        exchange: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> PaginatedInstrumentsResponse:
        """Searches instruments with multi-field matching, filters, and pagination."""
        items, total = self.repo.search_advanced(
            query_str=query,
            instrument_type=instrument_type,
            exchange=exchange,
            page=page,
            limit=limit
        )
        return PaginatedInstrumentsResponse(
            total=total,
            page=page,
            limit=limit,
            items=[InstrumentResponse.model_validate(item) for item in items]
        )

    def resolve_instrument(self, query: str, explicit_symbol: Optional[str] = None) -> InstrumentResolutionResult:
        """
        Authoritatively resolves an instrument query.
        Directly checks ISINs, BSE scrip codes, AMFI scheme codes, and symbol tokens before fallback to scored ranking.
        Flags ambiguous queries (e.g. 'Tata') requiring user clarification.
        """
        cleaned_query = query.strip()
        
        # 1. Direct explicit symbol / code lookup
        check_symbol = explicit_symbol.strip() if explicit_symbol else None
        if not check_symbol and len(cleaned_query) <= 12 and not " " in cleaned_query:
            check_symbol = cleaned_query

        if check_symbol:
            # Check by ISIN (12 chars starting with IN)
            if re.match(r"^IN[A-Z0-9]{10}$", check_symbol.upper()):
                match = self.repo.get_by_isin(check_symbol.upper())
                if match:
                    return InstrumentResolutionResult(
                        resolved=True,
                        instrument=InstrumentResponse.model_validate(match),
                        message=f"Resolved directly via ISIN: {match.isin} ({match.company_name})"
                    )

            # Check by BSE 6-digit scrip code
            if re.match(r"^\d{6}$", check_symbol):
                bse_match = self.repo.get_by_bse_code(check_symbol)
                if bse_match:
                    return InstrumentResolutionResult(
                        resolved=True,
                        instrument=InstrumentResponse.model_validate(bse_match),
                        message=f"Resolved directly via BSE code {check_symbol}: {bse_match.company_name}"
                    )
                # Check AMFI scheme code
                mf_match = self.repo.get_by_scheme_code(check_symbol)
                if mf_match:
                    return InstrumentResolutionResult(
                        resolved=True,
                        instrument=InstrumentResponse.model_validate(mf_match),
                        message=f"Resolved directly via AMFI Scheme Code {check_symbol}: {mf_match.company_name}"
                    )

            # Check by symbol
            match = self.repo.get_by_symbol_and_exchange(check_symbol.upper())
            if match:
                return InstrumentResolutionResult(
                    resolved=True,
                    instrument=InstrumentResponse.model_validate(match),
                    message=f"Resolved directly via symbol: {match.exchange}:{match.symbol}"
                )

        common_words = {
            "FOR", "ARE", "THE", "CAN", "AND", "NOT", "BUY", "SELL", "HOLD", "OUT", "RUN", "NEW",
            "TOP", "LOW", "BIG", "PER", "NET", "SET", "NOW", "ALL", "DAY", "DAYS", "SIX", "ONE",
            "TWO", "TEN", "MAX", "MIN", "CAP", "INR", "RS", "HORIZON", "MONTH", "MONTHS", "YEAR",
            "YEARS", "RESEARCH", "INVEST", "RISK", "WANT", "TEST", "WITH", "TELL", "ENTRY", "EXIT",
            "STOCK", "SHARE", "PRICE", "RATE", "HIGH", "GOOD", "BEST", "LONG", "TERM", "SHORT",
            "WELL", "REAL", "FREE", "CASH", "FLOW", "DEBT", "FUND", "PEER", "VIEW", "PLAN"
        }

        # Check if the query contains an explicit parenthesized ticker, e.g. (GREENPOWER), (RELIANCE), (500325)
        paren_symbols = re.findall(r"\(([A-Za-z0-9\^]{2,15})\)", cleaned_query)
        for ps in paren_symbols:
            ps_upper = ps.upper()
            if ps_upper not in common_words:
                match = (
                    self.repo.get_by_symbol_and_exchange(ps_upper)
                    or self.repo.get_by_bse_code(ps_upper)
                    or self.repo.get_by_scheme_code(ps_upper)
                    or self.repo.get_by_isin(ps_upper)
                )
                if match:
                    return InstrumentResolutionResult(
                        resolved=True,
                        instrument=InstrumentResponse.model_validate(match),
                        message=f"Resolved directly via parenthesized symbol ({match.symbol}): {match.company_name}"
                    )

        # 2. Tokenize and search
        tokens = re.findall(r"[A-Za-z0-9\^]+", cleaned_query)
        for t in tokens:
            t_upper = t.upper()
            # If token is ISIN
            if re.match(r"^IN[A-Z0-9]{10}$", t_upper):
                match = self.repo.get_by_isin(t_upper)
                if match:
                    return InstrumentResolutionResult(
                        resolved=True,
                        instrument=InstrumentResponse.model_validate(match),
                        message=f"Resolved via ISIN token: {match.isin} ({match.company_name})"
                    )
            # If token is BSE scrip code / AMFI code
            if re.match(r"^\d{6}$", t):
                match = self.repo.get_by_bse_code(t) or self.repo.get_by_scheme_code(t)
                if match:
                    return InstrumentResolutionResult(
                        resolved=True,
                        instrument=InstrumentResponse.model_validate(match),
                        message=f"Resolved via identifier token: {match.company_name}"
                    )
            # Direct ticker token match for prominent symbols
            if len(t) >= 4 and t_upper not in common_words:
                match = self.repo.get_by_symbol_and_exchange(t_upper)
                if match:
                    is_exact_upper = (t == t_upper)
                    company_words = [cw.lower() for cw in match.company_name.split() if len(cw) >= 3 and cw.lower() not in ("company", "limited", "ltd")]
                    has_company_mention = any(cw in cleaned_query.lower() for cw in company_words)
                    if len(cleaned_query.split()) <= 3 or is_exact_upper or has_company_mention:
                        return InstrumentResolutionResult(
                            resolved=True,
                            instrument=InstrumentResponse.model_validate(match),
                            message=f"Resolved via symbol token: {match.exchange}:{match.symbol} ({match.company_name})"
                        )

        # 3. Clean natural language prompt words to isolate company/instrument name
        stop_words = {
            "i", "want", "to", "invest", "in", "run", "multiple", "strategies", "simulate", "different",
            "scenarios", "and", "tell", "me", "whether", "the", "current", "price", "is", "suitable",
            "for", "entering", "entry", "exit", "about", "what", "do", "you", "think", "of", "should",
            "buy", "sell", "hold", "please", "with", "at", "target", "stop", "loss", "my", "money",
            "capital", "analyze", "research", "study", "investigate", "evaluate", "report", "on",
            "a", "six", "three", "twelve", "one", "month", "months", "year", "years",
            "horizon", "days", "day", "stock", "equity", "share", "shares", "company", "limited", "ltd",
            "approach", "perspective", "view", "trading", "investment", "rupees", "rs", "inr",
            "moderate", "conservative", "aggressive", "risk", "tolerance", "profile", "scenario"
        }
        query_without_parens = re.sub(r"\([^\)]*\)", " ", cleaned_query)
        extracted_tokens = [w for w in re.findall(r"[A-Za-z\^]+", query_without_parens) if w.lower() not in stop_words and len(w) >= 3]
        search_target = " ".join(extracted_tokens) if extracted_tokens else cleaned_query

        # Multi-word search with both stripped search_target and fallback to cleaned_query
        matches, _ = self.repo.search_advanced(search_target, limit=20)
        if not matches and search_target != cleaned_query:
            matches, _ = self.repo.search_advanced(cleaned_query, limit=20)

        # If still no matches, try searching individual significant tokens
        if not matches and extracted_tokens:
            for tok in extracted_tokens:
                if len(tok) >= 3:
                    tok_matches, _ = self.repo.search_advanced(tok, limit=10)
                    if tok_matches:
                        matches = tok_matches
                        break

        if not matches:
            return InstrumentResolutionResult(
                resolved=False,
                requires_clarification=False,
                candidates=[],
                message=f"No matching instrument found for query: '{cleaned_query}'"
            )

        if len(matches) == 1:
            return InstrumentResolutionResult(
                resolved=True,
                instrument=InstrumentResponse.model_validate(matches[0]),
                message=f"Resolved uniquely to {matches[0].exchange}:{matches[0].symbol} ({matches[0].company_name})"
            )

        # 4. Score candidate matches
        q_lower = search_target.lower()
        full_q_lower = cleaned_query.lower()
        query_words = set(re.findall(r"[a-z0-9]+", q_lower))
        scored_matches = []

        for m in matches:
            c_name_lower = m.company_name.lower()
            brand_name = c_name_lower.replace(" company limited", "").replace(" limited", "").replace(" ltd.", "").strip()
            score = 0.0

            if m.symbol.lower() == q_lower or (m.nse_symbol and m.nse_symbol.lower() == q_lower):
                score += 10.0
            elif m.symbol.lower() in [t.lower() for t in tokens]:
                score += 12.0
            elif brand_name in full_q_lower:
                score += 10.0 + len(brand_name.split())
            elif brand_name == q_lower or brand_name in q_lower:
                score += 8.0 + len(brand_name.split())
            else:
                brand_words = set(re.findall(r"[a-z0-9]+", brand_name))
                overlap = query_words.intersection(brand_words)
                significant_overlap = [w for w in overlap if w not in ("company", "limited", "ltd", "india", "the", "fund", "direct", "plan")]
                score += len(significant_overlap) * 2.0

            scored_matches.append((score, m))

        scored_matches.sort(key=lambda x: x[0], reverse=True)

        if not scored_matches or scored_matches[0][0] == 0:
            return InstrumentResolutionResult(
                resolved=False,
                requires_clarification=False,
                candidates=[],
                message=f"No matching instrument found for query: '{cleaned_query}'"
            )

        top_score, top_match = scored_matches[0]
        second_score = scored_matches[1][0] if len(scored_matches) > 1 else 0.0

        # Unambiguous winner
        if top_score >= 5.0 and top_score > second_score + 2.0:
            return InstrumentResolutionResult(
                resolved=True,
                instrument=InstrumentResponse.model_validate(top_match),
                message=f"Resolved to {top_match.exchange}:{top_match.symbol} ({top_match.company_name})"
            )

        # Ambiguous query (e.g. 'Tata', 'Reliance', 'HDFC' with multiple listed entities or schemes)
        def tie_breaker(item):
            s, m = item
            prominence = 3.0 if m.symbol in ("TATAMOTORS", "TATASTEEL", "TATAPOWER", "TCS", "RELIANCE", "INFY", "HDFCBANK", "GREENPOWER") else 0.0
            return (s + prominence)

        scored_matches.sort(key=tie_breaker, reverse=True)
        candidates = [
            InstrumentCandidate(
                id=m.id,
                symbol=m.symbol,
                company_name=m.company_name,
                exchange=m.exchange,
                instrument_type=m.instrument_type,
                confidence=round(min(1.0, s / (top_score + 1e-5)), 2),
                data_availability=m.data_availability
            ) for s, m in scored_matches[:8] if s > 0
        ]

        return InstrumentResolutionResult(
            resolved=False,
            requires_clarification=True,
            candidates=candidates,
            message=f"Ambiguous query '{cleaned_query}'. Multiple instruments matched across Indian exchanges and schemes. Please clarify which entity you intended."
        )

    def get_by_id(self, instrument_id: str) -> Optional[InstrumentResponse]:
        item = self.repo.get_by_id(instrument_id)
        return InstrumentResponse.model_validate(item) if item else None

    def get_sync_status(self) -> InstrumentSyncStatusResponse:
        return self.sync_service.get_sync_status()

    def trigger_sync(self):
        return self.sync_service.sync_all()
