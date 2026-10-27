from typing import List, Optional
import re
from sqlalchemy.orm import Session
from app.db.repositories.instrument_repo import InstrumentRepository
from app.schemas.instrument import (
    InstrumentResponse,
    InstrumentResolutionResult,
    InstrumentCandidate,
    InstrumentCreate
)

SEED_INSTRUMENTS = [
    {
        "exchange": "NSE",
        "symbol": "GREENPOWER",
        "company_name": "Orient Green Power Company Limited",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Utilities",
        "industry": "Renewable Energy",
        "isin": "INE999K01014"
    },
    {
        "exchange": "NSE",
        "symbol": "RELIANCE",
        "company_name": "Reliance Industries Limited",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Energy",
        "industry": "Oil, Gas & Consumable Fuels",
        "isin": "INE002A01018"
    },
    {
        "exchange": "NSE",
        "symbol": "TATAMOTORS",
        "company_name": "Tata Motors Limited",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Consumer Discretionary",
        "industry": "Automobiles",
        "isin": "INE155A01022"
    },
    {
        "exchange": "NSE",
        "symbol": "TATASTEEL",
        "company_name": "Tata Steel Limited",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Materials",
        "industry": "Metals & Mining",
        "isin": "INE081A01020"
    },
    {
        "exchange": "NSE",
        "symbol": "TATAPOWER",
        "company_name": "Tata Power Company Limited",
        "instrument_type": "EQUITY",
        "currency": "INR",
        "sector": "Utilities",
        "industry": "Electric Utilities",
        "isin": "INE245A01021"
    },
    {
        "exchange": "NSE",
        "symbol": "INFY",
        "company_name": "Infosys Limited",
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
        "instrument_type": "INDEX",
        "currency": "INR",
        "sector": "Indices",
        "industry": "Broad Market Benchmark",
        "isin": "IN0000000001"
    }
]

class InstrumentService:
    def __init__(self, db: Session):
        self.repo = InstrumentRepository(db)
        self._ensure_seed_data()

    def _ensure_seed_data(self):
        for item in SEED_INSTRUMENTS:
            existing = self.repo.get_by_symbol_and_exchange(item["symbol"], item["exchange"])
            if not existing:
                self.repo.create(InstrumentCreate(**item))

    def resolve_instrument(self, query: str, explicit_symbol: Optional[str] = None) -> InstrumentResolutionResult:
        """
        Resolves a company name or ticker to an authoritative instrument.
        Detects ambiguity and prevents silent substitution.
        """
        if explicit_symbol:
            match = self.repo.get_by_symbol_and_exchange(explicit_symbol.strip().upper())
            if match:
                return InstrumentResolutionResult(
                    resolved=True,
                    instrument=InstrumentResponse.model_validate(match),
                    message=f"Resolved directly via symbol: {match.exchange}:{match.symbol}"
                )

        cleaned_query = query.strip()
        # Direct symbol check
        words = re.findall(r"[A-Za-z0-9\^]+", cleaned_query)
        for w in words:
            match = self.repo.get_by_symbol_and_exchange(w.upper())
            if match:
                return InstrumentResolutionResult(
                    resolved=True,
                    instrument=InstrumentResponse.model_validate(match),
                    message=f"Resolved via symbol token: {match.exchange}:{match.symbol}"
                )

        # Multi-word search
        matches = self.repo.search(cleaned_query, limit=10)
        if not matches:
            # Check individual keywords for candidate matches
            for w in words:
                if len(w) > 3:
                    sub_matches = self.repo.search(w, limit=5)
                    for sm in sub_matches:
                        if sm not in matches:
                            matches.append(sm)

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

        # Score matches based on token overlap and phrase containment
        scored_matches = []
        q_lower = cleaned_query.lower()
        query_words = set(re.findall(r"[a-z0-9]+", q_lower))

        for m in matches:
            c_name_lower = m.company_name.lower()
            # Clean generic legal entity suffixes
            brand_name = c_name_lower.replace(" company limited", "").replace(" limited", "").strip()
            score = 0.0

            # Direct phrase containment
            if brand_name in q_lower:
                score += 5.0 + len(brand_name.split())
            elif m.symbol.lower() in query_words:
                score += 5.0
            else:
                brand_words = set(re.findall(r"[a-z0-9]+", brand_name))
                overlap = query_words.intersection(brand_words)
                # Ignore very common generic words if matched alone
                significant_overlap = [w for w in overlap if w not in ("company", "limited", "india", "the")]
                score += len(significant_overlap)

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
        if top_score >= 3.0 and top_score > second_score + 1.0:
            return InstrumentResolutionResult(
                resolved=True,
                instrument=InstrumentResponse.model_validate(top_match),
                message=f"Resolved to {top_match.exchange}:{top_match.symbol} ({top_match.company_name})"
            )

        # Ambiguous matches with tied or close scores (e.g. 'Tata' matching Tata Motors, Tata Steel, Tata Power)
        candidates = [
            InstrumentCandidate(
                symbol=m.symbol,
                company_name=m.company_name,
                exchange=m.exchange,
                confidence=round(min(1.0, s / (top_score + 1e-5)), 2)
            ) for s, m in scored_matches if s > 0
        ]

        return InstrumentResolutionResult(
            resolved=False,
            requires_clarification=True,
            candidates=candidates,
            message=f"Ambiguous query '{cleaned_query}'. Multiple instruments matched. Please clarify which company you intended."
        )

    def search_instruments(self, query: str, limit: int = 10) -> List[InstrumentResponse]:
        results = self.repo.search(query, limit=limit)
        return [InstrumentResponse.model_validate(r) for r in results]

    def get_by_id(self, instrument_id: str) -> Optional[InstrumentResponse]:
        item = self.repo.get_by_id(instrument_id)
        return InstrumentResponse.model_validate(item) if item else None
