# API設計仕様

## Base URL
`http://localhost:8000`

---

## 1. Route Search API

### `GET /search`
出発駅・到着駅・時刻を指定して、リスク分析済みの経路を検索します。

**Parameters:**
- `from_station`: 出発駅名 (例: `東京`)
- `to_station`: 到着駅名 (例: `高尾`)
- `time`: 出発時刻 `HH:MM` (例: `10:00`)

**Response:**
```json
{
  "routes": [
    {
      "segments": [
        {
          "railway": "中央線快速",
          "from": "東京",
          "to": "新宿",
          "departure_time": "10:00",
          "arrival_time": "10:14"
        }
      ],
      "transfers": 0,
      "risk": {
        "level": "HIGH", // HIGH, MEDIUM, LOW
        "score": 12.5,   // 遅延確率(%)
        "reasons": [
          {
            "railway": "ChuoRapid",
            "display": "ChuoRapid: 12.5%の遅延リスク"
          }
        ]
      },
      "crowd": {
        "level": "HIGH",
        "score": 450000,
        "details": ["新宿(極めて混雑)"]
      },
      "scores": {
        "speed": 4.5,      // 5段階評価
        "comfort": 2.0,
        "reliability": 1.5
      },
      "delay_warnings": [], // リアルタイム遅延情報
      "venue_warnings": {   // イベント会場情報
        "transfer_warnings": [],
        "passing_info": []
      }
    }
  ]
}
```

---

## 2. AI Diagnosis API

### `POST /ai/diagnose`
経路情報を受け取り、OpenAI APIを使用して定性的なアドバイスと診断を行います。

**Request Body:**
```json
{
  "segments": [...],     // /search のレスポンスと同じ
  "risk": {...},         // /search のレスポンスと同じ
  "crowd": {...},
  "venue_warnings": {...},
  "delay_warnings": [...]
}
```

**Response:**
```json
{
  "diagnosis": "⚠️ 警告モード ⚠️\nこのルートは中央線快速の遅延リスクが高いため注意が必要です...",
  "model": "gpt-4o-mini"
}
```

---

## 3. Utility API

### `GET /stations`
駅名オートコンプリート用の駅一覧を返します。
- **Response**: `["東京", "新宿", "高尾", ...]`
