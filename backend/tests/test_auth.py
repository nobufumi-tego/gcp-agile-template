"""
認証ガードのテスト。
- Authorization ヘッダ無し → 403
- 不正なトークン → 401
- 認証通過後に Firestore 未初期化なら 503（require_db）
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_protected_endpoint_rejects_missing_authorization_header(
    client: AsyncClient,
) -> None:
    res = await client.get("/api/v1/profile")
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_protected_endpoint_rejects_invalid_token(client: AsyncClient) -> None:
    res = await client.get(
        "/api/v1/profile", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_authorized_request_returns_503_when_firestore_unset(
    client: AsyncClient, override_verify_token
) -> None:
    """env 未設定で Firestore が None のとき、認証通過後でも 503 を返す。"""
    override_verify_token()
    res = await client.get(
        "/api/v1/profile", headers={"Authorization": "Bearer ignored"}
    )
    assert res.status_code == 503
    assert "Firestore" in res.json()["detail"]
