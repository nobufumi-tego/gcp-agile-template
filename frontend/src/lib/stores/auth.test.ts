/**
 * 認証ストアの最小テスト。
 * 実装側で Firebase をモックするのは将来 - ここではストアの初期値・派生ストアの整合性のみ検証。
 */
import { describe, expect, it } from 'vitest';
import { get } from 'svelte/store';
import { authLoading, idToken, isAuthenticated, user } from './auth';

describe('auth stores', () => {
  it('user は初期状態で null', () => {
    expect(get(user)).toBeNull();
  });

  it('isAuthenticated は user が null のとき false', () => {
    expect(get(isAuthenticated)).toBe(false);
  });

  it('idToken は初期状態で null', () => {
    expect(get(idToken)).toBeNull();
  });

  it('authLoading は初期状態で true（onAuthStateChanged 完了前）', () => {
    expect(get(authLoading)).toBe(true);
  });
});
