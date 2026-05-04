# profile モジュール

ユーザープロフィール（Firestore `users/{uid}`）の取得と表示名更新を提供する。

## エンドポイント

| Method | Path | 説明 |
|---|---|---|
| `GET` | `/api/v1/profile/` | 自分のプロフィールを返す（無ければ作成） |
| `PUT` | `/api/v1/profile/` | display_name を更新（1-50 文字、トリム済み） |

すべて `Authorization: Bearer <Firebase-IDトークン>` 必須。

## 開発

```bash
# モジュール単独でテスト
cd backend && uv run pytest ../modules/profile/backend/tests/
```

## TDD

`backend/tests/test_router.py` がすべての契約を網羅している。
- `display_name` 検証: 422
- 認証: 403/401
- Firestore 未設定: 503
- ハッピーパス: 200 + Firestore.update 検証
