export type MessageRole = 'user' | 'assistant' | 'system'

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
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

export type ProviderName = 'vsellm' | 'openrouter' | 'openai' | 'mock'

export interface ProviderConfig {
  provider: ProviderName
  apiKey?: string
  model?: string
  baseUrl?: string
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
