import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useChatStore } from '@/stores/chat'
import { computed } from 'vue'

vi.mock('@/api/chat', () => ({
  buildStreamRequest: vi.fn((msgs, params) => ({ messages: msgs, ...params })),
  streamChat: vi.fn(async (_req, onChunk, onDone) => {
    onChunk('Hello ')
    onChunk('world')
    onDone()
  }),
}))

vi.mock('@/stores/settings', () => ({
  useSettingsStore: () => ({
    isConfigured: computed(() => true),
  }),
}))

describe('useChatStore', () => {
  it('creates a chat with correct defaults', () => {
    const store = useChatStore()
    const chat = store.createChat('Test chat')
    expect(chat.title).toBe('Test chat')
    expect(chat.messages).toHaveLength(0)
    expect(store.activeChatId).toBe(chat.id)
  })

  it('addMessage appends to active chat', () => {
    const store = useChatStore()
    store.createChat()
    store.addMessage('user', 'Hello')
    expect(store.messages).toHaveLength(1)
    expect(store.messages[0].role).toBe('user')
    expect(store.messages[0].content).toBe('Hello')
  })

  it('auto-titles chat from first user message', () => {
    const store = useChatStore()
    store.createChat()
    store.addMessage('user', 'What is the meaning of life?')
    expect(store.activeChat?.title).toBe('What is the meaning of life?')
  })

  it('auto-truncates long titles to 40 chars + ellipsis', () => {
    const store = useChatStore()
    store.createChat()
    store.addMessage('user', 'A'.repeat(50))
    expect(store.activeChat?.title).toBe('A'.repeat(40) + '...')
  })

  it('deleteChat removes it and switches active', () => {
    const store = useChatStore()
    const c1 = store.createChat('c1')
    const c2 = store.createChat('c2')
    store.deleteChat(c2.id)
    expect(store.chats).toHaveLength(1)
    expect(store.activeChatId).toBe(c1.id)
  })

  it('clearMessages empties active chat', () => {
    const store = useChatStore()
    store.createChat()
    store.addMessage('user', 'hi')
    store.clearMessages()
    expect(store.messages).toHaveLength(0)
  })

  it('sendMessage streams tokens into assistant message', async () => {
    const store = useChatStore()
    store.createChat()
    await store.sendMessage('Hello')
    const assistant = store.messages.find((message) => message.role === 'assistant')
    expect(assistant?.content).toBe('Hello world')
    expect(store.streaming).toBe(false)
    expect(store.needsProvider).toBe(false)
  })

  it('needsProvider starts as false and resets to false after successful send', async () => {
    const store = useChatStore()
    expect(store.needsProvider).toBe(false)
    store.createChat()
    await store.sendMessage('Hello')
    expect(store.needsProvider).toBe(false)
  })
})
