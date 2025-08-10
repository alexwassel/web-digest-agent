
from abc import ABC, abstractmethod
from typing import Dict, Any

class ModelClient(ABC):
    @abstractmethod
    def complete_text(self, prompt: str, max_tokens: int = 800) -> str: ...

    @abstractmethod
    def complete_json(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]: ...
