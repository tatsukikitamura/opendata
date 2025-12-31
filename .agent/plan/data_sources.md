# データソース（ODPT）

## 使用するAPI

| データ | 用途 | 取得頻度 |
|---|---|---|
| 路線系統情報 | 路線一覧の表示 | 初回のみ（マスター） |
| 運行情報 | リアルタイム遅延状況 | 5分ごと |
| 運行情報（履歴） | 遅延リスク算出用 | 定期蓄積 |

## エンドポイント（予定）

```
GET https://api.odpt.org/api/v4/odpt:Railway?acl:consumerKey={API_KEY}
GET https://api.odpt.org/api/v4/odpt:TrainInformation?acl:consumerKey={API_KEY}
```

## 必要な情報
- ODPTのAPIキー（要取得）
