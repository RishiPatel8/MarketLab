from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Base class for SQLAlchemy declarative models
Base = declarative_base()

# Resolve URLs for sync and async
db_url = settings.DATABASE_URL
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
    db_url_sync = "sqlite:///./marketlab.db"
    db_url_async = "sqlite+aiosqlite:///./marketlab.db"

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
