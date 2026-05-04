# ADR-002: Firebase Auth × Cloud Run の認証分離

## 文脈
スマホファーストの認証 UX と、バックエンドの GCP ファースト方針を両立する必要がある。

## 決定
- 認証フロントエンド: Firebase Auth（Google プロバイダ）
- 認証検証: Cloud Run 上の FastAPI で Firebase Admin SDK の verify_id_token

## 結果
スマホ → リダイレクト認証、PC → ポップアップで分岐する。
