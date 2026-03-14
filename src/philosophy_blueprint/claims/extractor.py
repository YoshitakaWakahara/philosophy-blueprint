from __future__ import annotations

import yaml
from openai import OpenAI

from ..config import GeminiConfig, OpenAIConfig
from .prompt import SYSTEM_PROMPT, build_user_prompt


def _call_api(client: OpenAI, model: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content
    return content.strip() if isinstance(content, str) else ""


def extract_claims_with_openai(
    cfg: OpenAIConfig,
    ref: str,
    source_text: str,
    translation_text: str,
    existing_ids: list[str],
    model: str,
) -> list[dict]:
    client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)
    raw = _call_api(client, model, build_user_prompt(ref, source_text, translation_text, existing_ids))
    return _parse_yaml(raw)


def extract_claims_with_gemini(
    cfg: GeminiConfig,
    ref: str,
    source_text: str,
    translation_text: str,
    existing_ids: list[str],
    model: str,
) -> list[dict]:
    client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)
    raw = _call_api(client, model, build_user_prompt(ref, source_text, translation_text, existing_ids))
    return _parse_yaml(raw)


def _parse_yaml(raw: str) -> list[dict]:
    # AIがmarkdownコードブロックで囲んで返すことがあるので除去する
    text = raw
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    data = yaml.safe_load(text)
    if isinstance(data, dict) and "claims" in data:
        return data["claims"] or []
    if isinstance(data, list):
        return data
    return []
