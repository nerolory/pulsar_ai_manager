import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ProviderConfig, HealthStatus, ProviderName } from '@/types'
import { configureProvider, getHealth, getProviderConfig } from '@/api/settings'

export const useSettingsStore = defineStore('settings', () => {
  const activeProvider = ref<ProviderName | null>(null)
  const activeModel = ref<string | null>(null)
  const savedProviders = ref<Record<string, { api_key: string | null; model: string | null }>>({})
  const health = ref<HealthStatus | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function applyProvider(config: ProviderConfig) {
    loading.value = true
    error.value = null
    try {
      await configureProvider(config)
      activeProvider.value = config.provider
      activeModel.value = config.model ?? null
      await checkHealth()
    } catch (error) {
      error.value = (error as Error).message
      throw error
    } finally {
      loading.value = false
    }
  }

  async function checkHealth() {
    try {
      health.value = await getHealth()
    } catch (error) {
      console.error('Health check failed:', error)
      error.value = `Health check failed: ${(error as Error).message}`
      health.value = { status: 'error', provider: 'none', mockMode: false }
    }
  }

  async function loadProviderConfig() {
    try {
      const config = await getProviderConfig()
      activeProvider.value = config.provider
      activeModel.value = config.model
      savedProviders.value = (config as any).all_providers ?? {}
    } catch (error) {
      console.error('Failed to load provider config:', error)
    }
    await checkHealth()
  }

  const isConfigured = computed(() =>
    health.value === null || health.value.status !== 'no_provider',
  )

  return { activeProvider, activeModel, savedProviders, health, loading, error, isConfigured, applyProvider, checkHealth, loadProviderConfig }
})
