// src/lib/firebase/api.ts
// Firebase IDトークンを使ったバックエンドAPIクライアント
import { get } from 'svelte/store';
import { idToken } from '$lib/stores/auth';

const API_BASE = import.meta.env.VITE_API_BASE_URL; // Cloud Run URL

// 認証付きfetch（全APIリクエストの基底）
async function authFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = get(idToken);
  if (!token) throw new Error('未認証');

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(error.message ?? 'APIエラー');
  }

  return res;
}

// GET
export async function apiGet<T>(path: string): Promise<T> {
  const res = await authFetch(path);
  return res.json();
}

// POST
export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await authFetch(path, {
    method: 'POST',
    body: JSON.stringify(body),
  });
  return res.json();
}

// PUT
export async function apiPut<T>(path: string, body: unknown): Promise<T> {
  const res = await authFetch(path, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
  return res.json();
}

// DELETE
export async function apiDelete<T>(path: string): Promise<T> {
  const res = await authFetch(path, { method: 'DELETE' });
  return res.json();
}
