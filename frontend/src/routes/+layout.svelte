<!-- src/routes/+layout.svelte -->
<!-- 全ページ共通：認証初期化・ボトムナビ・Safe Area対応 -->
<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { initAuth, isAuthenticated, authLoading } from '$lib/stores/auth';
  import BottomNav from '$lib/components/BottomNav.svelte';

  let { children } = $props();

  // 認証が必要なルート
  const protectedRoutes = ['/home', '/profile', '/settings'];

  onMount(() => {
    const unsubscribe = initAuth();
    return unsubscribe;
  });

  // 未認証なら保護ルートへのアクセスをブロックして /login へ
  $effect(() => {
    if (!$authLoading && !$isAuthenticated) {
      if (protectedRoutes.some((r) => page.url.pathname.startsWith(r))) {
        goto('/login');
      }
    }
  });
</script>

<!-- Safe Area 対応（iPhone ノッチ・ホームバー） -->
<div class="app-shell">
  {#if $authLoading}
    <!-- スプラッシュ（認証確認中） -->
    <div class="splash">
      <div class="spinner"></div>
    </div>
  {:else}
    <main class="main-content">
      {@render children()}
    </main>

    {#if $isAuthenticated}
      <BottomNav />
    {/if}
  {/if}
</div>

<style>
  .app-shell {
    display: flex;
    flex-direction: column;
    min-height: 100dvh; /* dynamic viewport height（スマホアドレスバー対応） */
    max-width: 430px; /* スマホ最大幅 */
    margin: 0 auto;
  }

  .main-content {
    flex: 1;
    overflow-y: auto;
    padding-bottom: calc(64px + env(safe-area-inset-bottom));
  }

  .splash {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100dvh;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
