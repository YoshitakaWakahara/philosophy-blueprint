from __future__ import annotations

from openai import OpenAI

from ..config import GeminiConfig
from .prompt import SYSTEM_PROMPT
from .prompt import build_user_prompt


def translate_with_gemini(
    cfg: GeminiConfig,
    source_text: str,
    ref: str,
    model: str,
) -> str:
    # Gemini OpenAI-compatible endpoint currently supports chat.completions.
    client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": build_user_prompt(ref=ref, source_text=source_text),
            },
        ],
    )
    message = response.choices[0].message.content
    if isinstance(message, str):
        return message.strip()
    return ""
