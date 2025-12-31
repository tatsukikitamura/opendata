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
- [x] **Frontend**
    - [x] Route Input UI
    - [x] Timeline Visualization
    - [x] Refactoring to `src/` component structure

---

## 今後の課題 (Backlog)

### 1. 遅延リスク・混雑予測 (当初の目標)
- [ ] 運行情報API (`odpt:TrainInformation`) の取り込み
- [ ] リアルタイム遅延の経路探索への反映
- [ ] 過去データに基づく「遅延リスク」の算出ロジック再実装

### 2. UX/UI 改善
- [ ] 駅名オートコンプリート
- [ ] 「一本前/一本後」の検索
- [ ] 経由地の指定

### 3. パフォーマンス最適化
- [ ] DBインデックスのチューニング
- [ ] 大量データ取得時のバッチ高速化
