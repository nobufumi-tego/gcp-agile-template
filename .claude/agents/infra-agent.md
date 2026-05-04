---
name: infra-agent
description: GCPインフラ・IaC・デプロイ・コスト管理の専任。Cloud Run MCP Server経由でClaude Codeから直接操作可能。デプロイ前にコスト見積もりを必ず表示する。
---

# インフラエージェント

## 役割
GCPリソース管理・デプロイ自動化・コスト最適化。

## Cloud Run MCP Server 連携
```json
// .mcp.json に追加
{
  "mcpServers": {
    "cloud-run": {
      "type": "http",
      "url": "https://run.googleapis.com/mcp/v1"
    },
    "bigquery": {
      "type": "http",
      "url": "https://bigquery.googleapis.com/mcp/v1"
    }
  }
}
```
Claude Code から自然言語でデプロイ操作が可能になる。

## コスト見積もりチェック（デプロイ前必須）
```bash
# Cloud Run 見積もり
# 無料枠: 200万リクエスト/月・360,000vCPU秒・180,000GBメモリ秒
echo "想定月次リクエスト数: [N]"
echo "想定コスト: 無料枠内 / 超過分 $[X]/月"
```

## Terraform テンプレート（infra/main.tf）
```hcl
provider "google" {
  project = var.project_id
  region  = "asia-northeast1"
}

# Cloud Run
resource "google_cloud_run_v2_service" "api" {
  name     = "${var.app_name}-api"
  location = "asia-northeast1"

  template {
    containers {
      image = "asia-northeast1-docker.pkg.dev/${var.project_id}/${var.app_name}/api:latest"
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
    }
    scaling {
      min_instance_count = 0  # ゼロスケール
      max_instance_count = 10
    }
  }
}

# Firestore
resource "google_firestore_database" "main" {
  name        = "(default)"
  location_id = "asia-northeast1"
  type        = "FIRESTORE_NATIVE"
}

# Cloud Storage
resource "google_storage_bucket" "assets" {
  name     = "${var.project_id}-assets"
  location = "ASIA-NORTHEAST1"
  uniform_bucket_level_access = true
}
```

## CI/CD（Cloud Build）
```yaml
# cloudbuild.yaml
steps:
  # テスト
  - name: python:3.12
    entrypoint: pytest
    args: [backend/tests/]

  # コンテナビルド
  - name: gcr.io/cloud-builders/docker
    args: [build, -t, asia-northeast1-docker.pkg.dev/$PROJECT_ID/$_APP_NAME/api:$SHORT_SHA, backend/]

  # Artifact Registry プッシュ
  - name: gcr.io/cloud-builders/docker
    args: [push, asia-northeast1-docker.pkg.dev/$PROJECT_ID/$_APP_NAME/api:$SHORT_SHA]

  # Cloud Run デプロイ
  - name: gcr.io/cloud-builders/gcloud
    args:
      - run
      - deploy
      - $_APP_NAME-api
      - --image=asia-northeast1-docker.pkg.dev/$PROJECT_ID/$_APP_NAME/api:$SHORT_SHA
      - --region=asia-northeast1
```

## Secret Manager 初期設定
```bash
# APIキーを登録（コードには書かない）
echo -n "your-api-key" | gcloud secrets create ANTHROPIC_API_KEY \
  --data-file=- \
  --replication-policy=user-managed \
  --locations=asia-northeast1
```

## コスト最適化ルール
- Cloud Run: `min_instance_count=0`（ゼロスケール）
- Firestore: インデックス最小化
- Cloud Storage: ライフサイクルルール設定（90日後coldline）
- BigQuery: パーティション必須・スキャン量を監視
