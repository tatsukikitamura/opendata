# Transit AI - Predictive Risk & Concierge

公共交通オープンデータチャレンジ2025

## 概要

**「ただの時刻表検索」ではありません。**
過去の膨大な運行データを分析し、「その列車がどれくらいの確率で遅れるか」を予測する**Predictive Risk（予測型リスク）エンジン**と、生成AIによる**定性的な移動診断**を組み合わせた、次世代の乗換案内アプリケーションです。

### 🚀 主な差別化機能

#### 1. 📊 Predictive Risk Analysis (予測型遅延リスク)
現在遅れていなくても、「過去の統計的にこの時間のこの路線は20%の確率で遅延する」といった**潜在的なリスク**を可視化します。
- **High Risk (赤)**: 遅延確率が高い、または現在遅延中。
- **Medium Risk (黄)**: 注意が必要。
- **Low Risk (緑)**: 平常運行かつ統計的にも安定。

#### 1.5. 💰 Cost Analysis (安さ)
- **速さ・快適さユーザーだけでなく、「安さ」を重視するユーザー向けの評価軸を追加。**
- 実際の運賃データに基づき、ルートのコストパフォーマンスをスコア化します。

#### 2. 🤖 AI Concierge (AI移動診断)
OpenAI APIを活用し、単なるデータだけでなく「コンシェルジュのようなアドバイス」を提供します。
- 「このルートは乗り換えが複雑で混雑しやすいため、荷物が多い場合は別ルートが推奨です」
- 「今日は近くでイベントがあるため、早めの移動をお勧めします」
といった、文脈を理解したサジェストを行います。

#### 3. 🎨 Modern & Intuitive UI
- **Sora Font** を採用した視認性の高いタイポグラフィ。
- リスクレベルに応じてUI全体のトーン（背景色など）が直感的に変化。
- 4軸スコア（速さ・快適・安定・安さ）による多角的なルート評価。

---

## 技術スタック

### Backend
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![OpenAI](https://img.shields.io/badge/OpenAI-412991.svg?style=for-the-badge&logo=openai&logoColor=white) ![DigitalOcean](https://img.shields.io/badge/DigitalOcean-%230167ff.svg?style=for-the-badge&logo=digitalOcean&logoColor=white)

- **Python 3.12** / **FastAPI**
- **SQLite + SQLAlchemy**: グラフデータと統計データの高速処理
- **OpenAI API**: GPT-4o-mini による診断
- **ODPT API & GTFS**: JR東日本、東京メトロ、都営地下鉄のデータを統合

### Frontend
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![GitHub Pages](https://img.shields.io/badge/github%20pages-121013?style=for-the-badge&logo=github&logoColor=white)

- **Vite** / **JavaScript** (No Framework overhead)
- **Tailwind CSS v4**: 最新のスタイリングエンジン
- **Design System**: Glassmorphism, Adaptive Colors

### Deployment Architecture
**完全自動化された、スケーラブルな遅延予測サービス** を目指し、以下の構成で運用します。

| Layer | Service | Details |
|---|---|---|
| **Frontend** | **GitHub Pages** | 静的ホスティング。`VITE_API_URL`でバックエンドと通信。 |
| **Backend** | **DigitalOcean App Platform** | Dockerコンテナとしてデプロイ。オートスケール対応。 |
| **Database** | **DO Managed PostgreSQL** | SQLiteから移行。フルマネージドで運用。 |
| **Automation** | **GitHub Actions** | 10分毎にデータを収集し、直接DBへINSERT。 |


---

## ディレクトリ構成
```
.
├── backend/
│   ├── main.py              # Entry point
│   ├── routers/             # API Endpoints (AI, Search, Stations)
│   ├── services/            # Core Logic (Risk, Routing, Venue)
│   ├── scripts/             # Data fetchers & importers
│   │   ├── fetchers/        # Raw data collectors
│   │   └── importers/       # DB importers
│   └── data/                # Raw Data & SQLite DB
│
└── frontend/
    ├── src/
    │   ├── components/      # UI Components (Timeline, Risk Cards)
    │   └── pages/           # Page Logic
    └── index.html
```

## ライセンス
MIT License
