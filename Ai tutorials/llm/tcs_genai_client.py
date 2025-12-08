from typing import List, Dict, Any
import httpx
from openai import OpenAI

from .base import LLMClient
from .config import ProviderConfig


class TcsGenAiClient(LLMClient):
    def __init__(self, cfg: ProviderConfig):
        self.model = cfg.model

        verify = cfg.extra.get("verify_ssl", True)
        http_client = httpx.Client(verify=verify)

        self.client = OpenAI(
            api_key=cfg.api_key,
            base_url=cfg.base_url,
            http_client=http_client,
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs,
        )
        return resp.choices[0].message.content
