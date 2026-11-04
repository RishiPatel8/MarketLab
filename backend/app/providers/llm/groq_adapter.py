from typing import Dict, Any, Optional
import json
import logging
import time
from app.providers.llm.base import BaseLLMAdapter
from app.providers.llm.gemini_adapter import ConfigurationError, LLMProviderError, redact_sensitive_text
from app.core.config import settings

logger = logging.getLogger("marketlab.provider.groq")


class GroqAdapter(BaseLLMAdapter):
    """
    Live Groq adapter using OpenAI-compatible client endpoint.
    Provides ultra-fast LPU inference for agentic research reasoning and report compilation.
    """

    PROVIDER_NAME = "groq"
    BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL or "qwen/qwen3.8-27b"
        self.max_retries = 3

        if not self.api_key:
            raise ConfigurationError(
                "GROQ_API_KEY is not configured in backend environment or .env. "
                "Configure GROQ_API_KEY or set LLM_PROVIDER=mock for offline execution."
            )

        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url=self.BASE_URL,
                api_key=self.api_key,
                default_headers={"User-Agent": "MarketLab-AI/1.0"}
            )
        except Exception as e:
            safe_err = redact_sensitive_text(str(e))
            raise LLMProviderError(f"Failed to initialize Groq OpenAI-compatible client: {safe_err}")

    def generate_json_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Generates structured JSON object responses with exponential backoff on transient errors.
        """
        last_err: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()
                response = self.client.chat.completions.create(
                    model=self.model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1
                )
                duration = time.time() - start_time
                content = response.choices[0].message.content or "{}"
                logger.info(f"Groq JSON completion succeeded via {self.model} in {duration:.2f}s")
                return json.loads(content)
            except Exception as e:
                last_err = e
                safe_err = redact_sensitive_text(str(e))
                logger.warning(f"Groq JSON completion attempt {attempt}/{self.max_retries} failed: {safe_err}")
                if attempt < self.max_retries:
                    time.sleep(1.0 * (2 ** (attempt - 1)))

        safe_err = redact_sensitive_text(str(last_err))
        raise LLMProviderError(f"Groq JSON completion failed after {self.max_retries} attempts: {safe_err}")

    def generate_text_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates free-text narrative report synthesis with retry safeguards.
        """
        last_err: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2
                )
                duration = time.time() - start_time
                text = response.choices[0].message.content or ""
                logger.info(f"Groq text completion succeeded via {self.model} in {duration:.2f}s")
                return text.strip()
            except Exception as e:
                last_err = e
                safe_err = redact_sensitive_text(str(e))
                logger.warning(f"Groq text completion attempt {attempt}/{self.max_retries} failed: {safe_err}")
                if attempt < self.max_retries:
                    time.sleep(1.0 * (2 ** (attempt - 1)))

        safe_err = redact_sensitive_text(str(last_err))
        raise LLMProviderError(f"Groq text completion failed after {self.max_retries} attempts: {safe_err}")
