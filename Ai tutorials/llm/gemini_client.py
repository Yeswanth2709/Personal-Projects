from google import genai
from typing import List, Dict, Any
from llm.base import LLMClient


class GeminiClient(LLMClient):
    def __init__(self, cfg):
        self.model = cfg.model
        self.client = genai.Client(api_key=cfg.api_key)

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        parts = []
        for m in messages:
            parts.append(f"{m['role'].upper()}: {m['content']}")
        prompt = "\n".join(parts)

        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            **kwargs
        )
        return resp.text
