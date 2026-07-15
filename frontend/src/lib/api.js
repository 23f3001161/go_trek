import { useAuthStore } from '@/stores/auth'

export async function apiFetch(path, options = {}) {
  const auth = useAuthStore()
  const res = await fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authentication-Token': auth.token,
      ...options.headers,
    },
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || data.message || 'Request failed')
  return data
}
