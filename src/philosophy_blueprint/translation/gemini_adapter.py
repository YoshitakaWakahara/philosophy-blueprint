from __future__ import annotations

from openai import OpenAI

from ..config import GeminiConfig


def translate_with_gemini(
    cfg: GeminiConfig,
    source_text: str,
    ref: str,
    model: str,
) -> str:
    # Gemini OpenAI-compatible endpoint.
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
