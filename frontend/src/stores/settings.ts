import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ProviderConfig, HealthStatus, ProviderName } from '@/types'
import { configureProvider, getHealth, getProviderConfig } from '@/api/settings'

export const useSettingsStore = defineStore('settings', () => {
  const activeProvider = ref<ProviderName | null>(null)
  const activeModel = ref<string | null>(null)
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
    } catch (err) {
      error.value = (err as Error).message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function checkHealth() {
    try {
      health.value = await getHealth()
    } catch (err) {
      console.error('Health check failed:', err)
      error.value = `Health check failed: ${(err as Error).message}`
      health.value = { status: 'error', provider: 'none', mockMode: false }
    }
  }

  async function loadProviderConfig() {
    try {
      const cfg = await getProviderConfig()
      activeProvider.value = cfg.provider
      activeModel.value = cfg.model
    } catch (err) {
      console.error('Failed to load provider config:', err)
    }
    await checkHealth()
  }

  const isConfigured = computed(() =>
    health.value === null || health.value.status !== 'no_provider',
  )

  return { activeProvider, activeModel, health, loading, error, isConfigured, applyProvider, checkHealth, loadProviderConfig }
})
