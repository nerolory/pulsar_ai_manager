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

export type ProviderName = 'vsellm' | 'openrouter' | 'openai' | 'anthropic' | 'groq' | 'cerebras' | 'qwen' | 'mistral' | 'gemini' | 'mock'

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
