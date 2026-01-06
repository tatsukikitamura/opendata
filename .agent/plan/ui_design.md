# UI設計 (Modern Professional)

## デザインコンセプト
- **Predictive & Calm**: 赤・黄・緑のカラーコードでリスクを直感的に伝達。
- **Sora Font**: 数字と欧文に可読性の高いSoraフォントを採用。
- **Glassmorphism**: モダンなカードUIと透過背景。

---

## 画面構成

```
[Home (Search)] → [Preview List] → [Route Detail & Diagnosis]
```

---

## 1. Route List (検索結果一覧)
複数の経路候補をカード形式で比較表示。

### カード要素
- **左側**: 到着時刻 (Big Bold) / 出発時刻 / 所要時間
- **中央**: **3軸スコア (3-Axis Scores)**
  - ⚡ 速さ (Speed)
  - 🛋️ 快適 (Comfort)
  - 🛡️ 安定 (Reliability)
  - *各項目をプログレスバーと数値(5.0満点)で可視化*
- **右側**: リスクラベル (遅延リスク高 / 注意 / 平常運行)

---

## 2. Route Detail (詳細画面)

### ヘッダー情報
- 経路サマリー (発着時刻・所要時間・乗換回数)
- **Dynamic Background**: リスクレベルに応じて背景色が変化。
  - High: Red Gradient
  - Medium: Amber Gradient
  - Low: Emerald Gradient

### Risk Analysis Accordions (リスク分析)
情報を以下のセクションに整理し、アコーディオンで展開。
1. **🚨 リアルタイム遅延**: 現在発生している遅延情報（最優先）。
2. **⚠️ 予測型リスク (Predictive Risk)**: 過去データに基づく遅延確率。「通常運行」でも表示。
3. **🎪 イベント情報**: 沿線の会場（東京ドーム等）のイベント有無。
4. **📊 駅混雑度**: 経由駅の乗降客数データ。

### AI Concierge (AI診断)
- **「診断開始」ボタン**: ユーザーのアクションで起動。
- **診断結果**:
  - GPT-4o-mini による定性コメント。
  - リスクレベルに応じて「警告モード」「注意モード」「安心モード」とトーンが変化。
  - 具体的なアドバイス（「少し早めに出ましょう」「トイレは済ませておきましょう」等）を提示。

### Timeline
- 縦型のタイムラインで乗車・乗換を表示。
- 駅間のみならず、リスク情報も統合的に表示。

---

## 3. Style Guide
- **Colors**:
  - Primary: Slate-800
  - Risk High: Red-600 / Red-50
  - Risk Medium: Amber-500 / Amber-50
  - Risk Low: Emerald-600 / Emerald-50
- **Typography**:
  - Headings/Numbers: `Sora`
  - Body (Japanese): `Noto Sans JP`
