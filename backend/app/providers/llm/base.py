from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLLMAdapter(ABC):
    @abstractmethod
    def generate_json_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate structured JSON response adhering to instructions."""
        pass

    @abstractmethod
    def generate_text_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate textual response."""
        pass
