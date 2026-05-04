// src/lib/firebase/client.ts
// Firebase クライアント初期化（スマホファースト・軽量）
import { initializeApp, getApps, type FirebaseApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup,
         signInWithRedirect, getRedirectResult,
         signOut, onAuthStateChanged, type User } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';
import { browser } from '$app/environment';

// 環境変数（SvelteKit: PUBLIC_ prefix で公開）
const firebaseConfig = {
  apiKey:            import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain:        import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId:         import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket:     import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId:             import.meta.env.VITE_FIREBASE_APP_ID,
};

// SSR対策：ブラウザのみ初期化
let app: FirebaseApp;
if (browser) {
  app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
}

export const getFirebaseAuth = () => getAuth(app);
export const getFirebaseFirestore = () => getFirestore(app);
export const getFirebaseStorage = () => getStorage(app);

// Google認証プロバイダ
export const googleProvider = new GoogleAuthProvider();

// スマホ判定（モバイルはリダイレクト認証を使用）
const isMobile = () => browser && /iPhone|Android|iPad/i.test(navigator.userAgent);

// Googleログイン（スマホ: redirect / PC: popup）
export async function signInWithGoogle(): Promise<User | null> {
  const auth = getFirebaseAuth();
  if (isMobile()) {
    await signInWithRedirect(auth, googleProvider);
    return null; // リダイレクト後に getRedirectResult で取得
  } else {
    const result = await signInWithPopup(auth, googleProvider);
    return result.user;
  }
}

// リダイレクト後の結果取得（スマホ認証の完了処理）
export async function handleRedirectResult(): Promise<User | null> {
  const auth = getFirebaseAuth();
  const result = await getRedirectResult(auth);
  return result?.user ?? null;
}

// ログアウト
export async function logout(): Promise<void> {
  const auth = getFirebaseAuth();
  await signOut(auth);
}

// 認証状態の監視（Svelteストアと連携）
export function watchAuthState(callback: (user: User | null) => void) {
  const auth = getFirebaseAuth();
  return onAuthStateChanged(auth, callback);
}
