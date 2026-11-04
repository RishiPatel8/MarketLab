from typing import Dict, Any, Optional
import json
import logging
from app.providers.llm.base import BaseLLMAdapter
from app.providers.llm.gemini_adapter import ConfigurationError, LLMProviderError, redact_sensitive_text
from app.core.config import settings

logger = logging.getLogger("marketlab.provider.openai")


class OpenAIAdapter(BaseLLMAdapter):
    """
    Live OpenAI adapter. Strictly forbids silent fallback to mock in live mode.
    """

    PROVIDER_NAME = "openai"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL or "gpt-4o-mini"

        if not self.api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is not configured. Silent fallback is disabled in live mode."
            )

    def generate_json_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            safe_err = redact_sensitive_text(str(e))
            raise LLMProviderError(f"OpenAI JSON completion failed: {safe_err}")

    def generate_text_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            safe_err = redact_sensitive_text(str(e))
            raise LLMProviderError(f"OpenAI text completion failed: {safe_err}")
