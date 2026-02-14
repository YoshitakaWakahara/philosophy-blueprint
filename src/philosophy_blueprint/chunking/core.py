from __future__ import annotations

import pathlib
import re
from collections import OrderedDict

import yaml

SECTION_HEADING_RE = re.compile(r"^\s*(\d{1,2})\s*\.?\s*$")


def extract_first_essay_lines(full_text: str) -> list[str]:
    lines = full_text.splitlines()

    first_essay_idxs = [
        i for i, line in enumerate(lines) if line.strip().upper().startswith("FIRST ESSAY.")
    ]
    second_essay_idxs = [
        i for i, line in enumerate(lines) if line.strip().upper().startswith("SECOND ESSAY.")
    ]

    if not first_essay_idxs:
        raise ValueError("Could not find FIRST ESSAY section.")

    # Gutenberg text contains a TOC and the actual body; prefer the body start when possible.
    start_idx = first_essay_idxs[1] + 1 if len(first_essay_idxs) >= 2 else first_essay_idxs[0] + 1
    end_idx = next((i for i in second_essay_idxs if i > start_idx), len(lines))
    return lines[start_idx:end_idx]


def build_genealogy_i_chunk_map(source_path: pathlib.Path) -> OrderedDict[str, str]:
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    text = source_path.read_text(encoding="utf-8")
    first_essay_lines = extract_first_essay_lines(text)

    chunks_by_section_num: OrderedDict[int, list[str]] = OrderedDict()
    current_section: int | None = None

    for line in first_essay_lines:
        heading_match = SECTION_HEADING_RE.match(line)
        if heading_match:
            current_section = int(heading_match.group(1))
            if current_section not in chunks_by_section_num:
                chunks_by_section_num[current_section] = []
            continue

        if current_section is not None:
            chunks_by_section_num[current_section].append(line)

    if not chunks_by_section_num:
        raise ValueError("No section chunks detected in FIRST ESSAY body.")

    chunk_map: OrderedDict[str, str] = OrderedDict()
    for section_num, lines in chunks_by_section_num.items():
        ref = f"GM.I.S{section_num:02d}"
        chunk_map[ref] = "\n".join(lines).strip()

    return chunk_map


def normalize_ref(ref: str) -> str:
    m = re.match(r"^\s*GM\.I\.S(\d{1,2})\s*$", ref, flags=re.IGNORECASE)
    if not m:
        raise ValueError(f"Invalid ref format: {ref}. Expected GM.I.S01 style.")
    return f"GM.I.S{int(m.group(1)):02d}"


def write_chunks(
    chunk_map: OrderedDict[str, str],
    output_dir: pathlib.Path,
    source_path: pathlib.Path,
    force: bool = False,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for ref, chunk_text in chunk_map.items():
        chunk_file = output_dir / f"{ref}.txt"
        if chunk_file.exists() and not force:
            raise FileExistsError(f"File exists: {chunk_file}")
        chunk_file.write_text(chunk_text + "\n", encoding="utf-8")

    index_file = output_dir / "index.yaml"
    index_data = {
        "source": str(source_path),
        "work": "Nietzsche_Genealogy_of_Morals_I",
        "chunks": [{"ref": ref, "path": f"{ref}.txt"} for ref in chunk_map.keys()],
    }
    index_file.write_text(
        yaml.safe_dump(index_data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
