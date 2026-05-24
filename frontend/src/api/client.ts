const BASE_URL = import.meta.env.VITE_API_URL ?? ''

async function apiRequest(method: string, url: string, data?: any) {
  const fullUrl = `${BASE_URL}/api/v1${url}`
  console.debug(`[API →] ${method.toUpperCase()} ${fullUrl}`)
  
  try {
    const res = await fetch(fullUrl, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: data ? JSON.stringify(data) : undefined,
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
      console.error(`[API ✗] ${url}`, message)
      throw new Error(message)
    }

    const result = await res.json()
    console.debug(`[API ←] ${res.status} ${url}`, result)
    return result
  } catch (err) {
    if (err instanceof Error) {
      console.error(`[API ✗] ${url}`, err.message)
      throw err
    }
    const message = 'Unknown error'
    console.error(`[API ✗] ${url}`, message)
    throw new Error(message)
  }
}

export const http = {
  get: (url: string) => apiRequest('GET', url),
  post: (url: string, data: any) => apiRequest('POST', url, data),
  put: (url: string, data: any) => apiRequest('PUT', url, data),
  delete: (url: string) => apiRequest('DELETE', url),
}
