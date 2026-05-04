# backend/middleware/auth.py
# Firebase IDトークンの検証（Cloud Run バックエンド側）
from functools import wraps
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import os

# Firebase Admin SDK 初期化（Cloud Runでは Application Default Credentials を使用）
if not firebase_admin._apps:
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        cred = credentials.ApplicationDefault()
    else:
        cred = credentials.ApplicationDefault()  # Cloud Runは自動認証
    firebase_admin.initialize_app(cred)

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Firebase IDトークンを検証して、デコードされたトークン情報を返す。
    FastAPIの依存性注入で使用する。

    使用例:
        @app.get("/api/v1/profile")
        async def get_profile(token: dict = Depends(verify_token)):
            user_id = token["uid"]
    """
    token = credentials.credentials
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="トークンの有効期限切れ")
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="無効なトークン")
    except Exception:
        raise HTTPException(status_code=401, detail="認証エラー")


def get_current_user_id(token: dict) -> str:
    """トークンからユーザーIDを取得するヘルパー"""
    return token["uid"]


def get_current_user_email(token: dict) -> str | None:
    """トークンからメールアドレスを取得するヘルパー"""
    return token.get("email")
