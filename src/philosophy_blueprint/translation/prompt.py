from __future__ import annotations

SYSTEM_PROMPT = (
    "You are a precise philosophy translator. "
    "Translate English to Japanese with high fidelity. "
    "Do not summarize. Preserve nuance and rhetorical tone. "
    "Keep paragraph structure and emphasis markers where possible. "
    "Prefer natural Japanese word order unless it changes meaning."
)


def build_user_prompt(ref: str, source_text: str) -> str:
    return (
        f"Ref: {ref}\n"
        "Task: Translate the following source text into Japanese.\n"
        "Constraints:\n"
        "- Keep all substantive meaning and implications.\n"
        "- Do not omit examples, qualifiers, or rhetorical contrasts.\n"
        "- Do not add commentary or notes.\n"
        "Output only the Japanese translation.\n\n"
        f"{source_text}"
    )
