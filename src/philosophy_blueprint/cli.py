from __future__ import annotations

import pathlib
from typing import Optional

import typer
import yaml
from rich import print

from .chunking import build_genealogy_i_chunk_map
from .chunking import normalize_ref
from .chunking import write_chunks
from .config import get_gemini_config
from .config import get_openai_config
from .models import ClaimsFile
from .translation import translate_with_gemini
from .translation import translate_with_openai
from .translation import write_translation_file

app = typer.Typer(help="philosophy-blueprint CLI")

DEFAULT_SOURCE_PATH = pathlib.Path("sources/genealogy_I/GM_I_full.txt")
DEFAULT_CHUNK_DIR = pathlib.Path("sources/genealogy_I/chunks")
DEFAULT_TRANSLATION_DIR = pathlib.Path("translations/genealogy_I")
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


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


def _normalize_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if normalized not in {"openai", "gemini"}:
        raise ValueError(f"Unsupported provider: {provider}. Use openai or gemini.")
    return normalized


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
        chunk_map = build_genealogy_i_chunk_map(source_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"[red]Chunk split failed:[/red] {e}")
        raise typer.Exit(code=1)

    try:
        write_chunks(chunk_map=chunk_map, output_dir=output_dir, source_path=source_path, force=force)
    except FileExistsError as e:
        print(f"[red]{e}[/red] (use --force to overwrite)")
        raise typer.Exit(code=1)

    print(f"[green]OK:[/green] created {len(chunk_map)} chunks in {output_dir}")


@app.command()
def translate_chunk(
    ref: str,
    source: str = str(DEFAULT_SOURCE_PATH),
    out_dir: str = str(DEFAULT_TRANSLATION_DIR),
    provider: str = "openai",
    model: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """
    ref（例: GM.I.S01）を参照して GM I の節を逐語訳し、translations/ に保存する。
    """
    try:
        normalized_ref = normalize_ref(ref)
        normalized_provider = _normalize_provider(provider)
        chunk_map = build_genealogy_i_chunk_map(pathlib.Path(source))
    except (ValueError, FileNotFoundError) as e:
        print(f"[red]Input error:[/red] {e}")
        raise typer.Exit(code=1)

    selected_model = model or (
        DEFAULT_OPENAI_MODEL if normalized_provider == "openai" else DEFAULT_GEMINI_MODEL
    )

    source_text = chunk_map.get(normalized_ref)
    if not source_text:
        print(f"[red]Chunk not found:[/red] {normalized_ref}")
        raise typer.Exit(code=1)

    if dry_run:
        print(f"[green]Resolved chunk:[/green] {normalized_ref}")
        print(f"provider={normalized_provider} model={selected_model}")
        print(source_text[:700] + ("..." if len(source_text) > 700 else ""))
        return

    if normalized_provider == "openai":
        try:
            cfg = get_openai_config()
        except RuntimeError as e:
            print(f"[red]Config error:[/red] {e}")
            raise typer.Exit(code=1)
        translated = translate_with_openai(
            cfg=cfg,
            source_text=source_text,
            ref=normalized_ref,
            model=selected_model,
        )
    else:
        try:
            cfg = get_gemini_config()
        except RuntimeError as e:
            print(f"[red]Config error:[/red] {e}")
            raise typer.Exit(code=1)
        translated = translate_with_gemini(
            cfg=cfg,
            source_text=source_text,
            ref=normalized_ref,
            model=selected_model,
        )

    if not translated:
        print("[red]Translation failed:[/red] empty response")
        raise typer.Exit(code=1)

    out_file = write_translation_file(
        output_dir=pathlib.Path(out_dir),
        ref=normalized_ref,
        source=source,
        translated_text=translated,
    )

    print(f"[green]OK:[/green] wrote translation: {out_file}")

if __name__ == "__main__":
    app()
