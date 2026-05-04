"""
profile モジュールのルーター。

主アプリ（backend/main.py）から `module_loader.load_modules()` 経由で読み込まれる。
ルーティングのプレフィックスは module.toml で指定（既定: /api/v1/profile）。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from google.cloud import firestore

# main.py の require_db / verify_token を再利用する。
# 主アプリの内部 API への依存はモジュールの規約で許容（同一プロセス内なので）。
from main import require_db
from middleware.auth import get_current_user_id, verify_token

from .models import DisplayNameUpdate

router = APIRouter()


@router.get("")
async def get_profile(token: dict = Depends(verify_token)):
    client = require_db()
    user_id = get_current_user_id(token)
    doc = await client.collection("users").document(user_id).get()
    if not doc.exists:
        user_data = {
            "uid": user_id,
            "email": token.get("email"),
            "display_name": token.get("name"),
            "photo_url": token.get("picture"),
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        await client.collection("users").document(user_id).set(user_data)
        return user_data
    return doc.to_dict()


@router.put("")
async def update_profile(
    body: DisplayNameUpdate,
    token: dict = Depends(verify_token),
):
    client = require_db()
    user_id = get_current_user_id(token)
    doc_ref = client.collection("users").document(user_id)
    await doc_ref.update(
        {
            "display_name": body.display_name,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
    )
    snapshot = await doc_ref.get()
    return snapshot.to_dict()
