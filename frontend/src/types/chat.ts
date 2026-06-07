/** Chat domain types — messages, conversations, and streaming. */

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
  /** Free model ID suggested when balance error occurs. */
  freeModelId?: string
}

export interface Chat {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: number
  updatedAt: number
}

export interface ChatParams {
  temperature: number
  maxTokens: number
  topP: number
  systemPrompt: string
  useContext: boolean
  contextDepth: number
}

export interface StreamChunk {
  text: string
  done: boolean
}
