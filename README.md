# 乗換案内 - 遅延リスク分析

公共交通オープンデータチャレンジ2025 プロトタイプ

## 概要

過去の遅延実績データに基づいて、経路の遅延リスクを予測する乗換案内アプリケーションです。

### 主な機能

- 🚃 **時刻表ベースのルート検索** - ODPT APIの時刻表データを使用
- 📊 **遅延リスク分析** - 過去の遅延データから路線ごとのリスクを算出
- 🎪 **イベント会場警告** - 経路上の大規模イベント会場を通知
- 👥 **混雑度予測** - 駅の乗降客数データから混雑レベルを推定

## 技術スタック

### Backend
- **FastAPI** - Python製の高速Webフレームワーク
- **SQLite** - 時刻表・遅延データの永続化
- **SQLAlchemy** - ORM

### Frontend
- **Vite** - 高速なビルドツール
- **Vanilla JavaScript** - フレームワークなし
- **Tailwind CSS v4** - ユーティリティファーストCSS

## ディレクトリ構成

```
.
├── backend/
│   ├── main.py              # FastAPIエントリーポイント
│   ├── routers/             # APIエンドポイント
│   │   ├── search.py        # ルート検索API
│   │   └── stations.py      # 駅オートコンプリートAPI
│   ├── services/            # ビジネスロジック
│   │   ├── routing.py       # グラフベースの経路探索
│   │   ├── timetable/       # 時刻表検索
│   │   ├── risk.py          # 遅延リスク計算
│   │   └── venue.py         # イベント会場警告
│   ├── db/                  # データベース設定・モデル
│   ├── scripts/             # データ取得・インポートスクリプト
│   └── data/                # 静的データ（GTFSなど）
│
├── frontend/
│   ├── index.html           # ホームページ
│   ├── detail.html          # 検索結果・詳細ページ
│   ├── style.css            # グローバルスタイル
│   └── src/
│       ├── pages/           # ページロジック
│       ├── components/      # UIコンポーネント
│       └── lib/             # ユーティリティ
│
└── .github/
    └── workflows/
        └── collect_delays.yml  # 遅延データ定期収集
```

## API

### `GET /search`

ルート検索

| パラメータ | 説明 |
|-----------|------|
| `from_station` | 出発駅（日本語） |
| `to_station` | 到着駅（日本語） |
| `time` | 出発時刻（HH:MM） |

### `GET /stations/autocomplete`

駅名オートコンプリート

| パラメータ | 説明 |
|-----------|------|
| `q` | 検索クエリ |

## データソース

- [公共交通オープンデータセンター (ODPT)](https://developer.odpt.org/)
  - JR東日本 時刻表
  - 東京メトロ GTFS
  - 都営地下鉄
- 遅延データ: GitHub Actions による定期収集

## ライセンス

MIT License
