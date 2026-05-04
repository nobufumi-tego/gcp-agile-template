---
name: deploy-gcp
description: GCPへのデプロイを安全に実行する。コスト確認・テスト通過・レビュー承認を確認してからデプロイする。
user-invocable: true
---

# GCPデプロイスキル

## 実行前チェック（すべて必須）

### 1. テスト確認
```bash
cd backend && uv run pytest --tb=short
# → 全件グリーンでなければ中止
```

### 2. コスト見積もり表示
```bash
# 現在の使用量確認
gcloud billing budgets list
gcloud run services describe $SERVICE_NAME \
  --region=asia-northeast1 \
  --format="value(status.observedGeneration)"
echo "---"
echo "デプロイ前にコスト影響を確認してください"
echo "Cloud Run 無料枠: 200万req/月・360,000vCPU秒/月"
```

### 3. レビュー確認
- review-agent の承認コメントが docs/sprints/sprint-N/ にあること

## バックエンドデプロイ（Cloud Run）
```bash
# イメージビルド
gcloud builds submit backend/ \
  --tag asia-northeast1-docker.pkg.dev/$PROJECT_ID/$APP_NAME/api:$(git rev-parse --short HEAD)

# Cloud Run デプロイ
gcloud run deploy $APP_NAME-api \
  --image asia-northeast1-docker.pkg.dev/$PROJECT_ID/$APP_NAME/api:$(git rev-parse --short HEAD) \
  --region asia-northeast1 \
  --min-instances 0 \
  --max-instances 10 \
  --memory 512Mi \
  --timeout 60

# デプロイ確認
gcloud run services describe $APP_NAME-api \
  --region asia-northeast1 \
  --format="value(status.url)"
```

## フロントエンドデプロイ（Firebase Hosting）
```bash
cd frontend
npm run build
firebase deploy --only hosting
echo "デプロイ完了: https://$PROJECT_ID.web.app"
```

## ロールバック手順
```bash
# 直前のリビジョンに戻す
gcloud run services update-traffic $APP_NAME-api \
  --to-revisions=PREV=100 \
  --region asia-northeast1
```

## デプロイ後確認
```bash
# ヘルスチェック
curl https://$(gcloud run services describe $APP_NAME-api \
  --region asia-northeast1 \
  --format="value(status.url)")/health

# Cloud Logging でエラー確認（直近5分）
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=20 \
  --freshness=5m
```
