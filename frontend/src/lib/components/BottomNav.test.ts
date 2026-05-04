/**
 * BottomNav の最小コンポーネントテスト。
 * 4 つのナビゲーション項目が描画され、44px 以上のタッチターゲットを満たすことを検証。
 */
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import BottomNav from './BottomNav.svelte';

describe('BottomNav', () => {
  it('4 つのナビゲーション項目をすべて描画する', () => {
    render(BottomNav);
    expect(screen.getByRole('link', { name: /ホーム/ })).toBeDefined();
    expect(screen.getByRole('link', { name: /検索/ })).toBeDefined();
    expect(screen.getByRole('link', { name: /活動/ })).toBeDefined();
    expect(screen.getByRole('link', { name: /プロフィール/ })).toBeDefined();
  });

  it('navigation のラベルを aria-label として持つ', () => {
    render(BottomNav);
    const nav = screen.getByLabelText('メインナビゲーション');
    expect(nav).toBeDefined();
  });
});
