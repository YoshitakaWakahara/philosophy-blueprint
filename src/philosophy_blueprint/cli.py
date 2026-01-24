from __future__ import annotations

import typer
from rich import print

from .config import get_openai_config

app = typer.Typer(help="philosophy-blueprint CLI")


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

import pathlib
import yaml

from .models import ClaimsFile

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
def translate_chunk(ref: str) -> None:
    """
    原文 sources/ 以下の ref（例: GM.I.S01）を読み、
    translations/ 以下に逐語訳を書き出す（中身は後で実装）。
    """
    print(f"Would translate chunk: {ref}")
    # TODO: OpenAI 呼び出し実装

if __name__ == "__main__":
    app()
