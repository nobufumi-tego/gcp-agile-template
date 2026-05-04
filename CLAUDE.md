# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# [PROJECT_NAME] — スマホファースト × GCPファースト

## プロジェクト概要
<!-- 一言：何を・誰に・なぜ -->

## Repository State（重要：未来の Claude へ）

スモークテストで以下を確認済み：
- backend は **uv 管理**（`pyproject.toml` + `uv.lock`）。`uv sync` で 3.12.x の Python と全依存が入る。
- frontend は **Svelte 5 + SvelteKit 2 + Tailwind v4 + adapter-static**。`npm install` → `npm run check` がエラー 0 件で通り、`npm run build` で `frontend/build/` に静的ファイル出力可能。
- backend は `GOOGLE_CLOUD_PROJECT` / `PROJECT_ID` 未設定でも起動可能（`/health` は 200・Firestore 依存エンドポイントは 503）。
- **テスト雛形済み**：backend `pytest`（**18 件パス**：core 4 + module_loader 8 + profile module 6・httpx.AsyncClient ベース）、frontend `vitest`（6 件パス・@testing-library/svelte + SvelteKit ランタイムモック）。
- **モジュールシステム稼働中**：`modules/profile/` がリファレンス実装、`backend/module_loader.py` が lifespan で自動ロード、`scripts/sync-modules.mjs` がフロントを同期、`scripts/install_module.py` で外部から取り込み可能。

未整備項目：
- `frontend/static/icon-192.png` / `icon-512.png` は未配置（manifest.json は参照のみ。実プロジェクトで PNG を配置すること）。
- `Makefile` の `PROJECT_ID` / `APP_NAME`、本ファイルの「GCPプロジェクト設定」、`frontend/.env.example` / `backend/.env.example` の値は**未設定プレースホルダ**。
- `firebase` CLI は別途 `npm install -g firebase-tools` が必要。
- ADR は `docs/adr/ADR-001-template.md` のテンプレートのみ、`docs/sprints/backlog.md` も雛形のみ。

## モジュールシステム（外部から機能を取り込む）

このリポジトリはフィーチャーモジュール方式で、検証済みの機能スライスを `modules/<name>/` に
配置します。1 機能 = backend ルーター + frontend コンポーネント/ルート + テスト が同居します。

### ディレクトリ規約
```
modules/<name>/
├── module.toml          # マニフェスト（[module].name は必須）
├── README.md
├── backend/
│   ├── __init__.py
│   ├── router.py        # 必須: APIRouter を `router` 名でエクスポート
│   ├── models.py        # 任意（相対 import 可: from .models import X）
│   └── tests/
│       └── test_*.py    # ルートの conftest.py の fixture（client / mock_firestore_db）を共有
└── frontend/
    ├── lib/             # → frontend/src/lib/modules/<name>/ に同期される
    └── routes/          # → frontend/src/routes/<route>/ に同期される
```

### ロードの仕組み
- **backend**: `backend/main.py` の lifespan で `module_loader.load_modules(app, modules/)` がアルファベット順に走査し、`router.py` を動的 import → `app.include_router(router, prefix=...)`。プレフィックス既定値は `/api/v1/<name>`、`module.toml` の `[backend].prefix` で上書き可。1 つが壊れても他はロードされる。
- **frontend**: `npm run modules:sync` が `scripts/sync-modules.mjs` を実行し、`modules/*/frontend/lib` を `frontend/src/lib/modules/<name>/` に、`modules/*/frontend/routes/*` を `frontend/src/routes/*` にコピー。同期先は **`.gitignore` 対象**で、各ファイル先頭に `AUTO-GENERATED` マーカーが入る。`dev` / `build` / `check` / `test` の前段で自動実行される。

### 取り込みコマンド
```bash
# ローカルパス
python scripts/install_module.py /path/to/external/module

# Git URL（branch 指定・モノレポの subdir 指定可）
python scripts/install_module.py https://github.com/user/repo.git --ref main --subdir packages/billing

# .zip
python scripts/install_module.py ./module.zip

# 既存上書き
python scripts/install_module.py <source> --force
```

### サンプルモジュール
`modules/profile/` がリファレンス実装。`/api/v1/profile` の GET / PUT を提供し、Pydantic バリデーション + Firestore 更新 + 認証ガード + テスト 6 件を含む。**新しいモジュールを書くときはこれをコピー元にする**。

## 仕様書の取り込みシステム（specs/）

外部から仕様書バンドル（ユーザーストーリー・受入条件・ADR・スプリント計画書）を取り込むための仕組み。コードのモジュールシステムと対称的に動作。

### バンドル構造
```
specs/<name>/
├── spec.toml             # マニフェスト（[spec].name は必須）
├── README.md             # バンドルの説明
└── docs/                 # プロジェクトの docs/ にミラーされる構造
    ├── adr/ADR-NNN-*.md
    └── sprints/sprint-N/specs/<story>.md
```

### 役割の分担
- `specs/<name>/` — 取り込み時の**凍結アーカイブ**（編集しない・再取り込みで上書きされる）
- `docs/...` — **実際の作業領域**（spec-agent / 人間が編集する）

`scripts/install_spec.py` は両方に配置する：(1) 元バンドル全体を `specs/<name>/` に凍結、(2) `docs/**` 部分を プロジェクトの `docs/**` にマージ。

### 取り込みコマンド
```bash
# ローカルパス
python scripts/install_spec.py /path/to/bundle

# Git URL（branch・モノレポ subdir 指定可）
python scripts/install_spec.py https://github.com/po/specs.git --ref main --subdir bundles/onboarding

# .zip
python scripts/install_spec.py ./onboarding-spec.zip

# 既存 docs/ ファイルを上書き
python scripts/install_spec.py <source> --force
```

### コンフリクト方針
- 同一内容なら静かにスキップ（idempotent）
- 内容が異なる既存ファイルがあると **exit 2** で警告し、コピーをスキップ
- `--force` で上書き
- `specs/<name>/` 自体は --force なしでも上書きされる（凍結アーカイブの再取り込み）

### サンプルバンドル
`specs/user-onboarding-mvp/` がリファレンス。Google ログイン仕様 + 表示名編集仕様 + ADR-002 の 3 ファイルが入っており、`docs/adr/ADR-002-auth-split.md` 等にコピー済み。**新規バンドルを作るときの構造の参考にする**。

## Architecture（複数ファイルを読まないと分からない big picture）

### 認証フロー（フロント → バック）
1. `frontend/src/lib/firebase/client.ts:signInWithGoogle` がブラウザ UA を見て分岐：
   - スマホ → `signInWithRedirect`（ポップアップは iOS Safari で動作不安定なため）
   - PC → `signInWithPopup`
   - リダイレクト後の結果は `handleRedirectResult` で取得。
2. `frontend/src/lib/stores/auth.ts:initAuth`（`+layout.svelte` の `onMount` から呼ばれる）が `onAuthStateChanged` で `user` ストアを更新し、ID トークンを `idToken` ストアに保存。**55 分ごとに `getIdToken(true)` で自動リフレッシュ**。
3. `frontend/src/lib/firebase/api.ts:authFetch` がすべての API 呼び出しの基底。`idToken` を `Authorization: Bearer ...` で付与し、`VITE_API_BASE_URL`（Cloud Run URL）に投げる。
4. `backend/middleware/auth.py:verify_token` が FastAPI の `Depends` で受け、Firebase Admin SDK の `verify_id_token` で検証。Cloud Run では Application Default Credentials を使う（`GOOGLE_APPLICATION_CREDENTIALS` 不要）。
5. `backend/main.py:get_profile` のように、ハンドラは `token: dict = Depends(verify_token)` を受け取り → `require_db()` で Firestore クライアント取得（未初期化なら 503）→ `get_current_user_id(token)` → Firestore `users/{uid}` を read/upsert。

新規エンドポイントを追加するときも必ず `Depends(verify_token)` を経由させ、Firestore を使うなら `require_db()` でガードすること。

### Svelte 5 規約（重要）
このリポジトリは **Svelte 5 構文**で書く。Svelte 4 構文は使わない：
- ✅ `let foo = $state(0)` / `let { children } = $props()`
- ✅ `$derived(...)` / `$effect(() => {...})`
- ✅ `{@render children()}`（旧 `<slot />`）
- ✅ `onclick={fn}`（旧 `on:click={fn}`）
- ✅ `import { page } from '$app/state'`（旧 `$app/stores` の `$page`）

### ポート規約
| 環境 | ポート | 設定箇所 |
|---|---|---|
| ローカル uvicorn `--reload` | **8000** | `Makefile`, CLAUDE.md |
| Dockerfile / Cloud Run | **8080** | `backend/Dockerfile` |
| SvelteKit dev | 5173 | Vite デフォルト（CORS 許可済み） |

`main.py` の CORS allowlist は `PROJECT_ID` 環境変数から `https://{PROJECT_ID}.web.app` / `.firebaseapp.com` / `http://localhost:5173` を許可する。

### Firestore 起動パターン
`backend/main.py` の `lifespan` は `GOOGLE_CLOUD_PROJECT` / `PROJECT_ID` を見て `firestore.AsyncClient(project=...)` を 1 回だけ初期化する。env 未設定時は `db = None` のまま起動し、Firestore 依存エンドポイントは `require_db()` で 503 を返す（`/health` は 200 のまま）。

### スマホ専用レイアウトシェル
`frontend/src/routes/+layout.svelte` が以下を強制：
- `max-width: 430px`（PC でも中央 430px に固定 = スマホ UI 前提）
- `min-height: 100dvh`（dynamic viewport で iOS のアドレスバー伸縮に追従）
- `padding-bottom: calc(64px + env(safe-area-inset-bottom))`（ボトムナビ + ノッチ対応）
- `protectedRoutes = ['/home', '/profile', '/settings']` に未認証アクセスすると `/login` へ強制リダイレクト

新ページを protected にしたい場合は `+layout.svelte` の配列に追加。

### ビルド・デプロイ経路
- frontend: `vite build` → `@sveltejs/adapter-static` が `frontend/build/` に SPA 出力（`fallback: 'index.html'`）→ `firebase.json` の `public: "frontend/build"` で Hosting にアップロード。
- backend: `gcloud run deploy --source backend/` で Dockerfile（uv ベース）をビルド → Artifact Registry 経由で Cloud Run。

## 技術スタック

### フロントエンド
- **Svelte 5** + **SvelteKit 2**（`adapter-static` で SPA 化）
- **Tailwind CSS v4**（Vite plugin・`src/app.css` で `@import "tailwindcss"`）
- **Vitest**（単体）+ **Playwright**（E2E / mobile-check）
- デプロイ先：Firebase Hosting（CDN・無料枠）

### バックエンド
- **Python 3.12** + **uv**（`pyproject.toml` + `uv.lock`）
- FastAPI 0.115（非同期・型安全）
- Cloud Run（コンテナ・ゼロスケール・asia-northeast1）
- Pub/Sub（非同期イベント処理）

### データ
- Firestore（NoSQL・リアルタイム・スマホ同期）
- Cloud Storage（ファイル・動画・モデル）
- BigQuery（分析・ML学習データ蓄積）

### AI / ML
- Vertex AI（モデル管理・推論）
- MediaPipe（オンデバイスML）
- Cloud Run MCP Server（Claude Codeからデプロイ直結）

### DevOps
- Cloud Build（CI/CD）
- Artifact Registry（コンテナ管理）
- Secret Manager（APIキー管理）

## GCPプロジェクト設定
```
PROJECT_ID=
APP_NAME=
REGION=asia-northeast1
```
`Makefile`・本ファイル・`backend/.env`・`frontend/.env.local` の 4 箇所を埋めること。

## コマンド集

### 初期セットアップ（プロジェクト ID 設定後に 1 回）
```bash
make setup        # gcloud で必要な GCP API を一括有効化
make install      # backend (uv sync) + frontend (npm install)
```
`make` が無い環境（Windows ネイティブ等）では下記の生コマンドを直接叩く。

### ローカル開発（**ターミナル 2 枚**）
```bash
# ターミナル 1: バックエンド（:8000）
cd backend && uv run uvicorn main:app --reload --port 8000

# ターミナル 2: フロントエンド（:5173）
cd frontend && npm run dev
```
make が使える環境なら `make dev-backend` / `make dev-frontend`。

### テスト（TDD 中心の開発フロー）

**重要**: pytest はプロジェクトルートから実行する（`pytest.ini` で `testpaths = backend/tests modules` を集中管理しているため）。`backend/.venv/Scripts/pytest.exe` を直接呼ぶか、`make test-backend` を使う。

```bash
# バックエンド全件（backend/tests + modules/*/backend/tests を一括収集）
backend/.venv/Scripts/pytest.exe --tb=short
backend/.venv/Scripts/pytest.exe -x --ff           # 失敗最優先・即停止（TDD ループ向け）

# 特定モジュールだけ
backend/.venv/Scripts/pytest.exe modules/profile

# 単体テスト指定
backend/.venv/Scripts/pytest.exe modules/profile/backend/tests/test_router.py::test_put_profile_rejects_empty_display_name -v

# Make 経由（POSIX シェル環境）
make test-backend

# フロントエンド単体（Vitest・watch がデフォルト・modules:sync が前段で走る）
cd frontend && npm test                       # 1 回実行
cd frontend && npm run test:watch             # ファイル変更で再実行

# フロントエンド型チェック
cd frontend && npm run check

# モバイルチェック（Playwright・mobile-chrome プロジェクト）
cd frontend && npm run mobile-check
```

### デプロイ
```bash
make deploy-backend       # gcloud run deploy --source backend/
make deploy-frontend      # npm run build → firebase deploy --only hosting
make deploy               # test → backend → frontend を順次
```

## Claude Code 環境（このリポジトリ固有）

### MCP サーバー（`.mcp.json`）
HTTP 型で 3 つ有効：
- **cloud-run** — Cloud Run のデプロイ・サービス管理を自然言語で
- **bigquery** — クエリ・テーブル操作
- **firestore** — ドキュメント read/write

### permissions（`.claude/settings.json`）
- **allow**: `gcloud:*`, `firebase:*`, `uv:*`, `uvx:*`, `pytest:*`, `npm:*`, `npx:*`, `git:*`
- **deny**: `gcloud secrets:*`（Claude は Secret Manager の値を直接読み書きできない。シークレット登録は人間が手動で行う）、`rm -rf /*`

### フック（クロスプラットフォーム・Python ベース）
- `PostToolUse` (Edit|Write): 編集ファイル名と時刻を `.claude/session.log` に追記
- `Stop`: セッション境界を `.claude/session.log` に記録

旧 bash 構文（`$(date +%H:%M)` / `basename`）は Windows で動かなかったため、Python ワンライナーに置換済み。

### 実験フラグ
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` が有効。`/sprint-planning` で agent team が起動できる前提。

## スプリント開発ルール

### エージェント構成（`.claude/agents/`）
- orchestrator  : タスク分解・進捗管理・ブロッカー解消（コードは書かない）
- spec-agent    : ユーザーストーリー・受入条件の生成
- backend-agent : FastAPI・Cloud Run実装
- mobile-agent  : スマホUX・PWA・レスポンシブ実装
- infra-agent   : GCPリソース・IaC・デプロイ管理

> 注: 旧版 CLAUDE.md では architect / test-agent / review-agent も列挙されていたが、現状 `.claude/agents/` には未配置。必要になったら作成すること。

### TDD ルール（必須・最優先）

このプロジェクトは **TDD（Red-Green-Refactor）が基本ワークフロー** です。

1. **Red** — まず失敗するテストを書く。テストは契約（API シグネチャ・期待される挙動）を定義する。
2. **Green** — そのテストを通す**最小限の実装**を書く。
3. **Refactor** — テストが緑のまま、実装をきれいにする。

具体ルール：
- 実装コミットの**前**にテストコミットを置く（`git log` で順序が確認できるようにする）。
- バックエンド：`backend/tests/test_*.py` に `pytest` + `httpx.AsyncClient` でテストを書く。`backend/tests/conftest.py` の `client` / `override_verify_token` フィクスチャを再利用する。
- フロントエンド：`*.test.ts` を**テスト対象と同じディレクトリに同居**させる。`vitest` + `@testing-library/svelte`。SvelteKit ランタイム依存（`$app/state` など）は `frontend/vitest.setup.ts` で既にモック済み。
- E2E ＆スマホチェックは `cd frontend && npm run mobile-check`（Playwright）。
- `/plan-feature` の計画書では「テスト計画」を**最優先項目**として書く。実装ファイルを変更するより前に、書くべきテストを列挙する。
- 例外：純粋なドキュメント・設定・型のリネームのみのコミットはテスト不要（PR 説明で「ノーテストで OK な理由」を明記）。

### スマホファーストルール（必須）
- モバイル幅（375px）で先に実装・確認
- タッチターゲット最小44×44px
- LCP 2.5秒以内・CLS 0.1以下
- オフライン対応（Service Worker）
- /mobile-check を実装ごとに実行

### GCPファーストルール（必須）
- ローカルDBは使わない → Firestore / BigQuery
- 環境変数は Secret Manager から取得（`gcloud secrets:*` は deny されているので登録は人間に依頼）
- ログは Cloud Logging に統一
- コスト確認：/deploy-gcp 実行前に見積もり表示

### スプリントサイクル（1週間）

#### 計画フェーズ（/plan モード：コードを書かない・人間承認必須）
```
/plan-architecture  → 大きな設計変更時のみ。ADR作成。人間承認。
  ↓
/plan-sprint        → バックログ全体計画・Wave設計・コスト見積もり。人間承認。
  ↓
/plan-feature × N   → ストーリーごとの詳細計画・影響ファイル・API契約。人間承認。
```

#### 実装フェーズ（承認後に開始）
```
/sprint-planning    → エージェント起動・worktree作成
実装（Wave並列）    → mobile / backend / infra が独立作業
/daily-standup      → 毎日の進捗確認・スマホ品質・コスト確認
/mobile-check       → LCP・CLS・PWA・375px確認
/deploy-gcp         → Cloud Run・Firebase Hosting デプロイ
```

#### 振り返りフェーズ
```
/sprint-review      → DoD確認・CLAUDE.md更新・レトロ記録
```

### /plan モードの原則
- 計画フェーズでは**コードを一行も書かない**
- 計画書を人間が承認してから実装開始
- バグ修正・軽微な変更は /plan-feature を省略可
- 計画変更は計画書を先に修正してから実装に反映

### Definition of Done
- [ ] /plan-feature の計画書が承認済み（テスト計画を含む）
- [ ] **テストを実装より先に書いた**（コミット順序で確認可能）
- [ ] 新機能には新テストが追加されている（実装のみのコミットは差し戻し）
- [ ] backend `uv run pytest` / frontend `npm test` が全件グリーン
- [ ] フロントエンド変更は `npm run check` で型エラー 0
- [ ] /mobile-check 通過（375px・LCP・タッチ・PWA）
- [ ] review-agent 承認
- [ ] Cloud Run・Firebase Hosting にデプロイ確認
- [ ] 受入条件すべて満たす
- [ ] CLAUDE.md に知見を追記
