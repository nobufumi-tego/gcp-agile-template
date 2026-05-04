# gcp-agile-template

[![CI](https://github.com/nobufumi-tego/gcp-agile-template/actions/workflows/ci.yml/badge.svg)](https://github.com/nobufumi-tego/gcp-agile-template/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

スマホファースト × GCP × Claude Code Agent によるアジャイル開発テンプレート。

## What's inside

- **Frontend**: SvelteKit 2 + Svelte 5 + Tailwind v4 + adapter-static (Firebase Hosting)
- **Backend**: FastAPI + Python 3.12 + uv (Cloud Run, asia-northeast1)
- **Auth**: Firebase Auth (mobile = redirect / desktop = popup)
- **Data**: Firestore + Cloud Storage + BigQuery
- **AI/ML**: Vertex AI / MediaPipe / Cloud Run MCP Server
- **CI/CD**: Cloud Build + Artifact Registry + Secret Manager

## Key features

- **TDD as default** — Red-Green-Refactor をスキル/エージェント/DoD に組み込み
- **Module system** — `modules/<name>/` に 1 機能 = backend ルーター + frontend スライス + テストを自己完結配置。`scripts/install_module.py` で外部から取り込み
- **Spec bundle system** — `specs/<name>/` に仕様書バンドル（ストーリー/ADR/プラン）を凍結保存。`scripts/install_spec.py` で外部から取り込み
- **Mobile-first guards** — 375px / LCP 2.5s / CLS 0.1 / 44px タッチターゲット を `/mobile-check` で強制
- **Cost-aware deploy** — `/deploy-gcp` でコスト見積もりを必須

## Getting started

詳しいセットアップ・規約・アーキテクチャは [CLAUDE.md](./CLAUDE.md) を参照。

```bash
# 依存インストール
cd backend && uv sync
cd frontend && npm install

# ローカル開発（ターミナル 2 枚）
cd backend && uv run uvicorn main:app --reload --port 8000
cd frontend && npm run dev

# テスト
backend/.venv/Scripts/pytest.exe          # backend + modules + scripts (25 件)
cd frontend && npm test                   # vitest (6 件)
cd frontend && npm run check              # svelte-check
```

## Use cases

個人開発の MVP、スタートアップの Pre-seed プロトタイプ、AI/ML を組み込んだスマホアプリ、PWA、エージェント駆動 TDD のショーケース、社内モジュール再利用基盤など。
詳細は CLAUDE.md の「Use cases」相当のセクション、または ADR / specs を参照。

## License

[MIT](./LICENSE)
