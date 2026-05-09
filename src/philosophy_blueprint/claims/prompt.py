from __future__ import annotations

SYSTEM_PROMPT = (
    "You are a precise philosophy analyst specializing in Nietzsche. "
    "Extract structured claims from philosophical texts. "
    "Output only valid YAML. Do not add commentary, markdown fences, or explanation."
)

CLAIM_TYPES = "genealogy | inversion | diagnosis | critique | distinction"


def build_user_prompt(ref: str, source_text: str, translation_text: str, existing_ids: list[str]) -> str:
    next_index = len(existing_ids) + 1
    example_id = f"{ref}.C{next_index:02d}"

    existing_note = (
        f"Already used claim_ids: {existing_ids}. Start from {example_id}."
        if existing_ids
        else f"Start claim_ids from {example_id}."
    )

    return (
        f"Ref: {ref}\n"
        f"{existing_note}\n\n"
        "Task: Extract all significant philosophical claims from the section below.\n\n"
        "Rules:\n"
        "- claim_id format: {ref}.C01, {ref}.C02, ... (zero-padded 2 digits)\n"
        f"- type must be one of: {CLAIM_TYPES}\n"
        "- statement_ja: one concise Japanese sentence stating the claim\n"
        "- my_paraphrase: leave as empty string ''\n"
        "- concepts: list of concept IDs in NIETZ.CONCEPT_NAME format (empty list if unclear)\n"
        "- sources.ref: exact section reference e.g. 'GM I §3'\n\n"
        "Output format (YAML list only, no other text):\n"
        "claims:\n"
        "  - claim_id: ...\n"
        "    type: ...\n"
        "    statement_ja: '...'\n"
        "    my_paraphrase: ''\n"
        "    concepts: []\n"
        "    sources:\n"
        "      - ref: '...'\n\n"
        "--- SOURCE TEXT ---\n"
        f"{source_text}\n\n"
        "--- JAPANESE TRANSLATION ---\n"
        f"{translation_text}"
    )
