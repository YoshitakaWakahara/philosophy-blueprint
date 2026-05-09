# AGENTS.md

このファイルは、このリポジトリで作業するAIコーディングエージェント向けの恒久ガイドです。

## 1. Project Goal

- 哲学テキストを「検証可能な構造データ（claims/concepts/maps）」として扱う。
- AIは下書き・抽出・翻訳・整形を担当し、最終判断は人間が行う。

## 2. Repository Rules

- `analysis/` はコミット対象の構造データ置き場。
- `sources/`, `translations/` は原文・生成物。`.gitignore` によりコミットしない。
- `trace/` は読解プロセスの記録。コミット対象。
- 原文の再配布につながる内容は `analysis/` に置かない。

## 3. Current Commands

- 環境確認: `uv run phblue info`
- claims 検証: `uv run phblue validate-claims`
- GM I 節分割: `uv run phblue divide-chunk --force`
- 単一節翻訳（テスト）: `uv run phblue translate-chunk GM.I.S01 --dry-run`
- 単一節翻訳（実行）: `uv run phblue translate-chunk GM.I.S01`

## 4. Chunk/Ref Conventions

- 参照IDは `GM.I.S01` 形式（ゼロ埋め2桁）を標準とする。
- 節見出しは原文の表記揺れ（`11` / `11.`）を許容して正規化する。
- GM I の分割対象は `FIRST ESSAY` 本文のみ（目次・他論文は除外）。

## 5. Coding Style

- Python 3.9+ 前提。
- 変更は最小差分で行い、既存CLIの設計（Typer + Pydantic）に合わせる。
- 例外時は `typer.Exit(code=1)` で終了し、原因を表示する。
- 新規機能は `--dry-run` など安全確認オプションを優先する。

## 6. Output Quality Bar

- 翻訳は要約せず、ニュアンス保持を優先。
- Claim抽出は必ず原文参照（`sources.ref`）とセットにする。
- 推測を出す場合は、推測であることを明示する。

## 7. Working Agreement

- 不明点は勝手に仕様を広げず、まず既存データ（`analysis/genealogy_I/claims.yaml`）と整合させる。
- 破壊的な操作（履歴破壊・大量削除）は行わない。
- 変更後は少なくとも関連CLIコマンドを1つ実行して動作確認する。
