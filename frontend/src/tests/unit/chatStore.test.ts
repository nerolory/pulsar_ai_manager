import { describe, it, expect, vi } from 'vitest'
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useSettingsStore } from '@/stores/settings'

vi.mock('@/api/chats', () => ({
  listChats: vi.fn(async () => []),
  createChat: vi.fn(async () => ({})),
  renameChat: vi.fn(async () => ({})),
  addMessageToChat: vi.fn(async () => ({})),
  reorderChats: vi.fn(async () => ({})),
  clearChatMessages: vi.fn(async () => ({})),
  deleteChat: vi.fn(async () => ({})),
  getChatMessages: vi.fn(async () => []),
}))

vi.mock('@/composables/useStreamChat', () => {
  const streaming = ref(false)
  return {
    useStreamChat: () => ({
      streaming,
      execute: vi.fn(async (_request, options: { onToken?: (t: string) => void } = {}) => {
        options.onToken?.('Hello ')
        options.onToken?.('world')
        streaming.value = false
        return {
          success: true,
          content: 'Hello world',
          error: null,
          isBalanceError: false,
          aborted: false,
        }
      }),
      abort: vi.fn(),
    }),
  }
})

function configureSettings() {
  const settings = useSettingsStore()
  settings.health = { status: 'ok', provider: 'mock', model: 'test-model', mockMode: false }
  settings.activeProvider = 'mock'
  settings.activeModel = 'test-model'
}

describe('useChatStore', () => {
  it('creates a chat with correct defaults', () => {
    configureSettings()
    const store = useChatStore()
    const chat = store.createChat('Test chat')
    expect(chat.title).toBe('Test chat')
    expect(chat.messages).toHaveLength(0)
    expect(store.activeChatId).toBe(chat.id)
  })

  it('addMessage appends to active chat', () => {
    configureSettings()
    const store = useChatStore()
    store.createChat()
    store.addMessage('user', 'Hello')
    expect(store.messages).toHaveLength(1)
    expect(store.messages[0].role).toBe('user')
    expect(store.messages[0].content).toBe('Hello')
  })

  it('auto-titles chat from first three words of user message', () => {
    configureSettings()
    const store = useChatStore()
    store.createChat()
    store.addMessage('user', 'What is the meaning of life?')
    expect(store.activeChat?.title).toBe('What is the...')
  })

  it('does not truncate short single-word titles', () => {
    configureSettings()
    const store = useChatStore()
    store.createChat()
    store.addMessage('user', 'Hello')
    expect(store.activeChat?.title).toBe('Hello')
  })

  it('deleteChat removes it and switches active', () => {
    configureSettings()
    const store = useChatStore()
    const c1 = store.createChat('c1')
    const c2 = store.createChat('c2')
    store.deleteChat(c2.id)
    expect(store.chats).toHaveLength(1)
    expect(store.activeChatId).toBe(c1.id)
  })

  it('clearMessages empties active chat', () => {
    configureSettings()
    const store = useChatStore()
    store.createChat()
    store.addMessage('user', 'hi')
    store.clearMessages()
    expect(store.messages).toHaveLength(0)
  })

  it('sendMessage streams tokens into assistant message', async () => {
    configureSettings()
    const store = useChatStore()
    store.createChat()
    expect(store.needsProvider).toBe(false)
    expect(store.streaming).toBe(false)
    expect(store.activeChat).not.toBeNull()
    await store.sendMessage('Hello')
    expect(store.messages.length).toBe(2)
    const assistant = store.messages.find((message) => message.role === 'assistant')
    expect(assistant?.content).toBe('Hello world')
    expect(store.streaming).toBe(false)
  })

  it('needsProvider is true when health reports no provider', () => {
    const settings = useSettingsStore()
    settings.health = { status: 'no_provider', provider: 'none', mockMode: false }
    const store = useChatStore()
    expect(store.needsProvider).toBe(true)
  })
})
