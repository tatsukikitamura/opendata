# データソース（ODPT）

## 使用するAPI

| データ | 用途 | 取得頻度 |
|---|---|---|
| 路線系統情報 | 路線一覧の表示 | 初回のみ（マスター） |
| 運行情報 | リアルタイム遅延状況 | 5分ごと |
| 運行情報（履歴） | 遅延リスク算出用 | 定期蓄積 |

## エンドポイント（予定・実績）

```
# マスターデータ
GET https://api.odpt.org/api/v4/odpt:Railway?acl:consumerKey={API_KEY}
GET https://api.odpt.org/api/v4/odpt:Station?acl:consumerKey={API_KEY}

# リアルタイムデータ (GTFS-RT)
GET https://api.odpt.org/api/v4/gtfs/realtime/JR-East_Train?acl:consumerKey={API_KEY}
```

## データ収集パイプライン
- **GitHub Actions**: 10分ごとに `collect_delays.py` を実行し、GTFS-RTデータを `backend/data/delays/` にJSONL形式で保存・コミットする。
- **DBインポート**: ローカル環境等で `import_delays.py` を実行し、蓄積されたJSONLデータをSQLiteにロードして分析に利用する。


## 必要な情報
- ODPTのAPIキー（要取得）
