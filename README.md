# Transit AI - Predictive Risk & Concierge
(旧: 乗換案内 - 遅延リスク分析)

公共交通オープンデータチャレンジ2025 プロトタイプ

## 概要

**「ただの時刻表検索」ではありません。**
過去の膨大な運行データを分析し、「その列車がどれくらいの確率で遅れるか」を予測する**Predictive Risk（予測型リスク）エンジン**と、生成AIによる**定性的な移動診断**を組み合わせた、次世代の乗換案内アプリケーションです。

### 🚀 主な差別化機能

#### 1. 📊 Predictive Risk Analysis (予測型遅延リスク)
現在遅れていなくても、「過去の統計的にこの時間のこの路線は20%の確率で遅延する」といった**潜在的なリスク**を可視化します。
- **High Risk (赤)**: 遅延確率が高い、または現在遅延中。
- **Medium Risk (黄)**: 注意が必要。
- **Low Risk (緑)**: 平常運行かつ統計的にも安定。

#### 2. 🤖 AI Concierge (AI移動診断)
OpenAI APIを活用し、単なるデータだけでなく「コンシェルジュのようなアドバイス」を提供します。
- 「このルートは乗り換えが複雑で混雑しやすいため、荷物が多い場合は別ルートが推奨です」
- 「今日は近くでイベントがあるため、早めの移動をお勧めします」
といった、文脈を理解したサジェストを行います。

#### 3. 🎨 Modern & Intuitive UI
- **Sora Font** を採用した視認性の高いタイポグラフィ。
- リスクレベルに応じてUI全体のトーン（背景色など）が直感的に変化。
- 3軸スコア（速さ・快適・安定）による多角的なルート評価。

---

## 技術スタック

### Backend
- **Python 3.12** / **FastAPI**
- **SQLite + SQLAlchemy**: グラフデータと統計データの高速処理
- **OpenAI API**: GPT-4o-mini による診断
- **ODPT API & GTFS**: JR東日本、東京メトロ、都営地下鉄のデータを統合

### Frontend
- **Vite** / **Vanilla JS** (No Framework overhead)
- **Tailwind CSS v4**: 最新のスタイリングエンジン
- **Design System**: Glassmorphism, Adaptive Colors

---

## セットアップ (開発者向け)

### 1. 前提条件
- Python 3.12+
- Node.js 18+
- ODPT API Access Token
- OpenAI API Key

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .env を編集して ODPT_API_TOKEN と OPENAI_API_KEY を設定してください
```

### 3. Data Import
初回起動時はデータの取得とデータベース構築が必要です。
```bash
# データの取得とDB構築（数分かかります）
python scripts/setup_database.py
```

### 4. Start Server
```bash
uvicorn main:app --reload
```

### 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## ディレクトリ構成
```
.
├── backend/
│   ├── main.py              # Entry point
│   ├── routers/             # API Endpoints (AI, Search, Stations)
│   ├── services/            # Core Logic (Risk, Routing, Venue)
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
