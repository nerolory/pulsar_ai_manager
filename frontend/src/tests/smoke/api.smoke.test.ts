/**
 * Smoke tests — hit the real backend.
 * Run only when VITE_API_URL is set and backend is up.
 * Skip automatically in CI / unit-only runs.
 */
import { describe, it, expect } from 'vitest'

const API = process.env.VITE_API_URL ?? 'http://localhost:8000'
const ENABLED = !!process.env.SMOKE

describe.skipIf(!ENABLED)('Backend smoke', () => {
  it('GET / returns app info', async () => {
    const res = await fetch(`${API}/`)
    expect(res.ok).toBe(true)
    const json = await res.json()
    expect(json.app).toBe('PulsarAI')
  })

  it('GET /api/v1/settings/health returns status field', async () => {
    const res = await fetch(`${API}/api/v1/settings/health`)
    expect(res.ok).toBe(true)
    const json = await res.json()
    expect(json).toHaveProperty('status')
    expect(json).toHaveProperty('provider')
  })

  it('POST /api/v1/settings/provider with mock succeeds', async () => {
    const res = await fetch(`${API}/api/v1/settings/provider`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider: 'mock' }),
    })
    expect(res.ok).toBe(true)
    const json = await res.json()
    expect(json.status).toBe('ok')
  })

  it('POST /api/v1/chat/stream returns streamed text', async () => {
    const res = await fetch(`${API}/api/v1/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [{ role: 'user', content: 'ping' }],
        temperature: 0.7,
        max_tokens: 128,
        top_p: 0.9,
        use_context: false,
      }),
    })
    expect(res.ok).toBe(true)
    const text = await res.text()
    expect(text.length).toBeGreaterThan(0)
  })
})
