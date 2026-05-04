"""
プロジェクトルートの pytest 共通フィクスチャ。

backend/ と modules/*/backend/tests/ の両方からこのファイルが参照される
（`testpaths = backend/tests modules` が pytest.ini に記載されているため）。
"""
from __future__ import annotations

from pathlib import Path
from typing import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# `pythonpath = backend` で sys.path に backend/ が入っているので、main などが直接 import できる。
# モジュール側のテストもここで定義された fixture を共有する。

ROOT = Path(__file__).resolve().parent
MODULES_ROOT = ROOT / "modules"


@pytest.fixture(autouse=True)
def _ensure_clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """テスト中は GCP プロジェクト系 env をクリアして Firestore 無効状態で起動する。"""
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.delenv("PROJECT_ID", raising=False)


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """
    lifespan も含めて起動する FastAPI 用テストクライアント。
    lifespan が走ることで modules/*/ の load_modules も実行される。
    """
    from main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        async with app.router.lifespan_context(app):
            yield ac


@pytest.fixture
def fake_token() -> dict:
    """verify_token をオーバーライドして返すダミートークン。"""
    return {
        "uid": "test-user-uid",
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/avatar.png",
    }


@pytest.fixture
def override_verify_token(fake_token: dict):
    """
    使用例:
        async def test_x(client, override_verify_token):
            override_verify_token()
            r = await client.get("/api/v1/x", headers={"Authorization": "Bearer x"})
    """
    from main import app
    from middleware.auth import verify_token

    def _apply(token: dict | None = None) -> None:
        app.dependency_overrides[verify_token] = lambda: token or fake_token

    yield _apply
    app.dependency_overrides.pop(verify_token, None)


@pytest.fixture
def mock_firestore_db(client, monkeypatch):
    """
    Firestore の AsyncClient を MagicMock で差し替える。

    `db.collection("users").document(uid).update(...)` / `.get()` の async チェーンを再現。
    `main.db` を monkeypatch するので、`require_db()` 経由の呼び出しにも透明に作用する。

    `client` を引数に取ることで lifespan 完了後に上書き順序を保証する。
    yield されるのは update / get / set の AsyncMock を持つ doc_ref。
    """
    from unittest.mock import AsyncMock, MagicMock

    import main

    snapshot = MagicMock()
    snapshot.exists = True
    snapshot.to_dict.return_value = {
        "uid": "test-user-uid",
        "email": "test@example.com",
        "display_name": "Updated Name",
        "photo_url": "https://example.com/avatar.png",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-05-04T00:00:00Z",
    }

    doc_ref = MagicMock()
    doc_ref.update = AsyncMock()
    doc_ref.set = AsyncMock()
    doc_ref.get = AsyncMock(return_value=snapshot)

    collection = MagicMock()
    collection.document = MagicMock(return_value=doc_ref)

    db = MagicMock()
    db.collection = MagicMock(return_value=collection)

    monkeypatch.setattr(main, "db", db)
    return doc_ref
