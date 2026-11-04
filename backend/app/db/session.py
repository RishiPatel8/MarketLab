from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Base class for SQLAlchemy declarative models
Base = declarative_base()

import os

# Resolve URLs for sync and async
db_url = settings.DATABASE_URL
if "sqlite" in db_url and "./" in db_url:
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    db_file = os.path.join(backend_dir, "marketlab.db").replace("\\", "/")
    db_url = f"sqlite+aiosqlite:///{db_file}"

if db_url.startswith("postgresql://"):
    db_url_sync = db_url.replace("postgresql://", "postgresql+psycopg://")
    db_url_async = db_url.replace("postgresql://", "postgresql+psycopg://")
elif db_url.startswith("postgresql+psycopg://"):
    db_url_sync = db_url
    db_url_async = db_url
elif db_url.startswith("sqlite+aiosqlite://"):
    db_url_async = db_url
    db_url_sync = db_url.replace("sqlite+aiosqlite://", "sqlite://")
elif db_url.startswith("sqlite://"):
    db_url_sync = db_url
    db_url_async = db_url.replace("sqlite://", "sqlite+aiosqlite://")
else:
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    db_file = os.path.join(backend_dir, "marketlab.db").replace("\\", "/")
    db_url_sync = f"sqlite:///{db_file}"
    db_url_async = f"sqlite+aiosqlite:///{db_file}"

# Sync Engine (used for migrations, fixtures, quant scripts, sync handlers)
sync_engine = create_engine(
    db_url_sync,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in db_url_sync else {}
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async Engine (used for FastAPI async dependencies)
async_engine = create_async_engine(
    db_url_async,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in db_url_async else {}
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

def ensure_schema_migrations(engine=sync_engine):
    """Ensures newly added columns exist in SQLite instances."""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            if "sqlite" in str(engine.url):
                # 1. instruments table
                res_inst = conn.execute(text("PRAGMA table_info(instruments)")).fetchall()
                existing_inst = {r[1] for r in res_inst}
                inst_defs = [
                    ('canonical_name', 'VARCHAR(255)'),
                    ('display_name', 'VARCHAR(255)'),
                    ('nse_symbol', 'VARCHAR(50)'),
                    ('bse_code', 'VARCHAR(20)'),
                    ('bse_symbol', 'VARCHAR(50)'),
                    ('scheme_code', 'VARCHAR(30)'),
                    ('amc_or_issuer', 'VARCHAR(255)'),
                    ('scheme_category', 'VARCHAR(100)'),
                    ('plan_type', 'VARCHAR(30)'),
                    ('option_type', 'VARCHAR(30)'),
                    ('latest_nav', 'FLOAT'),
                    ('latest_nav_date', 'DATETIME'),
                    ('status', 'VARCHAR(20) DEFAULT "ACTIVE"'),
                    ('source_provider', 'VARCHAR(50) DEFAULT "NSE"'),
                    ('source_record_identifier', 'VARCHAR(100)'),
                    ('data_availability', 'VARCHAR(50) DEFAULT "SUPPORTED"'),
                    ('aliases', 'VARCHAR(500)'),
                    ('last_sync_timestamp', 'DATETIME'),
                    ('last_verified_timestamp', 'DATETIME'),
                    ('updated_at', 'DATETIME')
                ]
                for col, col_t in inst_defs:
                    if col not in existing_inst:
                        conn.execute(text(f"ALTER TABLE instruments ADD COLUMN {col} {col_t}"))

                # 2. reports table
                res_rep = conn.execute(text("PRAGMA table_info(reports)")).fetchall()
                existing_rep = {r[1] for r in res_rep}
                rep_defs = [
                    ('decision_rating', 'VARCHAR(50) DEFAULT "INSUFFICIENT_EVIDENCE"'),
                    ('entry_price_min', 'FLOAT'),
                    ('entry_price_max', 'FLOAT'),
                    ('fair_value_min', 'FLOAT'),
                    ('fair_value_max', 'FLOAT'),
                    ('target_bull', 'FLOAT'),
                    ('target_base', 'FLOAT'),
                    ('target_bear', 'FLOAT'),
                    ('stop_loss_price', 'FLOAT'),
                    ('horizon_type', 'VARCHAR(50) DEFAULT "medium_term"'),
                    ('strategy_consensus_json', 'TEXT'),
                    ('scenario_projections_json', 'TEXT')
                ]
                for col, col_t in rep_defs:
                    if col not in existing_rep:
                        conn.execute(text(f"ALTER TABLE reports ADD COLUMN {col} {col_t}"))

                # 3. research_runs table
                res_runs = conn.execute(text("PRAGMA table_info(research_runs)")).fetchall()
                existing_runs = {r[1] for r in res_runs}
                run_defs = [
                    ('investment_amount_inr', 'FLOAT DEFAULT 50000.0'),
                    ('horizon_category', 'VARCHAR(50) DEFAULT "medium_term"'),
                    ('risk_tolerance', 'VARCHAR(50) DEFAULT "moderate"')
                ]
                for col, col_t in run_defs:
                    if col not in existing_runs:
                        conn.execute(text(f"ALTER TABLE research_runs ADD COLUMN {col} {col_t}"))

                conn.commit()
    except Exception as e:
        pass

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

