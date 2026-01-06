# 次期開発・運用ロードマップ to Production

本番運用に向けたデプロイ計画とアーキテクチャ移行の設計図です。

## 🎯 最終目標
**「完全自動化された、スケーラブルな遅延予測サービス」**
- ユーザーは Web (GitHub Pages) からアクセス。
- バックエンドは DigitalOcean 上で稼働。
- データは GitHub Actions が 10分ごとに自動収集し、クラウド上の PostgreSQL に蓄積。

---

## 🏗 アーキテクチャ構成

| レイヤー | 現在 (Prototype) | 目標 (Production) | 備考 |
|---|---|---|---|
| **Frontend** | Localhost | **GitHub Pages** | 静的ホスティング。バックエンドURLを環境変数で切り替え。 |
| **Backend** | Localhost (Uvicorn) | **DigitalOcean** | App Platform (Docker) または Droplet。 |
| **Database** | SQLite (`data.db`) | **PostgreSQL** | DigitalOcean Managed DB または Droplet内構築。 |
| **Automation** | Crontab / Manual | **GitHub Actions** | 10分毎に実行し、直接 PostgreSQL に INSERT する。 |

---

## 🗓 移行ステップ

### Phase 1: PostgreSQL 移行 (最難関・最優先)
SQLite から PostgreSQL への完全移行を行います。
- [ ] **ローカル開発環境の整備**: Docker Compose で PostgreSQL を立ち上げる。
- [ ] **ドライバ導入**: `psycopg2-binary` または `asyncpg` を導入。
- [ ] **DB接続設定の環境変数化**: `DATABASE_URL` で接続先を切り替えられるように `database.py` を改修。
- [ ] **スキーママイグレーション**: SQLite 特有の型（あれば）を修正し、PostgreSQL でテーブルを作成。
- [ ] **データ移行スクリプト**: 既存の `data.db` (SQLite) からデータを読み出し、PostgreSQL にバルクインサートするスクリプトを作成。

### Phase 2: バックエンドのコンテナ化 & デプロイ
DigitalOcean で動かすための準備。
- [ ] **Dockerfile 作成**: 軽量な Python イメージで構築。
- [ ] **DigitalOcean Setup**: App Platform または Droplet の契約。
- [ ] **デプロイ**: 環境変数を設定し、クラウド上で FastAPI を起動。
- [ ] **疎通確認**: クラウド上の API を叩いてデータが返ってくるか確認。

### Phase 3: 自動収集システムのクラウド化
現在ローカルやファイルベースで行っている収集を、クラウドDB直結に変更。
- [ ] **収集スクリプト改修**: JSONファイル保存ではなく、DB (`TrainStatus` テーブル) へ直接保存するように変更。
- [ ] **GitHub Actions 設定**:
  - `collect_delays.yml` を更新。
  - GitHub Secrets に `DB_HOST`, `DB_USER`, `DB_PASSWORD` などを設定。
  - 10分ごとの Cron 実行で、クラウドDBにデータが溜まる環境を構築。

### Phase 4: フロントエンド本番公開
- [ ] **本番ビルド設定**: `VITE_API_URL` を DigitalOcean の URL に差し替え。
- [ ] **GitHub Pages デプロイ**: `gh-pages` ブランチへの自動デプロイワークフロー作成。
- [ ] **E2Eテスト**: 本番環境での動作確認。

---

## ⚠️ 技術的課題・注意点

1.  **DB接続セキュリティ**:
    - GitHub Actions から DigitalOcean の DB に接続するため、DB のファイアウォール設定で IP制限を緩和するか（非推奨）、SSL接続を強制する必要がある。
2.  **コスト管理**:
    - DigitalOcean の DB (Managed) は固定費がかかるため、Droplet 内に Docker で DB を立てて節約するか検討が必要。
3.  **データ整合性**:
    - 移行中にデータ構造が変わる可能性があるため、バックアップを確実に取る。
