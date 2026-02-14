from __future__ import annotations

import pathlib

from philosophy_blueprint.translation import write_translation_file


def test_write_translation_file_includes_metadata(tmp_path: pathlib.Path) -> None:
    out_file = write_translation_file(
        output_dir=tmp_path,
        ref="GM.I.S01",
        source="sources/genealogy_I/GM_I_full.txt",
        provider="gemini",
        model="gemini-2.5-flash",
        translated_text="翻訳本文",
    )

    text = out_file.read_text(encoding="utf-8")
    assert "## Metadata" in text
    assert "- ref: GM.I.S01" in text
    assert "- provider: gemini" in text
    assert "- model: gemini-2.5-flash" in text
    assert "- generated_at_utc:" in text
