from typing import Dict, Any, Optional
import json
import logging
from app.providers.llm.base import BaseLLMAdapter
from app.providers.llm.mock_adapter import MockLLMAdapter
from app.core.config import settings

logger = logging.getLogger("marketlab.provider.openai")

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self._fallback = MockLLMAdapter()

    def generate_json_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            return self._fallback.generate_json_response(system_prompt, user_prompt)
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
            logger.warning(f"OpenAI call failed ({e}); using deterministic fallback")
            return self._fallback.generate_json_response(system_prompt, user_prompt)

    def generate_text_response(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            return self._fallback.generate_text_response(system_prompt, user_prompt)
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
            logger.warning(f"OpenAI call failed ({e}); using deterministic fallback")
            return self._fallback.generate_text_response(system_prompt, user_prompt)
