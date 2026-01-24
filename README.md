# philosophy-blueprint
哲学テキストは「読む」だけでなく、「分析し、分解し、再構成し、検証できる」。  
哲学をIR化し、機械化できる部分はAIに任せ、理解すべき部分は人間が担うためのブループリント。

## 🎯 Purpose
- 暗黙知だった思考プロセスを明示的なデータ構造にする（claims / concepts / relations / maps）
- 機械が得意な部分は AI / 自動化に委譲し、理解の本質は人間が保持する
- 成果を再利用可能な知識モデルとして蓄積する

## 📦 What This Repository Provides
- `claims.yaml` : 哲学テキストから抽出された主張（Claim）の構造化
- `concepts.yaml` : 概念と概念間関係のモデル
- `map` : Mermaid などで出力する思想マップ
- CLI ツール `phblue`
  - 構造バリデーション
  - 翻訳支援（AI）
  - claims 抽出支援（AI）
  - map 生成
- Traceability : Claim → 原文参照を常に保持

## 🧩 AI と人間の分担
“哲学書を読む” の工程を分解し、役割を再設計。

| 工程 | 従来 | philosophy-blueprint |
| --- | --- | --- |
| 原文を読む | 人間 | そのまま or AI翻訳支援 |
| 逐語訳 | 人間 | ✅ AIが担当 |
| 重要箇所の抽出 | 人間 | ✅ AIが候補提示 |
| 主張構造を整理 | 人間（頭） | 🤝 AIが下書き、人がレビュー |
| 概念・関係の整理 | 人間 | 🤝 AI + 人間で確定 |
| 思想マップ化 | 人間 | ✅ 自動生成 |
| 「理解した」と言えるか | 人間 | 🔥 人間のみ（本質） |
| 批判・検証 | ゼミ/議論 | 🤖 AI壁打ち + 人の判断 |

👉 AI = 読む・拾う・並べる・可視化する  
👉 人間 = 理解する / 判断する / 自分の言葉で引き受ける

## 🏗 Repository Structure
```
analysis/         # 公開できる構造データ (claims / concepts / maps)
sources/          # 原文（非公開 / Git管理外）
translations/     # AI逐語訳（非公開 / Git管理外）
trace/            # Claim ←→ 原文紐付け
src/philosophy_blueprint/
  cli.py          # Typer CLI
  config.py
  models.py
```

## 🔑 Design Principles
- 原文の再配布はしない（著作権配慮）が、原文参照は必ず残す
- 「理解」は paraphrase としてデータ構造化する
- AIの出力は常に「候補」であり「権威」ではない
- 目指すのは「検証可能な哲学」

## 🧪 Using the Tool
```
uv run phblue info
uv run phblue validate-claims
```
（今後追加予定：`translate-chunk`, `extract-claims`, `build-map`, `review-claim` …）

## 📚 First Target Work
Friedrich Nietzsche — Zur Genealogie der Moral（道徳の系譜）  
まずは 第1論文 を対象に実験しています。

## 🧭 Vision
- 哲学書を「読む」だけでなく “コンパイル可能” にする
- 思想を 検索 / 比較 / 接続 できる形へ
- 初学者にも研究者にもメンテナンスできる哲学知識へ

philosophy-blueprint は「理解を助ける道具」であり、「理解を代替する装置」ではない。

## 📝 License

Code: MIT

Structured data: 現状は同様。ただし将来必要なら分離検討。
