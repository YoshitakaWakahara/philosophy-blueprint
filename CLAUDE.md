# philosophy-blueprint

ニーチェ「道徳の系譜」第I論文（GM I）の逐語翻訳・分析ツール。
AIは翻訳・抽出・整形を担当し、最終判断は人間が行う。

---

## セットアップ

```bash
uv sync
cp .env.sample .env  # APIキーを設定
```

`.env` の設定項目：

```
OPENAI_API_KEY=xxxx
GEMINI_API_KEY=yyyy
```

- Gemini APIキー: Google AI Studio（aistudio.google.com）で発行
- 課金有効化: Google Cloud Console でプロジェクトに請求先アカウントをリンク

---

## リポジトリ構成

```
sources/genealogy_I/
  GM_I_full.txt        # 原文（英語）
  chunks/              # GM.I.S01〜S17（節ごとに分割済み）

analysis/genealogy_I/
  claims.yaml          # 主張リスト（コミット対象）

translations/genealogy_I/
  GM.I.S01.md ...      # 翻訳出力（コミットしない）

src/philosophy_blueprint/
  cli.py               # CLIエントリポイント（Typer）
  config.py            # APIキー読み込み
  chunking/            # テキスト分割ロジック
  translation/         # OpenAI / Gemini アダプター
```

**規約:**
- `analysis/` のみコミット対象。`sources/`, `translations/`, `trace/` はコミットしない
- 原文の再配布につながる内容は `analysis/` に置かない
- 参照IDは `GM.I.S01` 形式（ゼロ埋め2桁）を標準とする

---

## コマンド

すべて `uv run phblue <subcommand>` で実行。

| 目的 | コマンド |
|------|---------|
| 設定確認 | `uv run phblue info` |
| チャンク分割 | `uv run phblue divide-chunk` |
| 単一節を翻訳 | `uv run phblue translate-chunk GM.I.S01 --provider gemini` |
| 内容確認のみ | `uv run phblue translate-chunk GM.I.S01 --dry-run` |
| 全節を一括翻訳 | `uv run phblue translate-all-chunks --provider gemini` |
| 範囲指定で翻訳 | `uv run phblue translate-all-chunks --provider gemini --from-ref GM.I.S03 --to-ref GM.I.S17` |
| 上書き再翻訳 | `uv run phblue translate-all-chunks --provider gemini --overwrite` |
| claims検証 | `uv run phblue validate-claims` |
| テスト実行 | `uv run pytest` |

**モデル:**
- Gemini デフォルト: `models/gemini-2.5-flash`
- OpenAI デフォルト: `gpt-4.1-mini`

---

## 開発ガイドライン

**コーディング:**
- Python 3.9+ 前提
- 変更は最小差分で。既存CLIの設計（Typer + Pydantic）に合わせる
- 例外時は `typer.Exit(code=1)` で終了し、原因を表示する
- 新規機能は `--dry-run` など安全確認オプションを優先する
- 変更後は関連CLIコマンドを1つ実行して動作確認する

**出力品質:**
- 翻訳は要約せず、ニュアンス保持を優先
- Claim抽出は必ず原文参照（`sources.ref`）とセットにする
- 推測を出す場合は、推測であることを明示する
- 不明点は勝手に仕様を広げず、`analysis/genealogy_I/claims.yaml` と整合させる
