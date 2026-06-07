import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ProviderConfig, HealthStatus, ProviderName, ProviderCapabilities, ModelInfo } from '@/types'
import type { ProviderMetadata } from '@/api/settings'
import { configureProvider, getHealth, getProviderConfig, getCapabilities, getModels, refreshModels, getProviders } from '@/api/settings'

export const useSettingsStore = defineStore('settings', () => {
  const activeProvider = ref<ProviderName | null>(null)
  const activeModel = ref<string | null>(null)
  const savedProviders = ref<Record<string, { api_key: string | null; model: string | null }>>({})
  const health = ref<HealthStatus | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const capabilities = ref<ProviderCapabilities | null>(null)
  const models = ref<ModelInfo[]>([])
  const modelsSource = ref<string>('cache')
  const providersMetadata = ref<Record<string, ProviderMetadata>>({})

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
      const config = await getProviderConfig()
      activeProvider.value = config.provider
      activeModel.value = config.model
      savedProviders.value = (config as any).all_providers ?? {}
    } catch (err) {
      console.error('Failed to load provider config:', err)
    }
    // Load health check after config is loaded
    await checkHealth()
  }

  async function loadProvidersMetadata() {
    try {
      providersMetadata.value = await getProviders()
    } catch (err) {
      console.error('Failed to load providers metadata:', err)
    }
  }

  async function loadCapabilities() {
    try {
      capabilities.value = await getCapabilities()
    } catch (err) {
      console.error('Failed to load capabilities:', err)
    }
  }

  async function loadModels(refresh = false) {
    try {
      const response = await getModels(refresh)
      models.value = response.models
      modelsSource.value = response.source
    } catch (err) {
      console.error('Failed to load models:', err)
    }
  }

  async function loadAllSettings() {
    // Load provider config first (highest priority)
    await loadProviderConfig()
    
    // Load providers metadata in parallel with other non-dependent calls
    const providersPromise = loadProvidersMetadata()
    
    // Load capabilities and models in parallel after provider config is loaded
    if (activeProvider.value) {
      await Promise.all([
        providersPromise,
        loadCapabilities(),
        loadModels()
      ])
    } else {
      await providersPromise
    }
  }

  async function refreshModelsList() {
    await loadModels(true)
  }

  const isConfigured = computed(() =>
    health.value === null || health.value.status !== 'no_provider',
  )

  return { 
    activeProvider, 
    activeModel, 
    savedProviders, 
    health, 
    loading, 
    error, 
    capabilities,
    models,
    modelsSource,
    providersMetadata,
    isConfigured, 
    applyProvider, 
    checkHealth, 
    loadProviderConfig,
    loadAllSettings,
    loadProvidersMetadata,
    loadCapabilities,
    loadModels,
    refreshModelsList
  }
})
