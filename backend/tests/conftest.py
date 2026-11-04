import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Ensure backend root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app as fastapi_app
from app.db.session import Base, get_sync_db, SyncSessionLocal
from app.services.instrument_service import InstrumentService
from app.services.rag_service import RAGService
from app.rag.embeddings import MockEmbeddingGenerator
import app.db.models

# Test database engine using SQLite in-memory or file
TEST_DB_URL = "sqlite:///./test_marketlab.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
SyncSessionLocal.configure(bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as db:
        InstrumentService(db)
        RAGService(db, embedding_generator=MockEmbeddingGenerator())
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_marketlab.db"):
        try:
            os.remove("./test_marketlab.db")
        except:
            pass

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    fastapi_app.dependency_overrides[get_sync_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()
