import os
import pytest
from datetime import datetime, timezone
from app.providers.market_data.yfinance_provider import YFinanceMarketDataProvider
from app.providers.llm.gemini_adapter import GeminiAdapter
from app.rag.embeddings import GeminiEmbeddingGenerator
from app.services.rag_service import RAGService
from app.agents.graph import research_graph

# Check gate
RUN_LIVE = os.environ.get("RUN_LIVE_INTEGRATION_TESTS", "").lower() in ("true", "1", "yes")


@pytest.mark.skipif(not RUN_LIVE, reason="Live integration tests gated by RUN_LIVE_INTEGRATION_TESTS=true")
def test_live_market_data_retrieval_greenpower():
    """Live Test 1: Retrieve real historical market bars for GREENPOWER.NS from yfinance."""
    provider = YFinanceMarketDataProvider()
    bars = provider.get_historical_bars("GREENPOWER", "NSE")
    assert len(bars) > 0, "Expected non-empty real historical bars from yfinance"
    latest = bars[-1]
    assert latest.close > 0
    assert latest.provider == "yfinance"
    assert latest.timestamp.tzinfo == timezone.utc


@pytest.mark.skipif(not RUN_LIVE, reason="Live integration tests gated by RUN_LIVE_INTEGRATION_TESTS=true")
def test_live_gemini_llm_call():
    """Live Test 2: Call real Gemini LLM API using google-genai."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.fail("BLOCKED: GEMINI_API_KEY is not configured in environment for live LLM call.")

    adapter = GeminiAdapter(api_key=api_key)
    res = adapter.generate_text_response(
        system_prompt="You are MarketLab AI. Reply with 'MARKETLAB_VERIFIED' and nothing else.",
        user_prompt="Status check"
    )
    assert "MARKETLAB_VERIFIED" in res


@pytest.mark.skipif(not RUN_LIVE, reason="Live integration tests gated by RUN_LIVE_INTEGRATION_TESTS=true")
def test_live_gemini_embedding_call():
    """Live Test 3: Generate real embeddings with Gemini API and validate dimension and finiteness."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.fail("BLOCKED: GEMINI_API_KEY is not configured in environment for live embedding call.")

    gen = GeminiEmbeddingGenerator(api_key=api_key, model="text-embedding-004", dim=768)
    vec = gen.generate_query_embedding("Orient Green Power renewable energy generation")
    assert len(vec) == 768
    assert all(not (x != x) for x in vec)  # no NaN
