from __future__ import annotations

import pathlib

from typer.testing import CliRunner

from philosophy_blueprint.cli import app

runner = CliRunner()


def _write_sample_source(path: pathlib.Path) -> None:
    path.write_text(
        "\n".join(
            [
                "HEADER",
                'FIRST ESSAY. "GOOD AND EVIL," "GOOD AND BAD"',
                'SECOND ESSAY. "GUILT," "BAD CONSCIENCE," AND THE LIKE',
                'FIRST ESSAY. "GOOD AND EVIL," "GOOD AND BAD."',
                "",
                "1.",
                "",
                "Alpha line 1",
                "",
                "11",
                "",
                "Beta line 1",
                'SECOND ESSAY. "GUILT," "BAD CONSCIENCE," AND THE LIKE.',
            ]
        ),
        encoding="utf-8",
    )


def test_divide_chunk_command(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "gm_i.txt"
    out_dir = tmp_path / "chunks"
    _write_sample_source(source)

    result = runner.invoke(
        app,
        [
            "divide-chunk",
            "--source",
            str(source),
            "--out-dir",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0
    assert (out_dir / "GM.I.S01.txt").exists()
    assert (out_dir / "GM.I.S11.txt").exists()
    assert (out_dir / "index.yaml").exists()


def test_translate_chunk_dry_run(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "gm_i.txt"
    _write_sample_source(source)

    result = runner.invoke(
        app,
        [
            "translate-chunk",
            "gm.i.s11",
            "--source",
            str(source),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Resolved chunk: GM.I.S11" in result.stdout


def test_translate_chunk_rejects_unknown_provider(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "gm_i.txt"
    _write_sample_source(source)

    result = runner.invoke(
        app,
        [
            "translate-chunk",
            "GM.I.S01",
            "--source",
            str(source),
            "--provider",
            "unknown",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "Unsupported provider" in result.stdout


def test_translate_all_chunks_dry_run_with_range(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "gm_i.txt"
    out_dir = tmp_path / "translations"
    _write_sample_source(source)

    result = runner.invoke(
        app,
        [
            "translate-all-chunks",
            "--source",
            str(source),
            "--out-dir",
            str(out_dir),
            "--provider",
            "gemini",
            "--from-ref",
            "GM.I.S01",
            "--to-ref",
            "GM.I.S11",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "would translate GM.I.S01" in result.stdout
    assert "would translate GM.I.S11" in result.stdout
    assert "total=2 done=2 skipped=0 failed=0" in result.stdout


def test_translate_all_chunks_invalid_range(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "gm_i.txt"
    _write_sample_source(source)

    result = runner.invoke(
        app,
        [
            "translate-all-chunks",
            "--source",
            str(source),
            "--from-ref",
            "GM.I.S11",
            "--to-ref",
            "GM.I.S01",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "from_ref must be <= to_ref" in result.stdout


def test_translate_all_chunks_invalid_requests_per_minute(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "gm_i.txt"
    _write_sample_source(source)

    result = runner.invoke(
        app,
        [
            "translate-all-chunks",
            "--source",
            str(source),
            "--requests-per-minute",
            "0",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "requests_per_minute must be > 0" in result.stdout
