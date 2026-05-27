import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { nanoid } from 'nanoid'
import type { Chat, ChatMessage, ChatParams, ContentPart, MessageContent } from '@/types'
import { streamChat, buildStreamRequest } from '@/api/chat'
import { listChats, createChat as apiCreateChat, renameChat as apiRenameChat, addMessageToChat, reorderChats as apiReorderChats, clearChatMessages, deleteChat as apiDeleteChat, getChatMessages } from '@/api/chats'
import { useSettingsStore } from '@/stores/settings'

const DEFAULT_PARAMS: ChatParams = { // v2

  temperature: 0.7,
  maxTokens: 4096,
  topP: 0.9,
  systemPrompt: '',
  useContext: true,
  contextDepth: 10,
}

export const useChatStore = defineStore('chat', () => {
  const chats = ref<Chat[]>([])
  const activeChatId = ref<string | null>(null)
  const params = ref<ChatParams>({ ...DEFAULT_PARAMS })
  const streaming = ref(false)
  const error = ref<string | null>(null)
  const loading = ref(false)

  let abortController: AbortController | null = null

  const settingsStore = useSettingsStore()
  const needsProvider = computed(() => !settingsStore.isConfigured)

  // ── Computed ──────────────────────────────────────
  const activeChat = computed<Chat | null>(
    () => chats.value.find((chat) => chat.id === activeChatId.value) ?? null,
  )

  const messages = computed<ChatMessage[]>(
    () => activeChat.value?.messages ?? [],
  )

  // ── Actions ───────────────────────────────────────
  function createChat(title = 'Новый чат'): Chat {
    const chat: Chat = {
      id: nanoid(),
      title,
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    }
    chats.value.unshift(chat)
    selectChat(chat.id)

    // Save to backend with same id — no id swap needed
    apiCreateChat(title, chat.id).catch(error => {
      console.error('Failed to save chat to backend:', error)
    })

    return chat
  }

  async function selectChat(id: string) {
    activeChatId.value = id
    const chat = chats.value.find(chat => chat.id === id)
    if (chat && chat.messages.length === 0) {
      try {
        const messages = await getChatMessages(id, 10)
        chat.messages = messages
      } catch (error) {
        console.error('[Chat] failed to load messages for chat:', id, error)
      }
    }
  }

  async function deleteChat(id: string) {
    // Remove from localStorage immediately
    chats.value = chats.value.filter((chat) => chat.id !== id)
    if (activeChatId.value === id) {
      const nextId = chats.value[0]?.id ?? null
      if (nextId) await selectChat(nextId)
      else activeChatId.value = null
    }
    
    // Delete from SQLite as backup (async, non-blocking)
    apiDeleteChat(id).catch(error => {
      console.error('Failed to delete chat from backend:', error)
    })
    
    // Auto-create new chat if all chats are deleted
    if (chats.value.length === 0) {
      await createChat()
      // Small delay to ensure UI updates focus
      await new Promise(resolve => setTimeout(resolve, 0))
    }
  }

  function renameChat(id: string, title: string) {
    const chat = chats.value.find((chat) => chat.id === id)
    if (!chat || !title.trim()) return
    chat.title = title.trim()
    apiRenameChat(id, title.trim()).catch(error => console.error('[Chat] failed to rename:', error))
  }

  function reorderChat(fromId: string, toId: string) {
    const fromIndex = chats.value.findIndex((chat) => chat.id === fromId)
    const toIndex = chats.value.findIndex((chat) => chat.id === toId)
    if (fromIndex === -1 || toIndex === -1) return
    const updated = [...chats.value]
    const [removed] = updated.splice(fromIndex, 1)
    updated.splice(toIndex, 0, removed)
    chats.value = updated
    apiReorderChats(updated.map((chat) => chat.id)).catch(error => console.error('[Chat] failed to reorder:', error))
  }

  function clearMessages() {
    if (!activeChat.value) return
    activeChat.value.messages = []
    activeChat.value.updatedAt = Date.now()
    clearChatMessages(activeChat.value.id).catch(error => console.error('[Chat] failed to clear messages:', error))
  }

  function addMessage(role: ChatMessage['role'], content: MessageContent, model?: string): ChatMessage {
    if (!activeChat.value) {
      throw new Error('No active chat - sendMessage should create chat first')
    }
    const message: ChatMessage = {
      id: nanoid(),
      role,
      content,
      createdAt: Date.now(),
      model,
    }
    activeChat.value.messages.push(message)
    activeChat.value.updatedAt = Date.now()
    // auto-title from first user message
    if (role === 'user' && activeChat.value.messages.filter((msg) => msg.role === 'user').length === 1) {
      const textContent = typeof content === 'string' ? content : (content.find(part => part.type === 'text')?.text ?? '📷 Изображение')
      const words = textContent.trim().split(/\s+/)
      const titleWords = words.slice(0, 3).join(' ')
      activeChat.value.title = (titleWords || '📷 Изображение') + (words.length > 3 ? '...' : '')
      apiRenameChat(activeChat.value.id, activeChat.value.title).catch(error => console.error('[Chat] failed to save title:', error))
    }
    return message
  }

  async function sendMessage(userText: string, imageParts?: ContentPart[]) {
    const hasImages = imageParts && imageParts.length > 0
    if (streaming.value || (!userText.trim() && !hasImages)) return
    if (needsProvider.value) return
    error.value = null

    if (!activeChat.value) {
      await createChat()
      await new Promise(resolve => setTimeout(resolve, 0))
    }

    const userContent: MessageContent = hasImages ? imageParts! : userText

    // Build context BEFORE mutating messages
    const historyMessages = params.value.useContext
      ? messages.value.filter((msg) => msg.role !== 'system').slice(-params.value.contextDepth)
      : []

    const request = buildStreamRequest(
      [...historyMessages, { id: '', role: 'user', content: userContent, createdAt: Date.now() }],
      params.value,
    )

    const currentModel = settingsStore.health?.model ?? settingsStore.activeModel ?? settingsStore.activeProvider ?? ''
    abortController = new AbortController()
    streaming.value = true
    const userMsg = addMessage('user', userContent)
    const assistantMsg = addMessage('assistant', '', currentModel)
    assistantMsg.createdAt = userMsg.createdAt + 1

    // Save user message immediately (incremental — no DELETE/INSERT)
    if (activeChatId.value) {
      addMessageToChat(activeChatId.value, userMsg).catch(error => console.error('[Chat] failed to save user msg:', error))
    }

    const MAX_RETRIES = 3
    let attempt = 0
    let lastError: Error | null = null

    while (attempt < MAX_RETRIES) {
      attempt++
      assistantMsg.content = ''
      lastError = null

      let succeeded = false
      await new Promise<void>((resolve) => {
        streamChat(
          request,
          (token) => { assistantMsg.content += token },
          () => {
            succeeded = true
            resolve()
          },
          (error) => {
            if (error.name === 'AbortError') {
              succeeded = true // user stopped intentionally
            } else {
              console.error(`[Chat] attempt ${attempt} error:`, error.message)
              lastError = error
            }
            resolve()
          },
          abortController!.signal,
        )
      })

      if (succeeded) {
        streaming.value = false
        abortController = null
        // Save completed assistant message incrementally
        if (activeChatId.value) {
          addMessageToChat(activeChatId.value, assistantMsg).catch(error => console.error('[Chat] failed to save assistant msg:', error))
        }
        return
      }

      if (attempt < MAX_RETRIES) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        abortController = new AbortController()
      }
    }

    // All attempts failed
    const modelName = currentModel || 'AI-модель'
    assistantMsg.content = `Сервис «${modelName}» сейчас недоступен. Попробуйте позже или выберите другой сервис в настройках.`
    console.error('[Chat] all retries failed:', (lastError as Error | null)?.message)
    streaming.value = false
    abortController = null
    if (activeChatId.value) {
      addMessageToChat(activeChatId.value, assistantMsg).catch(error => console.error('[Chat] failed to save error msg:', error))
    }
  }

  function stopStreaming() {
    abortController?.abort()
    streaming.value = false
  }

  async function loadChats() {
    try {
      loading.value = true
      
      // Load from backend as primary source
      try {
        const chatList = await listChats()
        chats.value = chatList
        if (chatList.length > 0) {
          // Set active chat if not set or invalid
          if (!activeChatId.value || !chatList.find(chat => chat.id === activeChatId.value)) {
            activeChatId.value = chatList[0].id
          }
          // Load messages for active chat
          const messages = await getChatMessages(activeChatId.value, 10)
          const chatIndex = chats.value.findIndex(chat => chat.id === activeChatId.value)
          if (chatIndex !== -1) {
            chats.value[chatIndex].messages = messages
          }
        }
      } catch (error) {
        console.error('Failed to load chats from backend:', error)
        // Don't fallback to localStorage - show error instead
        error.value = 'Failed to load chats from server'
      }
    } catch (error) {
      error.value = 'Не удалось загрузить чаты'
      console.error('Failed to load chats:', error)
    } finally {
      loading.value = false
    }
  }

  async function loadMoreMessages(before: number) {
    if (!activeChatId.value) return
    try {
      const messages = await getChatMessages(activeChatId.value, 10, before)
      if (messages.length > 0) {
        const chatIndex = chats.value.findIndex(chat => chat.id === activeChatId.value)
        if (chatIndex !== -1) {
          chats.value[chatIndex].messages = [...messages, ...chats.value[chatIndex].messages]
        }
      }
    } catch (error) {
      console.error('Failed to load more messages:', error)
    }
  }

  return {
    chats,
    activeChatId,
    activeChat,
    messages,
    params,
    streaming,
    error,
    loading,
    needsProvider,
    createChat,
    selectChat,
    deleteChat,
    renameChat,
    reorderChat,
    clearMessages,
    addMessage,
    sendMessage,
    stopStreaming,
    loadChats,
    loadMoreMessages,
  }
})
