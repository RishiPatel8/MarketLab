from typing import Dict, Any, Optional
import json
import logging
from app.providers.llm.base import BaseLLMAdapter
from app.providers.llm.mock_adapter import MockLLMAdapter
from app.core.config import settings

logger = logging.getLogger("marketlab.provider.gemini")

class GeminiAdapter(BaseLLMAdapter):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self._fallback = MockLLMAdapter()

    def generate_json_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            return self._fallback.generate_json_response(system_prompt, user_prompt)
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            prompt = f"{system_prompt}\n\nPlease respond with valid JSON strictly.\n\n{user_prompt}"
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
        except Exception as e:
            logger.warning(f"Gemini call failed ({e}); using deterministic fallback")
            return self._fallback.generate_json_response(system_prompt, user_prompt)

    def generate_text_response(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            return self._fallback.generate_text_response(system_prompt, user_prompt)
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            prompt = f"{system_prompt}\n\n{user_prompt}"
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini call failed ({e}); using deterministic fallback")
            return self._fallback.generate_text_response(system_prompt, user_prompt)


def get_llm_adapter() -> BaseLLMAdapter:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openai" and settings.OPENAI_API_KEY:
        return OpenAIAdapter()
    elif provider == "gemini" and settings.GEMINI_API_KEY:
        return GeminiAdapter()
    return MockLLMAdapter()
