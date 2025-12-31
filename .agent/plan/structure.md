# ディレクトリ構造

> **注意**: これは実装完了後の**目標構造**です。現状とは異なる部分があります。

```
opendata/
├── .agent/
│   ├── plan/                    # 計画書
│   │   ├── overview.md
│   │   ├── ui_design.md
│   │   ├── data_sources.md
│   │   ├── tasks.md
│   │   └── structure.md         # このファイル
│   └── project_strategy.md      # プロジェクト戦略
│
├── backend/
│   ├── venv/                    # Python仮想環境
│   ├── main.py                  # FastAPIエントリポイント
│   ├── db/                      # データベース層
│   │   ├── __init__.py          # モジュールエクスポート
│   │   ├── database.py          # DB接続設定
│   │   └── models.py            # SQLAlchemyモデル
│   ├── services/                # サービス層（ビジネスロジック）
│   │   ├── __init__.py          # モジュールエクスポート
│   │   ├── odpt_client.py       # ODPT APIクライアント
│   │   ├── collector.py         # データ収集スクリプト
│   │   └── risk_calculator.py   # リスク算出ロジック
│   └── data.db                  # SQLiteデータベース
│
├── frontend/
│   ├── index.html               # ホーム画面（路線一覧）
│   ├── detail.html              # 路線詳細画面（※routes.html/result.htmlを統合）
│   ├── main.js                  # ホーム画面のJS
│   ├── detail.js                # 詳細画面のJS
│   ├── style.css                # Tailwind CSSエントリ
│   ├── vite.config.js           # Vite設定
│   └── package.json
│
└── README.md                    # プロジェクト説明
```

---

## ファイル詳細

### バックエンド

| ファイル | 役割 |
|---|---|
| `main.py` | APIルーティング（/lines, /lines/{id}/status など） |
| `database.py` | SQLite接続、セッション管理 |
| `models.py` | Line, TrainStatus などのテーブル定義 |
| `odpt_client.py` | ODPT APIへのHTTPリクエスト処理 |
| `collector.py` | 定期実行で運行情報を収集しDBに保存 |
| `risk_calculator.py` | 過去データから遅延リスクを算出 |

### フロントエンド

| ファイル | 役割 |
|---|---|
| `index.html` | 路線一覧カードを表示 |
| `detail.html` | 選択した路線のリスク詳細を表示 |
| `main.js` | API呼び出し、カードレンダリング |
| `detail.js` | API呼び出し、Chart.jsでグラフ描画 |
