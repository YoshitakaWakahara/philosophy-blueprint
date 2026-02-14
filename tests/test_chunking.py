from __future__ import annotations

import pathlib

import pytest

from philosophy_blueprint.chunking import build_genealogy_i_chunk_map
from philosophy_blueprint.chunking import normalize_ref


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
                "Alpha line 2",
                "",
                "11",
                "",
                "Beta line 1",
                "",
                "12.",
                "",
                "Gamma line 1",
                'SECOND ESSAY. "GUILT," "BAD CONSCIENCE," AND THE LIKE.',
            ]
        ),
        encoding="utf-8",
    )


def test_build_chunk_map_supports_heading_without_dot(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "sample.txt"
    _write_sample_source(source)

    chunk_map = build_genealogy_i_chunk_map(source)

    assert list(chunk_map.keys()) == ["GM.I.S01", "GM.I.S11", "GM.I.S12"]
    assert "Alpha line 1" in chunk_map["GM.I.S01"]
    assert "Beta line 1" in chunk_map["GM.I.S11"]
    assert "Gamma line 1" in chunk_map["GM.I.S12"]


def test_normalize_ref_accepts_variants() -> None:
    assert normalize_ref("GM.I.S1") == "GM.I.S01"
    assert normalize_ref("gm.i.s11") == "GM.I.S11"
    assert normalize_ref(" GM.I.S09 ") == "GM.I.S09"


def test_normalize_ref_rejects_invalid() -> None:
    with pytest.raises(ValueError):
        normalize_ref("GM.II.S01")
