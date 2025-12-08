from typing import List, Dict, Any
from openai import OpenAI

from .base import LLMClient
from .config import ProviderConfig


class OpenAIClient(LLMClient):
    def __init__(self, cfg: ProviderConfig):
        self.model = cfg.model
        self.client = OpenAI(
            api_key=cfg.api_key,
            base_url=cfg.base_url,  # None => default OpenAI cloud
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs,
        )
        return resp.choices[0].message.content
