# API設計

## ベースURL
```
http://localhost:8000/api/v1
```

---

## エンドポイント一覧

| メソッド | パス | 説明 |
|---|---|---|
| GET | `/lines` | 路線一覧を取得 |
| GET | `/lines/{line_id}` | 路線詳細を取得 |
| GET | `/lines/{line_id}/status` | 現在の運行状況を取得 |
| GET | `/lines/{line_id}/risk` | 遅延リスク分析を取得 |

---

## 詳細

### GET `/lines`
路線一覧を取得する。

**レスポンス**
```json
{
  "lines": [
    {
      "id": "odpt.Railway:JR-East.ChuoRapid",
      "name": "中央線快速",
      "color": "#F15A22",
      "current_status": "normal"
    }
  ]
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| id | string | 路線ID（ODPT形式） |
| name | string | 路線名（日本語） |
| color | string | ラインカラー（HEX） |
| current_status | string | 現在の状況（normal/delay/suspended） |

---

### GET `/lines/{line_id}`
指定した路線の詳細情報を取得する。

**パラメータ**
- `line_id`: 路線ID

**レスポンス**
```json
{
  "id": "odpt.Railway:JR-East.ChuoRapid",
  "name": "中央線快速",
  "color": "#F15A22",
  "stations": ["東京", "神田", "御茶ノ水", "..."],
  "operator": "JR東日本"
}
```

---

### GET `/lines/{line_id}/status`
指定した路線の現在の運行状況を取得する。

**レスポンス**
```json
{
  "line_id": "odpt.Railway:JR-East.ChuoRapid",
  "status": "delay",
  "status_text": "遅延",
  "cause": "混雑の影響",
  "updated_at": "2025-12-29T22:30:00+09:00"
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| status | string | normal / delay / suspended |
| status_text | string | 日本語表記 |
| cause | string | 原因（あれば） |
| updated_at | datetime | 最終更新日時 |

---

### GET `/lines/{line_id}/risk`
指定した路線の遅延リスク分析を取得する。

**クエリパラメータ**
- `hour` (optional): 時間帯（0-23）

**レスポンス**
```json
{
  "line_id": "odpt.Railway:JR-East.ChuoRapid",
  "probability": 75,
  "level": "High",
  "description": "過去7日間で遅延率が高い路線です。",
  "hourly_breakdown": [
    {"hour": 7, "probability": 85},
    {"hour": 8, "probability": 90},
    {"hour": 9, "probability": 60}
  ],
  "advice": "朝8時台は特に遅延が発生しやすいです。余裕を持って出発しましょう。"
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| probability | int | 遅延確率（0-100） |
| level | string | Low / Medium / High |
| hourly_breakdown | array | 時間帯別の遅延確率 |
| advice | string | アドバイステキスト |
