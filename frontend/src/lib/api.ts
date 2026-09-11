import type { Business, CustomerAccessResponse } from '../types/api'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  const data = (await response.json().catch(() => null)) as { detail?: string; code?: string } | T | null
  if (!response.ok) {
    const error = data as { detail?: string; code?: string } | null
    const message = error?.detail ?? 'Unable to complete the request.'
    const requestError = new Error(message) as Error & { code?: string; status?: number }
    requestError.code = error?.code
    requestError.status = response.status
    throw requestError
  }
  return data as T
}

export function createCustomerAccess(slug: string, source: string) {
  return apiRequest<CustomerAccessResponse>(`/api/v1/access/${encodeURIComponent(slug)}`, {
    method: 'POST',
    body: JSON.stringify({ source }),
  })
}

export function getBusiness(slug: string) {
  return apiRequest<Business>(`/api/v1/businesses/${encodeURIComponent(slug)}`)
}

export function recordSocialClick(slug: string, socialLinkId: number) {
  return apiRequest<unknown>(`/api/v1/businesses/${encodeURIComponent(slug)}/social-links/${socialLinkId}/click`, {
    method: 'POST',
    body: JSON.stringify({}),
  })
}
