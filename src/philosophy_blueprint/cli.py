from __future__ import annotations

import pathlib
import re
from collections import OrderedDict

import typer
import yaml
from openai import OpenAI
from rich import print

from .config import get_openai_config
from .models import ClaimsFile

app = typer.Typer(help="philosophy-blueprint CLI")

DEFAULT_SOURCE_PATH = pathlib.Path("sources/genealogy_I/GM_I_full.txt")
DEFAULT_CHUNK_DIR = pathlib.Path("sources/genealogy_I/chunks")
DEFAULT_TRANSLATION_DIR = pathlib.Path("translations/genealogy_I")

SECTION_HEADING_RE = re.compile(r"^\s*(\d{1,2})\s*\.?\s*$")


@app.callback()
def main() -> None:
    """
    philosophy-blueprint コマンドラインツール。
    """
    # ルートコマンドはサブコマンドのハブとして利用する
    pass


@app.command()
def info() -> None:
    """
    動作確認用: 設定が読めているかだけ確認。
    """
    try:
        cfg = get_openai_config()
    except RuntimeError as e:
        print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)

    print("[green]philosophy-blueprint[/green]")
    print(f"OPENAI_BASE_URL = {cfg.base_url}")


def _extract_first_essay_lines(full_text: str) -> list[str]:
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


def _build_genealogy_i_chunk_map(source_path: pathlib.Path) -> OrderedDict[str, str]:
    if not source_path.exists():
        raise FileNotFoundError(source_path)

    text = source_path.read_text(encoding="utf-8")
    first_essay_lines = _extract_first_essay_lines(text)

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


def _normalize_ref(ref: str) -> str:
    m = re.match(r"^\s*GM\.I\.S(\d{1,2})\s*$", ref, flags=re.IGNORECASE)
    if not m:
        raise ValueError(f"Invalid ref format: {ref}. Expected GM.I.S01 style.")
    return f"GM.I.S{int(m.group(1)):02d}"


@app.command()
def validate_claims(path: str = "analysis/genealogy_I/claims.yaml") -> None:
    """
    claims.yaml を読み込み、Pydanticでバリデーションする。
    """
    file_path = pathlib.Path(path)
    if not file_path.exists():
        print(f"[red]File not found:[/red] {file_path}")
        raise typer.Exit(code=1)

    data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    try:
        ClaimsFile.model_validate(data)
    except Exception as e:
        print(f"[red]Validation failed:[/red] {e}")
        raise typer.Exit(code=1)

    print(f"[green]OK:[/green] {file_path} is valid.")


@app.command()
def divide_chunk(
    source: str = str(DEFAULT_SOURCE_PATH),
    out_dir: str = str(DEFAULT_CHUNK_DIR),
    force: bool = False,
) -> None:
    """
    GM I の本文を節ごとに分割し、sources/genealogy_I/chunks に保存する。
    """
    source_path = pathlib.Path(source)
    output_dir = pathlib.Path(out_dir)

    try:
        chunk_map = _build_genealogy_i_chunk_map(source_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"[red]Chunk split failed:[/red] {e}")
        raise typer.Exit(code=1)

    output_dir.mkdir(parents=True, exist_ok=True)

    for ref, chunk_text in chunk_map.items():
        chunk_file = output_dir / f"{ref}.txt"
        if chunk_file.exists() and not force:
            print(f"[red]File exists:[/red] {chunk_file} (use --force to overwrite)")
            raise typer.Exit(code=1)
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

    print(f"[green]OK:[/green] created {len(chunk_map)} chunks in {output_dir}")


@app.command()
def translate_chunk(
    ref: str,
    source: str = str(DEFAULT_SOURCE_PATH),
    out_dir: str = str(DEFAULT_TRANSLATION_DIR),
    model: str = "gpt-4.1-mini",
    dry_run: bool = False,
) -> None:
    """
    ref（例: GM.I.S01）を参照して GM I の節を逐語訳し、translations/ に保存する。
    """
    try:
        normalized_ref = _normalize_ref(ref)
        chunk_map = _build_genealogy_i_chunk_map(pathlib.Path(source))
    except (ValueError, FileNotFoundError) as e:
        print(f"[red]Input error:[/red] {e}")
        raise typer.Exit(code=1)

    source_text = chunk_map.get(normalized_ref)
    if not source_text:
        print(f"[red]Chunk not found:[/red] {normalized_ref}")
        raise typer.Exit(code=1)

    if dry_run:
        print(f"[green]Resolved chunk:[/green] {normalized_ref}")
        print(source_text[:700] + ("..." if len(source_text) > 700 else ""))
        return

    try:
        cfg = get_openai_config()
    except RuntimeError as e:
        print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)

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
                    f"Ref: {normalized_ref}\n"
                    "Task: Translate the following source text into Japanese.\n"
                    "Output only the Japanese translation.\n\n"
                    f"{source_text}"
                ),
            },
        ],
    )
    translated = (response.output_text or "").strip()
    if not translated:
        print("[red]Translation failed:[/red] empty response")
        raise typer.Exit(code=1)

    output_dir = pathlib.Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{normalized_ref}.md"
    out_file.write_text(
        "\n".join(
            [
                f"# {normalized_ref}",
                "",
                "## Source",
                f"- {source}",
                "",
                "## Translation (JA)",
                translated,
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"[green]OK:[/green] wrote translation: {out_file}")

if __name__ == "__main__":
    app()
