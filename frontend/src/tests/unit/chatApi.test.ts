import { describe, it, expect } from 'vitest'
import { buildStreamRequest } from '@/api/chat'
import type { ChatMessage, ChatParams } from '@/types'

const params: ChatParams = {
  temperature: 0.7,
  maxTokens: 2048,
  topP: 0.9,
  systemPrompt: 'Be concise',
  useContext: true,
  contextDepth: 10,
}

const messages: ChatMessage[] = [
  { id: '1', role: 'user', content: 'Hello', createdAt: 0 },
  { id: '2', role: 'assistant', content: 'Hi', createdAt: 0 },
]

describe('buildStreamRequest', () => {
  it('maps messages to role+content only', () => {
    const req = buildStreamRequest(messages, params)
    expect(req.messages).toEqual([
      { role: 'user', content: 'Hello' },
      { role: 'assistant', content: 'Hi' },
    ])
  })

  it('passes params correctly', () => {
    const req = buildStreamRequest(messages, params)
    expect(req.temperature).toBe(0.7)
    expect(req.max_tokens).toBe(2048)
    expect(req.system_prompt).toBe('Be concise')
    expect(req.use_context).toBe(true)
  })

  it('omits system_prompt when empty', () => {
    const req = buildStreamRequest(messages, { ...params, systemPrompt: '' })
    expect(req.system_prompt).toBeUndefined()
  })
})
