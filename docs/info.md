# 応募作品情報

## 応募作品名*
Transit AI - Predictive Risk & Concierge

## 応募作品を公開しているURL*
https://tatsuki.dev/opendata/

## 作品の説明*
「ただの時刻表検索」ではない、次世代の乗換案内アプリケーションです。

過去の膨大な運行データを分析し、「その列車がどれくらいの確率で遅れるか」を予測するPredictive Risk（予測型リスク）エンジンと、生成AIによる定性的な移動診断を組み合わせました。

### 主な機能
1. **Predictive Risk Analysis**: 現在遅れていなくても、統計的に「この時間のこの路線は20%の確率で遅延する」といった潜在的リスクを可視化
2. **AI Concierge**: OpenAI GPT-4o-miniを活用し、「荷物が多い場合は別ルートが推奨」等の文脈を理解したアドバイスを提供
3. **Cost Analysis**: 運賃データに基づくコストパフォーマンス評価
4. **4軸スコア評価**: 速さ・快適・安定・安さの多角的なルート評価

### 技術スタック
- Backend: Python 3.12 / FastAPI / SQLite + SQLAlchemy / OpenAI API
- Frontend: Vite / JavaScript / Tailwind CSS v4
- Deploy: GitHub Pages (Frontend) / DigitalOcean App Platform (Backend)

## 作品の紹介資料*
<!-- TODO: スライドPDFをアップロード -->

## 作品の紹介動画（Youtube）のURL*
<!-- TODO: YouTubeにデモ動画をアップロード -->

## 作品の写真やスクリーンショットなど(5枚まで)*
<!-- TODO: UIスクリーンショットを用意 -->

## 作品のマニュアルURL
https://github.com/tatsukikitamura/opendata/blob/main/README.md
<!-- GitHubのURLを確認して更新してください -->

## 使用したオープンデータ*
* 公共交通オープンデータセンター: https://ckan.odpt.org/
    - JR東日本のGTFS・GTFS-RTデータ（リアルタイム運行情報）
    - 東京メトロの列車運行情報API
    - 都営地下鉄の運行データ
