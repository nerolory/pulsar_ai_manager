/** Provider domain types — configuration, capabilities, models, health. */

export type ProviderName = 'vsellm' | 'openrouter' | 'openai' | 'anthropic' | 'groq' | 'cerebras' | 'qwen' | 'mistral' | 'gemini' | 'gigachat' | 'local_llm' | 'mock'

export interface ProviderConfig {
  provider: ProviderName
  apiKey?: string
  model?: string
  baseUrl?: string
}

export interface ProviderCapabilities {
  supports_caching: boolean
  supports_images: boolean
  supports_pdf: boolean
  supports_system_prompt: boolean
  supports_files: string[]
  max_context_tokens: number
  streaming: boolean
  pricing_model: 'per_token' | 'per_request'
  has_balance_api: boolean
  has_models_list: boolean
  free_tier_available: boolean
}

export interface ModelInfo {
  id: string
  name: string
  context_length: number
  pricing?: Record<string, unknown> | null
  free_tier: boolean
  is_free?: boolean
  daily_limit?: number
  requires_payment?: boolean
  model_group_id?: string
  balance?: number
  limit_period?: string
  limit_tokens?: number
}

export interface HealthStatus {
  status: 'ok' | 'error' | 'no_provider'
  provider: string
  model?: string
  mockMode: boolean
}
