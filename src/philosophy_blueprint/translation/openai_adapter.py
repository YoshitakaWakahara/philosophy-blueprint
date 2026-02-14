from __future__ import annotations

import pathlib

from openai import OpenAI

from ..config import OpenAIConfig


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
                "content": (
                    "You are a precise philosophy translator. "
                    "Translate English to Japanese with high fidelity. "
                    "Do not summarize. Preserve nuance and rhetorical tone."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Ref: {ref}\n"
                    "Task: Translate the following source text into Japanese.\n"
                    "Output only the Japanese translation.\n\n"
                    f"{source_text}"
                ),
            },
        ],
    )
    return (response.output_text or "").strip()


def write_translation_file(
    output_dir: pathlib.Path,
    ref: str,
    source: str,
    translated_text: str,
) -> pathlib.Path:
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
                "## Translation (JA)",
                translated_text,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return out_file
