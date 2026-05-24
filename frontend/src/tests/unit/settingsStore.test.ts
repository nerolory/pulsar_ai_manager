import { describe, it, expect, vi } from 'vitest'
import { useSettingsStore } from '@/stores/settings'

vi.mock('@/api/settings', () => ({
  configureProvider: vi.fn(async () => {}),
  getHealth: vi.fn(async () => ({
    status: 'ok',
    provider: 'MockProvider',
    mockMode: true,
  })),
  getProviderConfig: vi.fn(async () => ({ provider: 'mock', model: null })),
}))

describe('useSettingsStore', () => {
  it('applyProvider updates provider state', async () => {
    const store = useSettingsStore()
    await store.applyProvider({ provider: 'mock' })
    expect(store.activeProvider).toBe('mock')
    expect(store.error).toBeNull()
  })

  it('checkHealth populates health state', async () => {
    const store = useSettingsStore()
    await store.checkHealth()
    expect(store.health?.status).toBe('ok')
    expect(store.health?.mockMode).toBe(true)
  })

  it('applyProvider sets error on failure', async () => {
    const { configureProvider } = await import('@/api/settings')
    vi.mocked(configureProvider).mockRejectedValueOnce(new Error('bad key'))
    const store = useSettingsStore()
    await expect(store.applyProvider({ provider: 'vsellm', apiKey: 'bad' })).rejects.toThrow()
    expect(store.error).toBe('bad key')
  })
})
