.PHONY: help setup install dev dev-backend dev-frontend test test-backend test-frontend deploy-backend deploy-frontend deploy

PROJECT_ID ?= your-project-id
APP_NAME   ?= your-app-name
REGION     ?= asia-northeast1

# 注意: Windows ネイティブ cmd/PowerShell には make が無い。
# WSL2 または Git Bash で利用するか、各ターゲットに記載のコマンドを直接実行する。

help:
	@echo "targets:"
	@echo "  make install         - backend (uv sync) + frontend (npm install)"
	@echo "  make dev-backend     - uvicorn :8000 を前面起動（Ctrl-C で停止）"
	@echo "  make dev-frontend    - vite :5173 を前面起動"
	@echo "  make test            - backend + frontend のテストを順次実行"
	@echo "  make deploy-backend  - Cloud Run へデプロイ"
	@echo "  make deploy-frontend - Firebase Hosting へデプロイ"
	@echo "  make deploy          - test → backend → frontend を順次"
	@echo "  make setup           - GCP API を一括有効化"
	@echo ""
	@echo "ローカル開発はターミナル 2 枚で 'make dev-backend' と 'make dev-frontend' を実行する。"

# 依存インストール
install:
	cd backend && uv sync
	cd frontend && npm install

# バックエンド単独起動（フォアグラウンド）
dev-backend:
	cd backend && uv run uvicorn main:app --reload --port 8000

# フロントエンド単独起動（フォアグラウンド）
dev-frontend:
	cd frontend && npm run dev

# 後方互換: dev は backend を起動（フロントは別ターミナルで dev-frontend）
dev: dev-backend

# テスト
test: test-backend test-frontend

test-backend:
	uv --directory backend run pytest -c $(CURDIR)/pytest.ini --tb=short $(CURDIR)/backend/tests $(CURDIR)/modules

test-frontend:
	cd frontend && npm test

# バックエンドデプロイ（Cloud Run）
deploy-backend:
	gcloud run deploy $(APP_NAME)-api \
		--source backend/ \
		--region $(REGION) \
		--min-instances 0 \
		--max-instances 10 \
		--memory 512Mi \
		--project $(PROJECT_ID)

# フロントエンドデプロイ（Firebase Hosting）
deploy-frontend:
	cd frontend && npm run build
	firebase deploy --only hosting

# 全体デプロイ
deploy: test deploy-backend deploy-frontend
	@echo "All deployed!"

# GCP初期セットアップ
setup:
	gcloud config set project $(PROJECT_ID)
	gcloud services enable \
		run.googleapis.com \
		firestore.googleapis.com \
		storage.googleapis.com \
		bigquery.googleapis.com \
		pubsub.googleapis.com \
		secretmanager.googleapis.com \
		cloudbuild.googleapis.com \
		artifactregistry.googleapis.com
	@echo "GCP services enabled"
