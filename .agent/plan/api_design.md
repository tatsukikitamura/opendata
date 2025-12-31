# API設計仕様

## ベースURL
`http://localhost:8000`

---

## 経路探索 API

### 1. 時刻表付き経路検索
実際の時刻表データに基づき、乗り換え待ち時間を含めた正確な行程を算出する。

- **URL**: `/search_with_times`
- **Method**: `GET`

**パラメータ**:
| 名前 | 必須 | 説明 | 例 |
|---|---|---|---|
| from_station | Yes | 出発駅名 | `東京` |
| to_station | Yes | 到着駅名 | `新宿` |
| time | Yes | 出発希望時刻 | `10:00` |

**レスポンス**:
```json
{
  "from": "東京",
  "to": "新宿",
  "theoretical_time": 15.0,  // 合計所要時間（分）
  "transfers": 1,            // 乗換回数
  "requested_departure": "10:00",
  "segments": [              // 行程セグメントのリスト
    {
      "from": "東京",
      "to": "御茶ノ水",
      "railway": "中央線快速",
      "departure_time": "10:05", // 発車時刻
      "arrival_time": "10:09",   // 到着時刻
      "train_type": "Rapid",
      "destination": "Takao",
      "train_number": "1034T"
    },
    {
      "from": "御茶ノ水",
      "to": "新宿",
      "railway": "中央・総武各駅停車",
      "departure_time": "10:15",
      "arrival_time": "10:20",
      "train_type": "Local",
      ...
    }
  ]
}
```

**エラーレスポンス**:
- `404 Not Found`: 駅が見つからない場合
- `400 Bad Request`: ルートが見つからない、または入力不正

---

### 2. 単純経路検索 (Legacy)
時刻表を使わず、グラフ構造のみで理論上の最短経路を検索する（デバッグ用）。

- **URL**: `/search`
- **Method**: `GET`
- **パラメータ**: `from_station`, `to_station`

---

## その他 API

### 駅情報
- `GET /stations`: 登録されている駅一覧を返す（オートコンプリート用などを想定）
