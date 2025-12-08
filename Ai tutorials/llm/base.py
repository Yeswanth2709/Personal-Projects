from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMClient(ABC):
    """Common interface all LLM providers must implement."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        messages: [{"role": "user" | "system" | "assistant", "content": "..."}]
        returns: assistant response text
        """
        raise NotImplementedError
