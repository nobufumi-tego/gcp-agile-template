/// <reference types="vitest" />
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  // Vitest 経由でコンポーネントテストを走らせるとき、Svelte は browser 条件で解決する必要がある
  // （SSR エントリだと mount(...) が server context で利用不可になる）
  resolve: process.env.VITEST
    ? { conditions: ['browser'] }
    : undefined,
  test: {
    include: ['src/**/*.{test,spec}.{js,ts}'],
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts']
  }
});
