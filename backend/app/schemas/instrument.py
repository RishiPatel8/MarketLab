from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class InstrumentBase(BaseModel):
    exchange: str = Field(default="NSE", description="Exchange code: NSE, BSE, NSE,BSE, or AMFI")
    symbol: str = Field(..., description="Primary identifier or ticker")
    company_name: str = Field(..., description="Full legal company or scheme name")
    canonical_name: Optional[str] = None
    display_name: Optional[str] = None
    instrument_type: str = Field(default="EQUITY", description="EQUITY, SME_EQUITY, ETF, MUTUAL_FUND, INDEX")
    currency: str = Field(default="INR")
    sector: Optional[str] = None
    industry: Optional[str] = None
    isin: Optional[str] = None
    
    # Dual-listing and exchange-specific identifiers
    nse_symbol: Optional[str] = None
    bse_code: Optional[str] = None
    bse_symbol: Optional[str] = None
    
    # Mutual fund specific metadata
    scheme_code: Optional[str] = None
    amc_or_issuer: Optional[str] = None
    scheme_category: Optional[str] = None
    plan_type: Optional[str] = None
    option_type: Optional[str] = None
    latest_nav: Optional[float] = None
    latest_nav_date: Optional[datetime] = None

    # Status and data availability
    status: Optional[str] = Field(default="ACTIVE")
    source_provider: Optional[str] = Field(default="NSE")
    source_record_identifier: Optional[str] = None
    data_availability: Optional[str] = Field(default="SUPPORTED", description="SUPPORTED, UNAVAILABLE, NAV_ONLY")
    aliases: Optional[str] = None

class InstrumentCreate(InstrumentBase):
    pass

class InstrumentUpdate(BaseModel):
    canonical_name: Optional[str] = None
    display_name: Optional[str] = None
    exchange: Optional[str] = None
    nse_symbol: Optional[str] = None
    bse_code: Optional[str] = None
    bse_symbol: Optional[str] = None
    isin: Optional[str] = None
    latest_nav: Optional[float] = None
    latest_nav_date: Optional[datetime] = None
    status: Optional[str] = None
    data_availability: Optional[str] = None
    last_sync_timestamp: Optional[datetime] = None
    last_verified_timestamp: Optional[datetime] = None

class InstrumentResponse(InstrumentBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    last_sync_timestamp: Optional[datetime] = None
    last_verified_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class PaginatedInstrumentsResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[InstrumentResponse]

class SourceSyncTelemetry(BaseModel):
    source_name: str
    source_url: str
    retrieval_timestamp: datetime
    source_file_date: Optional[str] = None
    response_status_code: Optional[int] = None
    downloaded_bytes: int = 0
    source_record_count: int = 0
    parsed_record_count: int = 0
    accepted_record_count: int = 0
    rejected_record_count: int = 0
    rejection_reasons: Dict[str, int] = Field(default_factory=dict)
    duplicate_count: int = 0
    inserted_count: int = 0
    updated_count: int = 0
    unchanged_count: int = 0
    is_live: bool = False
    provenance: str = "LIVE_OFFICIAL"
    validation_status: str = "PASSED"
    error_message: Optional[str] = None

class InstrumentSyncStatusResponse(BaseModel):
    distinct_canonical_entities: int = 0
    total_instruments: int
    active_instruments: int
    exchange_specific_listings: int = 0
    nse_listed_count: int
    bse_listed_count: int
    dual_listed_count: int
    bse_exclusive_count: int
    etf_count: int
    etf_nse_count: int = 0
    etf_bse_count: int = 0
    mutual_fund_count: int
    sme_count: int
    records_with_isin: int
    records_with_bse_code: int = 0
    records_with_scheme_code: int = 0
    records_unverified_status: int = 0
    sources: Dict[str, SourceSyncTelemetry] = Field(default_factory=dict)
    last_sync_time_nse: Optional[datetime] = None
    last_sync_time_bse: Optional[datetime] = None
    last_sync_time_amfi: Optional[datetime] = None
    last_sync_status: str
    message: str

class InstrumentCandidate(BaseModel):
    id: Optional[str] = None
    symbol: str
    company_name: str
    exchange: str
    instrument_type: str = "EQUITY"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    match_reason: Optional[str] = None
    data_availability: str = "SUPPORTED"

class InstrumentResolutionResult(BaseModel):
    resolved: bool
    requires_clarification: bool = False
    instrument: Optional[InstrumentResponse] = None
    candidates: List[InstrumentCandidate] = []
    message: str
