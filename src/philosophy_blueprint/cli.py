from __future__ import annotations

import pathlib
import time
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
DEFAULT_GEMINI_MODEL = "models/gemini-2.5-flash"


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
def validate_claims(path: str = "analysis/genealogy_I/claims") -> None:
    """
    claims yaml を読み込み、Pydanticでバリデーションする。ファイルまたはディレクトリを指定可。
    """
    target = pathlib.Path(path)

    if target.is_dir():
        files = sorted(target.glob("*.yaml"))
        if not files:
            print(f"[yellow]No yaml files found in {target}[/yellow]")
            raise typer.Exit(code=1)
        errors = 0
        for f in files:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            try:
                ClaimsFile.model_validate(data)
                print(f"[green]OK:[/green] {f.name}")
            except Exception as e:
                print(f"[red]Failed:[/red] {f.name}: {e}")
                errors += 1
        if errors:
            raise typer.Exit(code=1)
    elif target.is_file():
        data = yaml.safe_load(target.read_text(encoding="utf-8"))
        try:
            ClaimsFile.model_validate(data)
        except Exception as e:
            print(f"[red]Validation failed:[/red] {e}")
            raise typer.Exit(code=1)
        print(f"[green]OK:[/green] {target} is valid.")
    else:
        print(f"[red]Not found:[/red] {target}")
        raise typer.Exit(code=1)


def _normalize_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if normalized not in {"openai", "gemini"}:
        raise ValueError(f"Unsupported provider: {provider}. Use openai or gemini.")
    return normalized


def _default_model_for_provider(provider: str) -> str:
    return DEFAULT_OPENAI_MODEL if provider == "openai" else DEFAULT_GEMINI_MODEL


def _translate_text(provider: str, source_text: str, ref: str, model: str) -> str:
    if provider == "openai":
        cfg = get_openai_config()
        return translate_with_openai(cfg=cfg, source_text=source_text, ref=ref, model=model)

    cfg = get_gemini_config()
    return translate_with_gemini(cfg=cfg, source_text=source_text, ref=ref, model=model)


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

    selected_model = model or _default_model_for_provider(normalized_provider)

    source_text = chunk_map.get(normalized_ref)
    if not source_text:
        print(f"[red]Chunk not found:[/red] {normalized_ref}")
        raise typer.Exit(code=1)

    if dry_run:
        print(f"[green]Resolved chunk:[/green] {normalized_ref}")
        print(f"provider={normalized_provider} model={selected_model}")
        print(source_text[:700] + ("..." if len(source_text) > 700 else ""))
        return

    try:
        translated = _translate_text(
            provider=normalized_provider,
            source_text=source_text,
            ref=normalized_ref,
            model=selected_model,
        )
    except RuntimeError as e:
        print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1)

    if not translated:
        print("[red]Translation failed:[/red] empty response")
        raise typer.Exit(code=1)

    out_file = write_translation_file(
        output_dir=pathlib.Path(out_dir),
        ref=normalized_ref,
        source=source,
        provider=normalized_provider,
        model=selected_model,
        translated_text=translated,
    )

    print(f"[green]OK:[/green] wrote translation: {out_file}")


@app.command()
def translate_all_chunks(
    source: str = str(DEFAULT_SOURCE_PATH),
    out_dir: str = str(DEFAULT_TRANSLATION_DIR),
    provider: str = "openai",
    model: Optional[str] = None,
    from_ref: Optional[str] = None,
    to_ref: Optional[str] = None,
    requests_per_minute: int = 5,
    overwrite: bool = False,
    continue_on_error: bool = True,
    dry_run: bool = False,
) -> None:
    """
    GM I の全チャンク（または範囲）を順に翻訳する。既存出力は既定でスキップ。
    """
    source_path = pathlib.Path(source)
    output_dir = pathlib.Path(out_dir)

    try:
        normalized_provider = _normalize_provider(provider)
        selected_model = model or _default_model_for_provider(normalized_provider)
        chunk_map = build_genealogy_i_chunk_map(source_path)
    except (ValueError, FileNotFoundError) as e:
        print(f"[red]Input error:[/red] {e}")
        raise typer.Exit(code=1)

    if requests_per_minute <= 0:
        print("[red]Input error:[/red] requests_per_minute must be > 0")
        raise typer.Exit(code=1)

    min_interval_seconds = 60.0 / requests_per_minute

    refs = list(chunk_map.keys())
    start_idx = 0
    end_idx = len(refs) - 1

    if from_ref:
        normalized_from = normalize_ref(from_ref)
        if normalized_from not in chunk_map:
            print(f"[red]Input error:[/red] from_ref not found: {normalized_from}")
            raise typer.Exit(code=1)
        start_idx = refs.index(normalized_from)

    if to_ref:
        normalized_to = normalize_ref(to_ref)
        if normalized_to not in chunk_map:
            print(f"[red]Input error:[/red] to_ref not found: {normalized_to}")
            raise typer.Exit(code=1)
        end_idx = refs.index(normalized_to)

    if start_idx > end_idx:
        print("[red]Input error:[/red] from_ref must be <= to_ref")
        raise typer.Exit(code=1)

    target_refs = refs[start_idx : end_idx + 1]
    output_dir.mkdir(parents=True, exist_ok=True)

    done = 0
    skipped = 0
    failed = 0
    last_request_ts: Optional[float] = None

    for ref in target_refs:
        out_file = output_dir / f"{ref}.md"
        if out_file.exists() and not overwrite:
            print(f"[yellow]Skip:[/yellow] {ref} already exists")
            skipped += 1
            continue

        source_text = chunk_map[ref]
        if dry_run:
            print(f"[green]Dry-run:[/green] would translate {ref}")
            done += 1
            continue

        try:
            # Keep request cadence under provider quota limits.
            if last_request_ts is not None:
                elapsed = time.monotonic() - last_request_ts
                if elapsed < min_interval_seconds:
                    wait_seconds = min_interval_seconds - elapsed
                    print(
                        f"[cyan]Wait:[/cyan] sleeping {wait_seconds:.1f}s for rate limit "
                        f"({requests_per_minute}/min)"
                    )
                    time.sleep(wait_seconds)

            translated = _translate_text(
                provider=normalized_provider,
                source_text=source_text,
                ref=ref,
                model=selected_model,
            )
            last_request_ts = time.monotonic()
            if not translated:
                raise ValueError("empty response")

            write_translation_file(
                output_dir=output_dir,
                ref=ref,
                source=source,
                provider=normalized_provider,
                model=selected_model,
                translated_text=translated,
            )
            print(f"[green]OK:[/green] wrote {ref}")
            done += 1
        except Exception as e:
            print(f"[red]Failed:[/red] {ref}: {e}")
            failed += 1
            if not continue_on_error:
                print("[red]Stop:[/red] continue_on_error is false")
                raise typer.Exit(code=1)

    print(
        f"[green]Batch done:[/green] total={len(target_refs)} done={done} skipped={skipped} failed={failed}"
    )

if __name__ == "__main__":
    app()
