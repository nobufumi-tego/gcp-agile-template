"""
FastAPI on Cloud Run — メインエントリポイント
Firebase Auth + Firestore + GCPファースト
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore

from module_loader import load_modules

MODULES_DIR = Path(__file__).resolve().parent.parent / "modules"

logger = logging.getLogger("uvicorn.error")

# GCPクライアント（起動時に1回だけ初期化）
db: firestore.AsyncClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")
    if project_id:
        db = firestore.AsyncClient(project=project_id)
        logger.info(f"Firestore client initialized for project={project_id}")
    else:
        # ローカル開発で GCP 未設定でも起動できるようにする。
        # Firestore に依存するエンドポイントは 503 を返す。
        db = None
        logger.warning(
            "GOOGLE_CLOUD_PROJECT / PROJECT_ID 未設定: Firestore は無効化されます。"
            " /health のみ動作します。"
        )

    loaded = load_modules(app, MODULES_DIR)
    if loaded:
        logger.info(f"loaded modules: {loaded}")

    yield


app = FastAPI(title=os.getenv("APP_NAME", "app") + " API", lifespan=lifespan)

# CORS（Firebase Hostingドメインを許可）
_project_id = os.getenv("PROJECT_ID", "")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://{_project_id}.web.app",
        f"https://{_project_id}.firebaseapp.com",
        "http://localhost:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_db() -> firestore.AsyncClient:
    """Firestore が初期化されていない場合は 503 を返す。"""
    from fastapi import HTTPException

    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Firestore 未初期化（GOOGLE_CLOUD_PROJECT 環境変数を設定してください）",
        )
    return db


# ヘルスチェック（認証不要・Cloud Run必須）
@app.get("/health")
async def health():
    return {"status": "ok", "firestore": db is not None}


# 注:
# 機能スライスは modules/<name>/backend/router.py に置くと、lifespan で自動 include される。
# 主アプリ直下にエンドポイントを足す場合のみ、ここで @app.get / @app.put を書く。
