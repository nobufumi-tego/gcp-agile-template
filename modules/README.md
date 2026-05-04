# modules/ — フィーチャーモジュール置き場

このディレクトリは、検証済みの機能スライス（backend ルーター + frontend ルート/コンポーネント + テスト）を**自己完結した単位**で配置するためのものです。

## 規約

```
modules/<name>/
├── module.toml          # マニフェスト（必須）
├── README.md            # モジュール説明
├── backend/             # 必須でない（fronted-only モジュールも可）
│   ├── __init__.py
│   ├── router.py        # 必須：APIRouter インスタンスを `router` 名でエクスポート
│   ├── models.py        # 任意
│   ├── services.py      # 任意
│   └── tests/           # pytest が自動で拾う
│       ├── __init__.py
│       └── test_*.py
└── frontend/            # 任意
    ├── lib/             # → frontend/src/lib/modules/<name>/ に sync される
    ├── routes/          # → frontend/src/routes/<name>/ に sync される
    └── tests/           # → frontend/src/lib/modules/<name>/ 配下のテストとして sync
```

## マニフェスト形式

`module.toml`:
```toml
[module]
name = "profile"
version = "0.1.0"
description = "ユーザープロフィール管理"

[backend]
# OpenAPI / FastAPI ルーターのプレフィックス。省略時は /api/v1/<name>
prefix = "/api/v1/profile"
# 追加で必要な Python 依存（backend/pyproject.toml にすでに無いもの）
deps = []

[frontend]
# 追加で必要な npm 依存（frontend/package.json にすでに無いもの）
deps = []
# ルートの一覧（人間向けのドキュメント。実際のコピーは frontend/routes/ ディレクトリ全体）
routes = ["profile/edit"]
```

## ロード順序

backend は `backend/main.py` の `lifespan` 起動時に `module_loader.load_modules()` が
`modules/*/` をアルファベット順に走査し、`module.toml` の `backend.prefix` で
`app.include_router(...)` する。

frontend は静的なディレクトリコピーで、`npm run modules:sync` を `prebuild` に組み込んでいる。

## 取り込み方法

```bash
# ローカルパスから
python scripts/install_module.py /path/to/external/module

# Git URL から
python scripts/install_module.py https://github.com/user/repo.git

# .zip から
python scripts/install_module.py /path/to/module.zip
```

## TDD との関係

各モジュールの `tests/` は親プロジェクトの `pytest` / `vitest` から透過的に走る。
モジュール開発者は **モジュール内で TDD を完結**させる。
