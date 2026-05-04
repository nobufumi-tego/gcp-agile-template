# /plan-feature: 表示名の更新

## 1. 対象ストーリー
- Story: User updates display_name
- スプリントゴール: プロフィール編集 MVP
- ユーザー文脈: スマホで片手・移動中に自分の表示名を変更できる

## 2. テスト計画（最優先・実装より先に書く）

`backend/tests/test_profile_update.py`:
- `test_put_profile_requires_auth_header` → ヘッダ無し: 403
- `test_put_profile_rejects_empty_display_name` → `""`: 422
- `test_put_profile_rejects_whitespace_only_display_name` → `"   "`: 422
- `test_put_profile_rejects_too_long_display_name` → 51 文字: 422
- `test_put_profile_returns_503_when_firestore_unset` → Firestore 未初期化: 503
- `test_put_profile_updates_firestore_and_returns_user` → ハッピーパス: 200・Firestore `update()` 呼び出し検証

`backend/tests/conftest.py` に `mock_firestore_db` フィクスチャ追加（`AsyncMock` ベース）。

フロントエンドのテスト（`profile/edit/+page.svelte` ＋ `apiPut`）は**別ストーリーに分割**。今回はバックエンドスライスのみ。

## 3. 影響範囲
- 変更: `backend/main.py`（ルート追加、`require_db` を Depends 経由に整理）
- 新規: `backend/tests/test_profile_update.py`、`conftest.py` への fixture 追加
- 変更しない: `middleware/auth.py`、フロントエンド（次ストーリー）

## 4. API契約
```
PUT /api/v1/profile
Authorization: Bearer <id-token>
Request: { "display_name": str (1-50 chars, トリム後) }
Response 200: { uid, email, display_name, photo_url, created_at, updated_at }
Errors:
  403 Authorization ヘッダ無し
  401 トークン不正
  422 display_name のバリデーション違反
  503 Firestore 未初期化
```

## 5. Firestore データ設計
変更なし。`users/{uid}` に既存の `display_name` を上書き、`updated_at` を `SERVER_TIMESTAMP` に更新。

## 6. スマホ対応計画
今回バックエンドのみのため対象外。次ストーリー（フロント実装）で対応。

## 7. 実装順序（TDD ベース）
- Step 0: テストファイル作成（Red を確認）
- Step 1: backend-agent → 最小実装（Green）
- Step 2: backend-agent → リファクタ（Pydantic モデル切り出し検討）
- Step 3: コミット履歴で test → impl → refactor の順序確認
