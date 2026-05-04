<!-- src/routes/login/+page.svelte -->
<!-- スマホファーストのログインページ -->
<script lang="ts">
  import { goto } from '$app/navigation';
  import { signInWithGoogle } from '$lib/firebase/client';
  import { isAuthenticated } from '$lib/stores/auth';

  let loading = $state(false);
  let error = $state('');

  // ログイン済みならホームへ
  $effect(() => {
    if ($isAuthenticated) goto('/home');
  });

  async function handleGoogleLogin() {
    loading = true;
    error = '';
    try {
      await signInWithGoogle();
      // スマホはリダイレクト認証なのでここには戻ってこない
      // PCはここでポップアップ完了 → $isAuthenticated が true になる
    } catch (e) {
      error = 'ログインに失敗しました。もう一度お試しください。';
      loading = false;
    }
  }
</script>

<div class="login-page">
  <div class="logo-area">
    <div class="logo">🔷</div>
    <h1>[APP_NAME]</h1>
    <p>[サービスの一言説明]</p>
  </div>

  <div class="auth-area">
    {#if error}
      <div class="error-msg" role="alert">{error}</div>
    {/if}

    <button
      class="google-btn"
      onclick={handleGoogleLogin}
      disabled={loading}
      aria-busy={loading}
    >
      {#if loading}
        <span class="btn-spinner"></span>
        <span>ログイン中...</span>
      {:else}
        <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        <span>Googleでログイン</span>
      {/if}
    </button>

    <p class="terms">
      ログインすることで<a href="/terms">利用規約</a>と
      <a href="/privacy">プライバシーポリシー</a>に同意したことになります。
    </p>
  </div>
</div>

<style>
  .login-page {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 100dvh;
    padding: 2rem 1.5rem;
    padding-bottom: calc(2rem + env(safe-area-inset-bottom));
    gap: 3rem;
  }

  .logo-area {
    text-align: center;
  }

  .logo {
    font-size: 4rem;
    margin-bottom: 1rem;
  }

  h1 {
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 0.5rem;
    color: #111;
  }

  p {
    color: #6b7280;
    margin: 0;
    font-size: 0.9rem;
  }

  .auth-area {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .google-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    width: 100%;
    min-height: 52px; /* タッチターゲット44px以上 */
    background: #fff;
    border: 1.5px solid #d1d5db;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 500;
    color: #374151;
    cursor: pointer;
    transition: background 0.15s, box-shadow 0.15s;
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }

  .google-btn:active {
    background: #f9fafb;
  }

  .google-btn:disabled {
    opacity: 0.6;
  }

  .btn-spinner {
    width: 18px;
    height: 18px;
    border: 2px solid #d1d5db;
    border-top-color: #6b7280;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .error-msg {
    padding: 0.75rem 1rem;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    color: #dc2626;
    font-size: 0.875rem;
  }

  .terms {
    font-size: 0.75rem;
    text-align: center;
    color: #9ca3af;
  }

  .terms a {
    color: #6b7280;
  }
</style>
