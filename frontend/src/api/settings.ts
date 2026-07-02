import { api } from './apiService'
import type { ProviderConfig, HealthStatus, ProviderName, ProviderCapabilities, ModelInfo } from '@/types'

export interface ProviderMetadata {
  name: string
  desc: string
  key_placeholder: string
  default_model: string
  base_url: string
  model_name: string
  model_name_code?: string
}

export interface SavedProviderEntry {
  api_key: string | null
  model: string | null
}

export interface ProviderConfigResponse {
  provider: ProviderName | null
  model: string | null
  api_key?: string | null
  all_providers?: Record<string, SavedProviderEntry>
}

export interface ProvidersListResponse {
  providers: Record<string, ProviderMetadata>
}

export interface ProviderBalance {
  balance: number
  currency: string
}

export interface BalanceResponse {
  balance: ProviderBalance | null
  message?: string
  message_code?: string
}

export interface ModelGroupInfo {
  id: string
  name: string
  description: string
}

interface HealthResponseRaw {
  status: string
  provider?: string
  model?: string
  mock_mode?: boolean
}

export async function configureProvider(config: ProviderConfig): Promise<void> {
  await api.post('/settings/provider', {
    provider: config.provider,
    api_key: config.apiKey,
    model: config.model,
    base_url: config.baseUrl,
  })
}

export async function testPrompt(): Promise<{ follows_instructions: boolean; model_answer: string }> {
  return await api.post('/settings/test-prompt', {})
}

export async function getProviderConfig(): Promise<ProviderConfigResponse> {
  return await api.get('/settings/provider')
}

export async function getProviders(): Promise<ProvidersListResponse> {
  return await api.get('/settings/providers')
}

export async function getHealth(): Promise<HealthStatus> {
  const data = await api.get<HealthResponseRaw>('/settings/health')
  if (!data) {
    throw new Error('No data received from health endpoint')
  }
  return {
    status: data.status as HealthStatus['status'],
    provider: data.provider ?? 'none',
    model: data.model,
    mockMode: data.mock_mode ?? false,
  }
}

export async function getCapabilities(): Promise<ProviderCapabilities> {
  return await api.get('/settings/capabilities')
}

export async function getModels(refresh = false, provider?: string): Promise<{ models: ModelInfo[]; source: string }> {
  const params = new URLSearchParams({ refresh: refresh.toString() })
  if (provider) params.append('provider', provider)
  return await api.get(`/settings/models?${params.toString()}`)
}

export async function refreshModels(): Promise<{ models: ModelInfo[]; source: string }> {
  return await api.post('/settings/refresh-models', {})
}

export async function detectProvider(baseUrl: string): Promise<{ provider: string | null; detected: boolean; compatible: boolean; message?: string; message_code?: string }> {
  return await api.post('/settings/detect-provider', { base_url: baseUrl })
}

export async function getBalance(): Promise<BalanceResponse> {
  return await api.get('/settings/balance')
}

export async function switchModel(model: string): Promise<{ success: boolean; model: string }> {
  return await api.post('/settings/switch-model', { model })
}

export async function getModelGroups(): Promise<{ groups: Record<string, ModelGroupInfo> }> {
  return await api.get('/settings/model-groups')
}

// Local LLM API functions
export async function getSystemCheck(): Promise<{
  specs: {
    total_ram_gb: number
    available_ram_gb: number
    cpu_cores: number
    cpu_threads: number
    cpu_freq_ghz: number
    gpu_available: boolean
    gpu_name: string | null
    gpu_vram_gb: number | null
    disk_free_gb: number
    os_name: string
    os_version: string
    architecture: string
  }
  tier: {
    tier: string
    can_run_local_llm: boolean
    recommended_model: string | null
    reason: string
    reason_code?: string
    reason_params?: Record<string, string | number>
    description_code?: string
  }
  cpu_features: Record<string, boolean>
}> {
  return await api.get('/admin/system-check')
}

export async function getLocalLLMSettings(): Promise<{
  enabled: boolean
  model: string
  can_run: boolean
  tier: string | null
  message: string
  message_code?: string
  message_params?: Record<string, string | number>
}> {
  return await api.get('/admin/local-llm/settings')
}

export async function getLocalModels(): Promise<{
  models: Record<string, {
    name: string
    params: string
    tier: string
    requirements: {
      ram_gb: number
      cpu_cores: number
      disk_gb: number
      gpu_vram_gb: number | null
    }
    download_url: string
    format: string
    context_length: number
    quantization: string
    downloaded: boolean
    can_run?: boolean
    can_run_reason?: string
    can_run_reason_code?: string
    can_run_reason_params?: Record<string, string | number>
  }>
  downloaded: string[]
  storage_info: {
    model_count: number
    total_size_gb: number
    models_dir: string
  }
}> {
  return await api.get('/admin/local-llm/models')
}

export async function downloadLocalModel(modelId: string): Promise<{
  success: boolean
  message: string
  status?: string
}> {
  return await api.post(`/admin/local-llm/download/${modelId}`, {})
}

export interface LocalDownloadJob {
  model_id: string
  status: 'idle' | 'downloading' | 'completed' | 'failed'
  bytes_done: number
  bytes_total: number
  percent: number
  error?: string | null
  message?: string | null
}

export async function getLocalDownloadJobs(): Promise<{ downloads: LocalDownloadJob[] }> {
  return await api.get('/admin/local-llm/downloads')
}

export async function getLocalDownloadStatus(modelId: string): Promise<LocalDownloadJob> {
  return await api.get(`/admin/local-llm/download/${modelId}/status`)
}

export async function deleteLocalModel(modelId: string): Promise<{
  success: boolean
  message: string
}> {
  return await api.delete(`/admin/local-llm/delete/${modelId}`)
}
