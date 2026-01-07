# 次期開発・運用ロードマップ to Production

本番運用に向けたデプロイ計画とアーキテクチャ移行の設計図です。
GitHub Student Developer Pack の特典を最大限活用し、コストを抑えつつ高品質な環境を構築します。

## 🎯 最終目標
**「完全自動化された、スケーラブルな遅延予測サービス」**
- **Architecture**: DigitalOcean (Backend/DB) + GitHub Pages (Frontend)
- **Status**: Production Ready
- **Cost**: 実質無料 (Student Pack Credits 利用)

---

## 🏗 アーキテクチャ構成

| レイヤー | 現在 (Prototype) | 目標 (Production) | サービス / プラン |
|---|---|---|---|
| **Frontend** | Localhost | **GitHub Pages** | 無料。静的ホスティング。`VITE_API_URL`でバックエンドと通信。 |
| **Backend** | Localhost (Uvicorn) | **DigitalOcean App Platform** | $200 Credit利用。Dockerコンテナとしてデプロイ。オートスケール対応。 |
| **Database** | SQLite (`data.db`) | **DO Managed PostgreSQL** | $200 Credit利用。フルマネージド（バックアップ・保守不要）。 |
| **Monitoring** | ログ出力のみ | **Sentry** (Optional) | 本番環境でのエラー監視・通知。（必要に応じて導入） |
| **Automation** | Manual | **GitHub Actions** | 10分毎にデータ取込 → DO上のDBへ直接INSERT (SSL接続)。 |

---

## 🗓 移行ステップ

### Phase 1: PostgreSQL 移行 & DB設計強化 (最優先)
SQLite から PostgreSQL への移行に加え、**Alembic** を導入してスキーマ管理をコード化します。
- [ ] **Alembic 導入**: `pip install alembic`。DBマイグレーション環境を初期化。
- [ ] **DBサーバ構築**: DigitalOcean 上で Managed PostgreSQL を作成（$15/mo plan等の範囲内で）。
- [ ] **DB接続設定**:
    - 本番: **SSL mode=require** を必須とし、Trusted Sources（IP制限）は使用しない（GitHub Actions対応のため）。
    - 開発: ローカルDocker または Cloud DB に接続。
- [ ] **初期マイグレーション**: 現在のモデル定義から Alembic で初期リビジョンを作成し、PostgreSQL にテーブルを作成。
- [ ] **データ移行**: 現在の `data.db` (SQLite) の内容を PostgreSQL に投入するスクリプト作成＆実行。

### Phase 2: バックエンドのクラウド化
DigitalOcean App Platform へのデプロイ。
- [ ] **Dockerfile 最適化**: 本番運用向けに軽量化・セキュリティ設定。
- [ ] **CORS設定**: `main.py` にて GitHub Pages のドメイン (`https://<user>.github.io`) からのアクセスを許可。
- [ ] **App Platform Setup**: GitHub リポジトリと連携し、自動デプロイ設定。
- [ ] **環境変数設定**: `ODPT_ACCESS_TOKEN`, `OPENAI_API_KEY`, `DATABASE_URL` を設定。

### Phase 3: 自動収集システムの常時稼働
GitHub Actions を利用した定期データ収集。
- [ ] **Actions Secrets 更新**: Cloud DB の接続情報をGitHub Secretsに登録（SSL接続用のパラメータ含む）。
- [ ] **収集ワークフロー改修**: `collect_delays.py` がファイル保存ではなく、直接 DB (`TrainStatus` テーブル) へ INSERT するモードを作成。
- [ ] **Cron 有効化**: 10分ごとの定期実行をオンにする。

### Phase 4: フロントエンド本番公開
- [ ] **Production Build**: バックエンドURLを本番用に書き換えてビルド。
- [ ] **Deploy**: `gh-pages` ブランチへデプロイし、一般公開。

---

## ⚠️ 技術的課題・注意点

1.  **DB接続セキュリティ (GitHub Actions)**:
    - DigitalOcean の "Trusted Sources" 機能は IP アドレスでの制限であり、GitHub Actions の動的で広範な IP 帯域をカバーするのは不可能です。
    - **対策**: IP制限は行わず、**SSL認証 (`sslmode=require`)** を強制し、複雑で強固なパスワードによってセキュリティを担保します。
2.  **CORS (Cross-Origin Resource Sharing)**:
    - Frontend (GitHub Pages) と Backend (DigitalOcean) のドメインが異なるため、ブラウザが通信をブロックしないよう、バックエンド側で適切な CORS ヘッダー設定が必須。
3.  **クレジット期限**:
    - DigitalOcean の $200 クレジットは有効期限（通常1年）があるため、期限切れ後のコスト（月額$20程度〜）を意識しておく。
