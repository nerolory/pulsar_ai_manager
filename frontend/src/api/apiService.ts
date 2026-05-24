/**
 * Central API service — single source of truth for all HTTP requests.
 * Always uses relative URLs so Vite proxy handles routing to the backend.
 * Never hardcode backend host here or in callers.
 */

const API_PREFIX = '/api/v1'

async function request<T = unknown>(method: string, path: string, data?: unknown): Promise<T> {
  const url = `${API_PREFIX}${path}`
  console.debug(`[API →] ${method} ${url}`)

  const res = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: data !== undefined ? JSON.stringify(data) : undefined,
  })

  if (!res.ok) {
    const text = await res.text()
    let message = `HTTP ${res.status}`
    try {
      const json = JSON.parse(text)
      message = json.detail ?? json.message ?? text
    } catch {
      message = text || message
    }
    console.error(`[API ✗] ${method} ${url}`, message)
    throw new Error(message)
  }

  const result = await res.json() as T
  console.debug(`[API ←] ${res.status} ${url}`)
  return result
}

export const api = {
  get:    <T>(path: string)               => request<T>('GET',    path),
  post:   <T>(path: string, data: unknown) => request<T>('POST',   path, data),
  put:    <T>(path: string, data: unknown) => request<T>('PUT',    path, data),
  patch:  <T>(path: string, data: unknown) => request<T>('PATCH',  path, data),
  delete: <T>(path: string)               => request<T>('DELETE', path),
}
