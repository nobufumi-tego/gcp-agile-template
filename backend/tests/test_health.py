"""
/health エンドポイントの最小テスト。
TDD のお手本：契約（status, firestore フラグ）が満たされることのみ検証する。
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok_without_gcp_env(client: AsyncClient) -> None:
    res = await client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body == {"status": "ok", "firestore": False}
