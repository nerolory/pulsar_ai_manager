export type MessageRole = 'user' | 'assistant' | 'system'

export interface ContentImageUrl {
  url: string
}

export interface ContentPart {
  type: 'text' | 'image_url'
  text?: string
  image_url?: ContentImageUrl
}

export type MessageContent = string | ContentPart[]

export interface ChatMessage {
  id: string
  role: MessageRole
  content: MessageContent
  createdAt: number
  model?: string
  rowid?: number
}

export interface Chat {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: number
  updatedAt: number
}

export type ProviderName = 'vsellm' | 'openrouter' | 'openai' | 'anthropic' | 'groq' | 'cerebras' | 'qwen' | 'mistral' | 'gemini' | 'gigachat' | 'mock'

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

export interface ChatParams {
  temperature: number
  maxTokens: number
  topP: number
  systemPrompt: string
  useContext: boolean
  contextDepth: number
}

export interface HealthStatus {
  status: 'ok' | 'error' | 'no_provider'
  provider: string
  model?: string
  mockMode: boolean
}

export interface StreamChunk {
  text: string
  done: boolean
}
