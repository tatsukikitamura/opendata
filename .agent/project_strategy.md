# プロジェクト戦略とアーキテクチャの決定事項

## 1. 範囲（スコープ）の戦略
- **拡大ターゲット**: **JR東日本 + 東京メトロ + 都営地下鉄**
  - *現状*: JR東日本はODPT API、地下鉄はGTFSデータを活用して統合済み。
  - *理由*: 都内の主要な移動を網羅するため、地下鉄の統合が必須であったため。
- **将来的な拡張**: 私鉄各社（東急、小田急、京王など）の追加。

## 2. 経路探索（ナビゲーション）のアーキテクチャ
- **決定事項**: **ODPTデータに基づく独自のグラフ探索エンジン（Dijkstra法）を実装する。**
- **アプローチ**: `route_graph.py` にてグラフネットワークを構築し、Dijkstra法で最短経路・乗り換え経路を探索する。
  - *実装済*:
    - 駅・路線データのグラフ化（`Station` ノード / `Ride`・`Transfer` エッジ）。
    - 実際の時刻表データ (`StationDeparture`) と連携した「時刻表ベースのユニークな経路探索」。
- **外部API**: データソースとして利用し、ロジックは内部で計算。

## 3. アプリの提供価値（リスク＆AIエンジン）
- **Core Value**: **「予測型」リスク管理と「AIコンシェルジュ」による定性診断**。
- **ワークフロー**:
  1. **ユーザー入力**: 出発駅、到着駅、時刻。
  2. **経路探索**: 最短・最適経路を計算。
  3. **リスク評価 (Predictive Risk)**:
     - 過去の遅延統計データとリアルタイム情報を照合。
     - 「通常運行だが、統計的に遅延確率が高い」といった隠れたリスクを検出。
  4. **AI診断 (Qualitative Diagnosis)**:
     - OpenAI APIを用いて、経路の混雑度・イベント情報・リスクレベルを総合的に分析。
     - 「この経路は混むので避けたほうがいい」「雨予報なので乗り換えの少ないこちらがおすすめ」といった人間味のあるアドバイスを提供。

## 4. 技術スタック・バージョン (実績)

### Frontend
- **Framework**: Vite v6 + Vanilla JS (ESModules)
- **Styling**: TailwindCSS **v4**
- **Font**: Sora (English/Numbers) + Noto Sans JP (Japanese)
- **Design**: "Modern Professional" - Clean, Card-based, Risk-aware coloring.

### Backend
- **Language**: Python 3.12
- **Framework**: FastAPI (0.109+)
- **Database**:
  - **ORM**: SQLAlchemy (2.0+)
  - **DB**: SQLite (Production-ready for prototype)
- **AI Integration**: OpenAI API (GPT-4o/mini)
- **Data Processing**:
  - `pandas`: データ分析・統計処理
  - `gtfs-realtime-bindings`: GTFS-RTデータ処理
  - `apscheduler`: 定期タスク実行
