import { api } from './apiService'
import type { ProviderConfig, HealthStatus, ProviderName } from '@/types'

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

export async function getProviderConfig(): Promise<{ provider: ProviderName | null; model: string | null }> {
  return await api.get('/settings/provider')
}

export async function getHealth(): Promise<HealthStatus> {
  const data = await api.get<any>('/settings/health')
  if (!data) {
    throw new Error('No data received from health endpoint')
  }
  return {
    status: data.status as HealthStatus['status'],
    provider: data.provider,
    model: data.model,
    mockMode: data.mock_mode,
  }
}
