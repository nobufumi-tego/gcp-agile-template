"""
profile モジュールのルーターテスト。
親プロジェクトの conftest.py（root）から client / override_verify_token /
mock_firestore_db フィクスチャを共有する。

エンドポイントは /api/v1/profile （module.toml の prefix + ルート定義）。
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_put_profile_requires_auth_header(client: AsyncClient) -> None:
    res = await client.put("/api/v1/profile", json={"display_name": "Alice"})
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_put_profile_rejects_empty_display_name(
    client: AsyncClient, override_verify_token
) -> None:
    override_verify_token()
    res = await client.put(
        "/api/v1/profile",
        json={"display_name": ""},
        headers={"Authorization": "Bearer x"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_put_profile_rejects_whitespace_only_display_name(
    client: AsyncClient, override_verify_token
) -> None:
    override_verify_token()
    res = await client.put(
        "/api/v1/profile",
        json={"display_name": "   "},
        headers={"Authorization": "Bearer x"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_put_profile_rejects_too_long_display_name(
    client: AsyncClient, override_verify_token
) -> None:
    override_verify_token()
    res = await client.put(
        "/api/v1/profile",
        json={"display_name": "a" * 51},
        headers={"Authorization": "Bearer x"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_put_profile_returns_503_when_firestore_unset(
    client: AsyncClient, override_verify_token
) -> None:
    override_verify_token()
    res = await client.put(
        "/api/v1/profile",
        json={"display_name": "Alice"},
        headers={"Authorization": "Bearer x"},
    )
    assert res.status_code == 503


@pytest.mark.asyncio
async def test_put_profile_updates_firestore_and_returns_user(
    client: AsyncClient, override_verify_token, mock_firestore_db
) -> None:
    override_verify_token()
    res = await client.put(
        "/api/v1/profile",
        json={"display_name": "  Updated Name  "},
        headers={"Authorization": "Bearer x"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["display_name"] == "Updated Name"
    assert body["uid"] == "test-user-uid"

    mock_firestore_db.update.assert_awaited_once()
    call_arg = mock_firestore_db.update.await_args.args[0]
    assert call_arg["display_name"] == "Updated Name"
    assert "updated_at" in call_arg
