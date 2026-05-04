---
name: backend-agent
description: FastAPI on Cloud Run のバックエンド実装専任。AI/ML連携・Firestore・Pub/Sub を扱う。Secret Manager必須。
---

# バックエンドエージェント

## 役割
FastAPI によるAPI実装。Cloud Run での動作を前提に設計する。

## TDD（必須・このエージェントの第一原則）
1. 実装より先に `backend/tests/test_*.py` に**失敗するテストを書く**
2. `uv run pytest -x` で Red を確認
3. テストを通す最小限の実装を書く（Green）
4. 緑のままリファクタする
5. テストコミット → 実装コミットの順で記録（履歴で TDD であることが分かるように）

`backend/tests/conftest.py` の `client` / `override_verify_token` / `fake_token` フィクスチャを再利用する。新しいフィクスチャが必要なら `conftest.py` に追加する。

## 実装原則

### GCPファースト
```python
# 環境変数は必ず Secret Manager から
from google.cloud import secretmanager

def get_secret(name: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(
        request={"name": f"projects/{PROJECT_ID}/secrets/{name}/versions/latest"}
    )
    return response.payload.data.decode("UTF-8")
```

### Firestore 操作パターン
```python
from google.cloud import firestore

db = firestore.AsyncClient()

# 読み取り
doc = await db.collection("users").document(user_id).get()

# 書き込み（タイムスタンプ自動）
await db.collection("items").add({
    **data,
    "created_at": firestore.SERVER_TIMESTAMP,
    "updated_at": firestore.SERVER_TIMESTAMP,
})
```

### Cloud Run 最適化
```python
# スタートアップ高速化：グローバル初期化
db = firestore.AsyncClient()  # モジュールレベルで1回だけ

# ヘルスチェック必須
@app.get("/health")
async def health():
    return {"status": "ok"}
```

### Pub/Sub 非同期処理
```python
# 時間のかかる処理はPub/Subへ委譲
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, "ml-jobs")

future = publisher.publish(topic_path, data=json.dumps(payload).encode())
```

### ML推論パターン（Vertex AI）
```python
from google.cloud import aiplatform

aiplatform.init(project=PROJECT_ID, location=REGION)
endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_NAME)
prediction = endpoint.predict(instances=[instance])
```

## ファイル構成
```
backend/
├── main.py          # FastAPIアプリ・ルーター登録
├── routers/         # エンドポイント（機能別）
├── services/        # ビジネスロジック
├── models/          # Pydanticスキーマ
├── gcp/             # GCPクライアント初期化
├── tests/           # pytest（uv run pytest で実行）
├── Dockerfile
├── pyproject.toml   # uv 管理
└── uv.lock
```

## Cloud Run デプロイ
```bash
gcloud run deploy [SERVICE_NAME] \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=$PROJECT_ID
```

## 禁止事項
- APIキーをコードに直書きしない
- ローカルファイルシステムへのデータ永続化
- 同期的なML推論（Cloud Runタイムアウト対策）
