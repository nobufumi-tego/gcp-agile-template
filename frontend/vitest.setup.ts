/**
 * Vitest setup — SvelteKit ランタイムモジュールのモック。
 * コンポーネントテストで `$app/state` / `$app/navigation` 等を使うとき、
 * 実際の SvelteKit クライアントランタイムは初期化されないので最小モックを差す。
 */
import { vi } from 'vitest';

vi.mock('$app/state', () => ({
  page: {
    url: new URL('http://localhost/'),
    params: {},
    route: { id: '/' },
    status: 200,
    error: null,
    data: {},
    form: null,
    state: {}
  },
  navigating: null,
  updated: { check: () => Promise.resolve(false), current: false }
}));

vi.mock('$app/navigation', () => ({
  goto: vi.fn(),
  invalidate: vi.fn(),
  invalidateAll: vi.fn(),
  preloadCode: vi.fn(),
  preloadData: vi.fn(),
  beforeNavigate: vi.fn(),
  afterNavigate: vi.fn()
}));

vi.mock('$app/environment', () => ({
  browser: true,
  dev: true,
  building: false,
  version: 'test'
}));
