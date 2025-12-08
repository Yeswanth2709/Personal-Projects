import os
import yaml
from dataclasses import dataclass
from typing import Any, Dict
from dotenv import load_dotenv

# Load .env when program starts
load_dotenv()

@dataclass
class ProviderConfig:
    name: str
    api_key: str
    base_url: str | None
    model: str
    extra: Dict[str, Any]


def load_config(path: str = "llm_config.yaml") -> ProviderConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    provider_name = raw["provider"]
    p = raw[provider_name]

    api_key = os.getenv(p["api_key_env"])
    if not api_key:
        raise RuntimeError(f"API key env var {p['api_key_env']} is not set")

    return ProviderConfig(
        name=provider_name,
        api_key=api_key,
        base_url=p.get("base_url"),
        model=p["model"],
        extra={k: v for k, v in p.items() if k not in ("api_key_env", "base_url", "model")}
    )
