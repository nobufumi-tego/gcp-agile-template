<!-- src/routes/+page.svelte -->
<script lang="ts">
  import { goto } from '$app/navigation';
  import { isAuthenticated, authLoading } from '$lib/stores/auth';

  $effect(() => {
    if ($authLoading) return;
    goto($isAuthenticated ? '/home' : '/login', { replaceState: true });
  });
</script>

<div class="redirecting">
  <div class="spinner"></div>
</div>

<style>
  .redirecting {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100dvh;
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
