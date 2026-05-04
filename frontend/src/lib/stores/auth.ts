// src/lib/stores/auth.ts
// 認証状態のグローバルストア（SvelteKit）
import { writable, derived } from 'svelte/store';
import type { User } from 'firebase/auth';
import { browser } from '$app/environment';
import { watchAuthState, handleRedirectResult } from '$lib/firebase/client';

// 認証状態
export const user = writable<User | null>(null);
export const authLoading = writable<boolean>(true);

// ログイン済みかどうか
export const isAuthenticated = derived(user, ($user) => $user !== null);

// IDトークン（バックエンドAPI認証用）
export const idToken = writable<string | null>(null);

// 認証状態の初期化（ルートレイアウトで呼ぶ）
export function initAuth() {
  if (!browser) return;

  // リダイレクト認証の完了処理（スマホGoogle認証後）
  handleRedirectResult().then((redirectUser) => {
    if (redirectUser) user.set(redirectUser);
  });

  // 認証状態の監視
  return watchAuthState(async (firebaseUser) => {
    user.set(firebaseUser);
    authLoading.set(false);

    if (firebaseUser) {
      // IDトークンを取得してバックエンドAPI呼び出しに使用
      const token = await firebaseUser.getIdToken();
      idToken.set(token);

      // トークンの自動更新（1時間ごと）
      setInterval(async () => {
        const refreshed = await firebaseUser.getIdToken(true);
        idToken.set(refreshed);
      }, 55 * 60 * 1000);
    } else {
      idToken.set(null);
    }
  });
}
