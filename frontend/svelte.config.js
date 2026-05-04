import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    // Firebase Hosting は静的ホスティング → adapter-static で SPA 化
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html', // SPA：未知ルートを index.html にフォールバック
      precompress: false,
      strict: false
    }),
    alias: {
      $lib: './src/lib'
    }
  }
};

export default config;
