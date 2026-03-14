# 開発ロードマップ

## 現状（2026-03-14時点）

### 完了済み

| フェーズ | 内容 | 状態 |
|---------|------|------|
| 基盤構築 | CLIツール `phblue`、Typer + Pydantic 設計 | ✅ |
| チャンク分割 | GM I 全文 → S01〜S17 に分割 | ✅ |
| AI翻訳 | S01〜S17 全節を Gemini で逐語翻訳 | ✅ |
| Claim構造定義 | `models.py` に Claim / ClaimsFile スキーマ定義 | ✅ |
| バリデーションCLI | `phblue validate-claims` | ✅ |

### データの現状

- `translations/genealogy_I/` に S01〜S17 の翻訳ファイルが揃っている
- `analysis/genealogy_I/claims.yaml` にサンプルclaimが2件（手動で書いたもの）
- `concepts.yaml` はまだ存在しない

---

## 今やること：Claim抽出（`extract-claims`）

翻訳が揃ったので、次は各節から「主張」を抽出してclaims.yamlに追加する。

### Claimのスキーマ（`models.py`より）

```yaml
- claim_id: GM.I.C01          # 連番ID
  type: genealogy              # genealogy / inversion / diagnosis / critique / distinction
  statement_ja: "..."          # 主張の一文（日本語）
  my_paraphrase: "..."         # 自分の言葉での解釈（人間が書く）
  concepts: ["NIETZ.XXX"]      # 関連概念ID
  sources:
    - ref: "GM I §2-3"         # 原文参照（必須）
```

### 実装方針

1. `phblue extract-claims <ref>` コマンドを追加
2. 翻訳テキスト + 原文チャンクをプロンプトに渡し、AIにClaim候補を出力させる
3. YAMLとしてパースし、既存の `claims.yaml` にマージ
4. `my_paraphrase` は空欄で出力し、人間がレビュー・記入する

### 品質ルール

- `sources.ref` は必ずセット（原文との紐付けが命）
- AIの出力は「候補」扱い。最終的な `my_paraphrase` は人間が書く
- `claim_id` は既存との重複を避けて採番する

---

## 次のステップ（Claim抽出の後）

### Step 3: 概念モデル化（`concepts.yaml`）

Claimから登場する概念を抽出し、概念間の関係を定義する。

```yaml
# concepts.yaml（想定フォーマット）
concepts:
  - concept_id: NIETZ.MORALITY_NOBLE
    label_ja: "主人道徳"
    definition_ja: "支配的階層が自己肯定から構築した価値体系"
    relations:
      - type: contradicts
        target: NIETZ.MORALITY_SLAVE
      - type: precedes
        target: NIETZ.VALUE_INVERSION
```

関係の型（候補）: `is_a`, `part_of`, `contradicts`, `precedes`, `transcends`

### Step 4: 思想マップ生成（`build-map`）

概念ネットワークを Mermaid 形式で出力する。

```bash
phblue build-map --format mermaid > analysis/genealogy_I/map.md
```

### Step 5（将来）: 比較・接続

- 複数の哲学者の概念ネットワークを接続する
- 「ニーチェの超人」と「仏教の解脱」の論理的距離を計算するなど
- Embeddingによるベクトル化は Step 4 以降の拡張として検討

---

## フェーズ全体像

```
[翻訳] → [Claim抽出] → [概念モデル化] → [マップ生成] → [比較・接続]
  ✅          ← 今ここ →
```
