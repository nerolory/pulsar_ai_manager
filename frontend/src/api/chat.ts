import type { ChatMessage, ChatParams } from '@/types'
import { API_BASE_URL } from './apiService'

export interface StreamRequest {
  messages: Pick<ChatMessage, 'role' | 'content'>[]
  temperature: number
  max_tokens: number
  top_p: number
  system_prompt?: string
  use_context: boolean
}

export function buildStreamRequest(
  messages: ChatMessage[],
  params: ChatParams,
): StreamRequest {
  return {
    messages: messages.map(({ role, content }) => ({ role, content })),
    temperature: params.temperature,
    max_tokens: params.maxTokens,
    top_p: params.topP,
    system_prompt: params.systemPrompt || undefined,
    use_context: params.useContext,
  }
}

/**
 * Opens a streaming fetch to /api/v1/chat/stream.
 * Calls onChunk for each token, onDone when complete, onError on failure.
 */
export async function streamChat(
  request: StreamRequest,
  onChunk: (token: string) => void,
  onDone: () => void,
  onError: (error: Error) => void,
  signal?: AbortSignal,
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal,
    })

    if (!response.ok) {
      const text = await response.text()
      let message = `HTTP ${response.status}`
      try {
        const json = JSON.parse(text)
        message = json.error ?? json.detail ?? json.message ?? text
      } catch {
        message = text || message
      }
      throw new Error(message)
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      onChunk(decoder.decode(value, { stream: true }))
    }
    onDone()
  } catch (error) {
    if ((error as Error).name === 'AbortError') return
    onError(error instanceof Error ? error : new Error(String(error)))
  }
}
