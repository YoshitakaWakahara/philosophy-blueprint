from __future__ import annotations
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # .env があれば読む


@dataclass
class OpenAIConfig:
    api_key: str
    base_url: str = "https://api.openai.com/v1"


def get_openai_config() -> OpenAIConfig:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Configure .env or env vars.")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return OpenAIConfig(api_key=api_key, base_url=base_url)