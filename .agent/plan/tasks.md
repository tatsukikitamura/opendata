# 残タスク一覧

## 完了済み (Implemented)
- [x] **Backend Infrastructure**
    - [x] setup FastAPI & SQLite
    - [x] ODPT API Integration (`odpt_client.py`)
- [x] **Route Search Engine**
    - [x] Graph Construction (`route_graph.py`)
    - [x] Dijkstra Algorithm Implementation
- [x] **Timetable Integration**
    - [x] `StationDeparture` Model & Data Ingestion
    - [x] `train_number` based connection logic
    - [x] Accurate direction handling (`StationOrder`)
    - [x] Terminal station Arrival Time logic (`TrainTimetable`)
- [x] **Risk & Predictive Analysis**
    - [x] 運行情報API (`odpt:TrainInformation`) の取り込み
    - [x] 過去データに基づく「遅延リスク」の算出ロジック (`risk.py`)
    - [x] リアルタイム遅延情報の表示
- [x] **AI / Intelligence**
    - [x] OpenAI APIによる経路の定性診断 (`diagnoseRoute`)
    - [x] リスクレベルに応じたコンシェルジュコメント
- [x] **Frontend**
    - [x] Route Input UI
    - [x] Timeline Visualization
    - [x] Refactoring to `src/` component structure
    - [x] 駅名オートコンプリート
    - [x] Modern UI Design (Sora Font, Dynamic Coloring)

---

## 今後の課題 (Backlog)

### 1. サービス対象拡大
- [ ] 東京メトロ・都営地下鉄の完全対応 (現在一部GTFS対応)
- [ ] 私鉄各社（東急、小田急など）の対応

### 2. UX/UI 改善
- [ ] 「一本前/一本後」の検索
- [ ] 経由地の指定
- [ ] PWA化

### 3. パフォーマンス最適化
43: - [ ] DBインデックスのチューニング
44: - [ ] 経路探索アルゴリズムの高速化（A*などへの移行検討）
45: 
46: ### 4. 本番運用・デプロイ (Production)
47: - [ ] **PostgreSQL Migration**
48:   - [ ] Local PostgreSQL Setup (Docker)
49:   - [ ] SQLite to Postgres Data Migration Script
50:   - [ ] Update `database.py` for `DATABASE_URL`
51: - [ ] **Backend Deployment (DigitalOcean)**
52:   - [ ] Dockerfile Creation
53:   - [ ] DigitalOcean App Platform / Droplet Setup
54: - [ ] **Automation (GitHub Actions)**
55:   - [ ] Update Data Collection Script -> Direct DB Insert
56:   - [ ] Configure GitHub Secrets (`DB_HOST`, etc.)
57: - [ ] **Frontend Deployment**
58:   - [ ] GitHub Pages Setup
59:   - [ ] Connect to Production Backend

