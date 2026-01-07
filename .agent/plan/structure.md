# ディレクトリ構造

> **注意**: リアルタイム更新される現在の実装構造です。

```
opendata/
├── .agent/                  # エージェント用ドキュメント
│   ├── plan/                # 設計・計画書
│   │   ├── structure.md     # 本ファイル
│   │   ├── api_design.md    # API仕様
│   │   ├── db_schema.md     # DBスキーマ
│   │   ├── tasks.md         # タスク一覧
│   │   └── ...
│   └── project_strategy.md
│
├── backend/
│   ├── venv/
│   ├── main.py              # FastAPIエントリーポイント
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py      # DB接続設定
│   │   └── models.py        # SQLAlchemyモデル定義
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── search.py        # 経路探索API
│   │   ├── stations.py      # 駅情報API
│   │   └── timetable.py     # 時刻表API
│   ├── services/
│   │   ├── __init__.py
│   │   ├── odpt_client.py   # ODPT APIクライアント
│   │   ├── route_graph.py   # 経路グラフ構築・Dijkstra探索
│   │   ├── fetch_timetables.py    # 時刻表データ収集バッチ
│   │   ├── fetch_station_order.py # 駅順データ収集バッチ
│   │   ├── extract_travel_times.py # 所要時間算出バッチ
│   │   └── timetable/       # 探索ロジック詳細
│   │       ├── core.py      # コア探索ロジック
│   │       ├── finder.py    # 列車検索ロジック
│   │       ├── direction.py # 方向判定ロジック
│   │       ├── utils.py     # 時間ユーティリティ
│   ├── scripts/
│   │   ├── collect_delays.py # GTFS-RT収集
│   │   ├── import_delays.py  # DBインポート
│   │   ├── show_delay_rate.py # 遅延率分析
│   │   └── ...
│   ├── data/
│   │   └── delays/          # 収集したJSONLデータ
│   ├── data.db              # SQLiteデータベース
│
├── frontend/
│   ├── index.html           # 検索ページエントリ
│   ├── detail.html          # 結果ページエントリ
│   ├── vite.config.js       # Vite設定
│   ├── style.css            # Tailwindロード
│   └── src/
│       ├── components/
│       │   └── Timeline.js  # タイムライン表示コンポーネント
│       ├── pages/
│       │   ├── home.js      # 検索ページロジック
│       │   └── detail.js    # 結果ページロジック
│       └── lib/
│           ├── api.js       # API呼び出し
│           └── utils.js     # 共通ユーティリティ
│
└── README.md
```
