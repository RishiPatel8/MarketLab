from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import MarketLabException
from app.db.session import sync_engine, Base, SyncSessionLocal, ensure_schema_migrations
import app.db.models
from app.services.instrument_service import InstrumentService
from app.services.rag_service import RAGService
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Initializing MarketLab AI backend...")
    # Initialize DB tables
    Base.metadata.create_all(bind=sync_engine)
    ensure_schema_migrations(sync_engine)
    # Seed default instruments and regulatory filings
    with SyncSessionLocal() as db:
        InstrumentService(db)
        RAGService(db)
    logger.info("MarketLab AI initialization complete. System ready.")
    yield
    logger.info("MarketLab AI shutting down.")

app = FastAPI(
    title="MarketLab AI — API",
    description="AI-powered stock research and strategy validation platform for Indian equities.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(MarketLabException)
async def marketlab_exception_handler(request: Request, exc: MarketLabException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.__class__.__name__, "message": exc.message, "details": exc.details}
    )

# Health Checks
@app.get("/health/live", tags=["Health"])
def health_live():
    return {"status": "alive", "timestamp": "ok"}

@app.get("/health/ready", tags=["Health"])
def health_ready():
    # Verify DB connectivity
    try:
        with SyncSessionLocal() as db:
            db.execute(app.db.models.Instrument.__table__.select().limit(1))
        return {"status": "ready", "database": "connected", "engine": "MarketLab 1.0"}
    except Exception as e:
        # Fallback to direct Instrument model
        try:
            from app.db.models import Instrument
            with SyncSessionLocal() as db:
                db.query(Instrument).first()
            return {"status": "ready", "database": "connected", "engine": "MarketLab 1.0"}
        except Exception as inner_e:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "not_ready", "error": str(inner_e)}
            )

# API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)
