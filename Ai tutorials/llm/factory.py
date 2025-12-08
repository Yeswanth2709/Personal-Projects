from .base import LLMClient
from .config import load_config, ProviderConfig
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .tcs_genai_client import TcsGenAiClient


_PROVIDER_MAP = {
    "openai": OpenAIClient,
    "gemini": GeminiClient,
    "tcs_genai": TcsGenAiClient,
}


def create_llm_client(config_path: str = "llm_config.yaml") -> LLMClient:
    cfg: ProviderConfig = load_config(config_path)
    cls = _PROVIDER_MAP.get(cfg.name)
    if cls is None:
        raise ValueError(f"Unknown provider: {cfg.name}")
    return cls(cfg)
