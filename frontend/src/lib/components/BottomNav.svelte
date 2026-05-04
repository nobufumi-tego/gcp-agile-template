<!-- src/lib/components/BottomNav.svelte -->
<!-- スマホ標準ボトムナビゲーション・Safe Area対応 -->
<script lang="ts">
  import { page } from '$app/state';

  const navItems = [
    { href: '/home', icon: '🏠', label: 'ホーム' },
    { href: '/search', icon: '🔍', label: '検索' },
    { href: '/activity', icon: '📊', label: '活動' },
    { href: '/profile', icon: '👤', label: 'プロフィール' }
  ];

  const currentPath = $derived(page.url.pathname);
</script>

<nav class="bottom-nav" aria-label="メインナビゲーション">
  {#each navItems as item}
    <a
      href={item.href}
      class="nav-item"
      class:active={currentPath.startsWith(item.href)}
      aria-current={currentPath.startsWith(item.href) ? 'page' : undefined}
    >
      <span class="nav-icon" aria-hidden="true">{item.icon}</span>
      <span class="nav-label">{item.label}</span>
    </a>
  {/each}
</nav>

<style>
  .bottom-nav {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 430px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: #fff;
    border-top: 0.5px solid #e5e7eb;
    padding-bottom: env(safe-area-inset-bottom);
    z-index: 100;
  }

  .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 56px; /* タッチターゲット確保 */
    padding: 8px 4px;
    text-decoration: none;
    color: #9ca3af;
    font-size: 0.625rem;
    gap: 2px;
    transition: color 0.15s;
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }

  .nav-item.active {
    color: #3b82f6;
  }

  .nav-icon {
    font-size: 1.25rem;
    line-height: 1;
  }

  .nav-label {
    font-weight: 500;
  }
</style>
