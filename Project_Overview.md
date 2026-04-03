# Phase 1 プロジェクト定義
## モータ／ファンの異常兆候検知 ＋ 原因候補トリアージ

> Phase 1 は「Agent を載せるための**壊れない診断エンジン**を作るフェーズ」

- ❌ Agent / LLM はまだ使わない
- ✅ 設計・型・状態・不変式・ワークフローが主役
- ✅「現場で説明できる診断」がゴール

---

## 問題設定

工場のモータ／ファンについて、振動 1ch ＋ 温度の時系列データを使い、以下を実現する診断支援ロジックを設計・実装する。

1. 異常兆候を早期に検知する
2. 異常時に考えられる原因候補を順位付きで提示する
3. なぜそう判断したかを説明可能な形で返す

---

## Input / Output

### Input

| 項目 | 内容 |
|---|---|
| 対象 | 1台のモータ／ファン |
| センサ | 振動 1ch（時系列）、温度（時系列） |
| 診断ウィンドウ | 例：直近 60分 / 24時間 |

```
time, vibration, temperature
t0, 0.21, 42.1
t1, 0.22, 42.3
...
```

### Output：`DiagnosisReport`

「スコアだけ返す」は NG。**説明できる診断**が必須。

| フィールド | 内容 |
|---|---|
| 異常スコア | 0.0–1.0 |
| 状態分類 | `NORMAL` / `WARNING` / `ANOMALY` |
| 原因候補 Top 2 | 例：`bearing_wear`, `overheating` |
| 根拠 Evidence | どの特徴量がどう異常だったか |
| データ品質評価 | 欠損率 / ノイズ過多 / 判断不能フラグ |
| 次のアクション提案 | 例：点検推奨 / 継続監視 / 追加センサ必要 |

---

## 想定する故障モード（最小限）

本格的な故障モードの網羅はPhase 2以降。Phase 1では「雰囲気が出る最小限」に絞り、学習効率を優先する。

| MODE | 内容 |
|---|---|
| `normal` | 正常状態 |
| `overheating` | 温度トレンドが明確に上昇 |
| `vibration_spike` | 振動RMSが上昇 |

この3パターンで `DiagnosisReport` の `root_cause_candidates` と `Evidence` に複数候補が入り、Phase 2 で LLM に渡す素材として十分機能する。

---

## 診断ロジックの大原則

- 機械学習で分類しない
- **ルール × 特徴量 × 物理的な説明**で判断する

これは Robust Python（不変式・型）と Architecture Patterns（Domain / Service 層）の両方に直結する。

---

## ドメインモデル設計（概念）

```
Machine
SensorSnapshot        ← 時系列の整合性を保つ器（不変式の主役）
DiagnosisConfig       ← 機械ごとの診断設定
FeatureSet            ← 抽出された特徴量
AnomalyScore
Evidence              ← どの特徴量がどう異常だったか
DiagnosisCandidate
DiagnosisReport       ← 正常に診断できた場合の結果
DiagnosisUnavailable  ← 診断続行不可の場合（理由・根拠付き）
```

`DiagnosisResult = DiagnosisReport | DiagnosisUnavailable`

---

## 不変式（Robust Python が直撃する箇所）

「物理的にあり得ない状態」を最初に弾く。

| 不変式 | 内容 |
|---|---|
| 時系列の単調増加 | `time` が単調増加していること |
| 必須キーの存在 | `temperature`, `vibration` が両方存在すること |
| 長さの一致 | `time` と各センサデータの長さが一致すること |
| 欠損率の上限 | 欠損率 > X% → 診断不可 |
| サンプリング間隔のばらつき | 間隔のばらつきが許容範囲内であること |
| 温度のハードウェア仕様範囲 | -50〜150℃ の範囲外 → センサ故障として即エラー |

### 不変式とバリデーションの分離方針

| チェック | 性格 | 置く場所 |
|---|---|---|
| 長さ一致・必須キー | オブジェクトの存在条件（不変式） | `SensorSnapshot.__post_init__` |
| 温度ハードウェア仕様 | センサ故障の検出（バリデーション） | `check_sensor_validity`（ドメインサービス） |
| 稼働条件（operating range 等） | 診断続行可否の判定 | `check_operating_condition`（ドメインサービス） |

`assert` ではなく `raise` を使う。理由は `assert` は `-O` フラグで無効化されるため、本番防衛には不適切。

---

## レイヤー構成

```
Presentation / Infra 層   pydantic, SQLAlchemy 等を自由に使う
        ↓ 変換
Application 層（workflow）  diagnose() などのユースケース調整
        ↓
Domain 層                  標準ライブラリのみ。振る舞いとデータに集中
```

ドメイン層はサードパーティライブラリに依存させない。pydantic はインフラ・API 境界にとどめる。

---

## 固定ワークフロー（Phase 1）

Agent ではなく固定ワークフロー。**ここが後で Agent に置き換わる場所**。

```
1. 検証（型・不変式）
2. センサ故障チェック       → check_sensor_validity()
3. 稼働条件チェック         → check_operating_condition()
4. データ品質評価
5. 特徴量抽出
6. 異常兆候スコアリング
7. 原因候補生成（ルールベース）
8. 根拠付きレポート生成
```

---

## Phase 1 完了条件

- [ ] `diagnose(machine_id, window)` が動く
- [ ] 異常／正常を安定して区別できる
- [ ] 原因候補が説明付きで返る
- [ ] 型・dataclass が使われている
- [ ] 失敗理由がログ／例外で追える

UI は不要。CLI または Python 関数で OK。

---

## 学習上の位置づけ

| 学習内容 | このプロジェクトでの対応箇所 |
|---|---|
| Architecture Patterns with Python | Repository Pattern、Ports & Adapters、Service Layer |
| Robust Python | 不変式、型、例外設計、`raise` vs `assert` |
| Effective Python | 副作用・状態・境界条件を意識したコード |

Phase 2 では「この診断を Agent が対話で進める」形に自然に進化できる。
