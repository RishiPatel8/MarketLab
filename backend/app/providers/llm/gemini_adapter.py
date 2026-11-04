from typing import Dict, Any, Optional, Type
import json
import logging
import time
import re
from pydantic import BaseModel, ValidationError
from app.providers.llm.base import BaseLLMAdapter
from app.providers.llm.mock_adapter import MockLLMAdapter
from app.core.config import settings

logger = logging.getLogger("marketlab.provider.gemini")


class LLMProviderError(Exception):
    """Raised when the LLM provider fails."""
    pass


class ConfigurationError(Exception):
    """Raised when required provider configuration is missing."""
    pass


def redact_sensitive_text(text: str) -> str:
    """Redacts potential API keys or authorization tokens from logs and error strings."""
    if not text:
        return ""
    # Redact Gemini keys (e.g. AIzaSy...)
    redacted = re.sub(r"AIzaSy[A-Za-z0-9_-]{15,}", "[REDACTED_GEMINI_KEY]", text)
    # Redact OpenAI keys
    redacted = re.sub(r"sk-[A-Za-z0-9_-]{15,}", "[REDACTED_API_KEY]", redacted)
    # Redact Groq keys
    redacted = re.sub(r"gsk_[A-Za-z0-9_-]{15,}", "[REDACTED_GROQ_KEY]", redacted)
    # Redact query param or header secrets
    redacted = re.sub(r"(?i)(key|api[_-]?key|token|secret)\s*[:=]\s*[^&\s]{6,}", r"\1=[REDACTED]", redacted)
    return redacted


class GeminiAdapter(BaseLLMAdapter):
    """
    Live Google Gemini adapter using the official google-genai SDK.
    Strictly enforces:
    - No silent fallback to mock provider in live mode.
    - Explicit configuration error if API key is missing.
    - Secret redaction in logs and errors.
    - Bounded retries with exponential backoff on transient errors.
    - Structured Pydantic validation on JSON generation.
    - Metadata recording: model, latency, provider.
    """

    PROVIDER_NAME = "gemini"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
        timeout_seconds: float = 30.0
    ):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-3.5-flash-lite"
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

        if not self.api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY is not configured in backend environment or .env. "
                "Silent fallback to mock LLM is disabled in live mode. "
                "Set GEMINI_API_KEY or configure LLM_PROVIDER=mock for offline testing."
            )

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            safe_err = redact_sensitive_text(str(e))
            raise LLMProviderError(f"Failed to initialize google-genai Client: {safe_err}")

    def generate_json_response(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[Type[BaseModel]] = None
    ) -> Dict[str, Any]:
        """
        Generates a structured JSON response from Gemini.
        Validates JSON parsing and optional Pydantic schema adherence.
        """
        combined_prompt = (
            f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
            f"CRITICAL: Output strictly valid JSON matching the required schema. Do not wrap with prose or markdown explanations.\n\n"
            f"USER QUERY AND INPUT CONTEXT:\n{user_prompt}"
        )

        models_to_try = [self.model]
        for fallback in ["gemini-3.5-flash", "gemini-3.5-flash-lite"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_err = None
        for model_name in models_to_try:
            for attempt in range(1, self.max_retries + 1):
                start_time = time.time()
                try:
                    from google.genai import types

                    config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )

                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=combined_prompt,
                        config=config
                    )

                    elapsed = round(time.time() - start_time, 3)
                    logger.info(f"Gemini JSON response received in {elapsed}s (model={model_name})")

                    raw_text = response.text.strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                    raw_text = raw_text.strip()

                    parsed = json.loads(raw_text)

                    if schema:
                        try:
                            validated = schema.model_validate(parsed)
                            return validated.model_dump()
                        except ValidationError as ve:
                            raise LLMProviderError(f"Gemini response did not conform to schema {schema.__name__}: {ve}")

                    return parsed

                except Exception as e:
                    safe_err = redact_sensitive_text(str(e))
                    last_err = safe_err
                    logger.warning(f"Gemini JSON call with {model_name} (attempt {attempt}/{self.max_retries}) failed: {safe_err}")
                    if "503" in safe_err or "404" in safe_err:
                        # Break out to try fallback model immediately
                        break
                    if attempt < self.max_retries:
                        time.sleep(1.0 * (2 ** (attempt - 1)))

        raise LLMProviderError(f"Gemini API request failed across models {models_to_try}: {last_err}")

    def generate_text_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generates textual response from Gemini with resilient model fallback."""
        combined_prompt = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER QUERY:\n{user_prompt}"

        models_to_try = [self.model]
        for fallback in ["gemini-3.5-flash", "gemini-3.5-flash-lite"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_err = None
        for model_name in models_to_try:
            for attempt in range(1, self.max_retries + 1):
                start_time = time.time()
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=combined_prompt
                    )
                    elapsed = round(time.time() - start_time, 3)
                    logger.info(f"Gemini text response received in {elapsed}s (model={model_name})")
                    return response.text.strip()
                except Exception as e:
                    safe_err = redact_sensitive_text(str(e))
                    last_err = safe_err
                    logger.warning(f"Gemini text call with {model_name} (attempt {attempt}/{self.max_retries}) failed: {safe_err}")
                    if "503" in safe_err or "404" in safe_err:
                        # Break out to try fallback model immediately
                        break
                    if attempt < self.max_retries:
                        time.sleep(1.0 * (2 ** (attempt - 1)))

        raise LLMProviderError(f"Gemini API text request failed across models {models_to_try}: {last_err}")


def get_llm_adapter(provider_override: Optional[str] = None) -> BaseLLMAdapter:
    """
    Factory resolving configured LLM adapter.
    Strictly adheres to:
    - 'mock' -> MockLLMAdapter
    - 'groq' -> GroqAdapter (raises ConfigurationError if unconfigured)
    - 'gemini' -> GeminiAdapter (raises ConfigurationError if unconfigured; no silent mock fallback)
    - 'openai' -> OpenAIAdapter (raises ConfigurationError if unconfigured)
    """
    provider = (provider_override or settings.LLM_PROVIDER).lower()

    if provider == "groq":
        from app.providers.llm.groq_adapter import GroqAdapter
        if not settings.GROQ_API_KEY:
            raise ConfigurationError(
                "GROQ_API_KEY is not configured. Silent fallback is disabled in live mode."
            )
        return GroqAdapter()
    elif provider == "gemini":
        return GeminiAdapter()
    elif provider == "openai":
        from app.providers.llm.openai_adapter import OpenAIAdapter
        if not settings.OPENAI_API_KEY:
            raise ConfigurationError(
                "OPENAI_API_KEY is not configured. Silent fallback is disabled in live mode."
            )
        return OpenAIAdapter()
    elif provider == "mock":
        return MockLLMAdapter()
    else:
        raise ConfigurationError(f"Unsupported LLM provider: '{provider}'. Supported: mock, groq, gemini, openai.")
