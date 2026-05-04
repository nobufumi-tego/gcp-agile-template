## Firebase 認証・Hosting 設定

### Firebase コンソール設定（初回必須）
1. Firebase コンソール → Authentication → Sign-in method → Google を有効化
2. 承認済みドメインに `your-project.web.app` を追加
3. Firebase コンソール → プロジェクト設定 → マイアプリ → SDK設定をコピー
4. `frontend/.env.local` に貼り付け

### 認証フロー
```
スマホ: Googleログイン → リダイレクト認証 → IDトークン取得
  PC:  Googleログイン → ポップアップ認証  → IDトークン取得

IDトークン → Authorization: Bearer [token] → Cloud Run FastAPI
FastAPI → firebase_auth.verify_id_token() → uid取得 → Firestore操作
```

### Firebase Hosting デプロイ
```bash
cd frontend && npm run build
firebase deploy --only hosting
# → https://[PROJECT_ID].web.app
```

### Firestore セキュリティルール（初回必須）
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // ユーザーは自分のドキュメントのみ読み書き可
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    // その他のコレクションは認証済みユーザーのみ
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```
