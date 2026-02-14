from __future__ import annotations

import pathlib
from datetime import datetime
from datetime import timezone

from openai import OpenAI

from ..config import OpenAIConfig
from .prompt import SYSTEM_PROMPT
from .prompt import build_user_prompt


def translate_with_openai(
    cfg: OpenAIConfig,
    source_text: str,
    ref: str,
    model: str,
) -> str:
    client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)
    response = client.responses.create(
        model=model,
        input=[
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
    return (response.output_text or "").strip()


def write_translation_file(
    output_dir: pathlib.Path,
    ref: str,
    source: str,
    provider: str,
    model: str,
    translated_text: str,
) -> pathlib.Path:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{ref}.md"
    out_file.write_text(
        "\n".join(
            [
                f"# {ref}",
                "",
                "## Source",
                f"- {source}",
                "",
                "## Metadata",
                f"- ref: {ref}",
                f"- provider: {provider}",
                f"- model: {model}",
                f"- generated_at_utc: {generated_at}",
                "",
                "## Translation (JA)",
                translated_text,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return out_file
