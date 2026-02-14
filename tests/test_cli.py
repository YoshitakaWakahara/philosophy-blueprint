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
