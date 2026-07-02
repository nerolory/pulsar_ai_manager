/**
 * Central API service — single source of truth for all HTTP requests.
 * Always uses relative URLs so Vite proxy handles routing to the backend.
 * Never hardcode backend host here or in callers.
 */

export const API_BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? ''
const API_PREFIX = `${API_BASE_URL}/api/v1`

export class ApiHttpError extends Error {
  status: number
  body: unknown

  constructor(status: number, message: string, body?: unknown) {
    super(message)
    this.name = 'ApiHttpError'
    this.status = status
    this.body = body
  }
}

async function request<T = unknown>(method: string, path: string, data?: unknown): Promise<T> {
  const url = `${API_PREFIX}${path}`

  const response = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: data !== undefined ? JSON.stringify(data) : undefined,
  })

  if (!response.ok) {
    const text = await response.text()
    let message = `HTTP ${response.status}`
    let body: unknown = text
    try {
      const json = JSON.parse(text)
      body = json
      message = json.error ?? json.detail ?? json.message ?? text
      if (typeof message === 'object') {
        message = JSON.stringify(message)
      }
    } catch {
      message = text || message
    }
    console.error(`[API ✗] ${method} ${url}`, message)
    throw new ApiHttpError(response.status, String(message), body)
  }

  return await response.json() as T
}

export const api = {
  get:    <T>(path: string)               => request<T>('GET',    path),
  post:   <T>(path: string, data: unknown) => request<T>('POST',   path, data),
  put:    <T>(path: string, data: unknown) => request<T>('PUT',    path, data),
  patch:  <T>(path: string, data: unknown) => request<T>('PATCH',  path, data),
  delete: <T>(path: string)               => request<T>('DELETE', path),
}
