/**
 * profile モジュールのフロントエンド API クライアント。
 * frontend/src/lib/firebase/api.ts の authFetch を使う。
 */
import { apiGet, apiPut } from '$lib/firebase/api';

export type Profile = {
  uid: string;
  email: string | null;
  display_name: string | null;
  photo_url: string | null;
  created_at?: string;
  updated_at?: string;
};

export async function getProfile(): Promise<Profile> {
  return apiGet<Profile>('/api/v1/profile');
}

export async function updateDisplayName(name: string): Promise<Profile> {
  return apiPut<Profile>('/api/v1/profile', { display_name: name });
}
