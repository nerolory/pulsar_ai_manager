import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { nanoid } from 'nanoid'
import type { Chat, ChatMessage, ChatParams } from '@/types'
import { streamChat, buildStreamRequest } from '@/api/chat'
import { listChats, createChat as apiCreateChat, saveChat, renameChat as apiRenameChat, addMessageToChat, reorderChats as apiReorderChats, clearChatMessages, deleteChat as apiDeleteChat, getChatMessages } from '@/api/chats'
import { useSettingsStore } from '@/stores/settings'

const DEFAULT_PARAMS: ChatParams = {
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
    () => chats.value.find((c) => c.id === activeChatId.value) ?? null,
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
    apiCreateChat(title, chat.id).catch(err => {
      console.error('Failed to save chat to backend:', err)
    })

    return chat
  }

  function selectChat(id: string) {
    console.log('[Chat] selectChat:', id, 'previous:', activeChatId.value)
    activeChatId.value = id
    console.log('[Chat] selectChat set to:', activeChatId.value)
  }

  async function deleteChat(id: string) {
    // Remove from localStorage immediately
    chats.value = chats.value.filter((c) => c.id !== id)
    if (activeChatId.value === id) {
      activeChatId.value = chats.value[0]?.id ?? null
    }
    
    // Delete from SQLite as backup (async, non-blocking)
    apiDeleteChat(id).catch(err => {
      console.error('Failed to delete chat from backend:', err)
    })
    
    // Auto-create new chat if all chats are deleted
    if (chats.value.length === 0) {
      await createChat()
      // Small delay to ensure UI updates focus
      await new Promise(resolve => setTimeout(resolve, 0))
    }
  }

  function renameChat(id: string, title: string) {
    const chat = chats.value.find((c) => c.id === id)
    if (!chat || !title.trim()) return
    chat.title = title.trim()
    apiRenameChat(id, title.trim()).catch(err => console.error('[Chat] failed to rename:', err))
  }

  function reorderChat(fromId: string, toId: string) {
    const fromIdx = chats.value.findIndex((c) => c.id === fromId)
    const toIdx = chats.value.findIndex((c) => c.id === toId)
    if (fromIdx === -1 || toIdx === -1) return
    const updated = [...chats.value]
    const [removed] = updated.splice(fromIdx, 1)
    updated.splice(toIdx, 0, removed)
    chats.value = updated
    apiReorderChats(updated.map((c) => c.id)).catch(err => console.error('[Chat] failed to reorder:', err))
  }

  function clearMessages() {
    if (!activeChat.value) return
    activeChat.value.messages = []
    activeChat.value.updatedAt = Date.now()
    clearChatMessages(activeChat.value.id).catch(err => console.error('[Chat] failed to clear messages:', err))
  }

  function addMessage(role: ChatMessage['role'], content: string, model?: string): ChatMessage {
    if (!activeChat.value) {
      throw new Error('No active chat - sendMessage should create chat first')
    }
    const msg: ChatMessage = {
      id: nanoid(),
      role,
      content,
      createdAt: Date.now(),
      model,
    }
    activeChat.value.messages.push(msg)
    activeChat.value.updatedAt = Date.now()
    // auto-title from first user message
    if (role === 'user' && activeChat.value.messages.filter((m) => m.role === 'user').length === 1) {
      const words = content.trim().split(/\s+/)
      const titleWords = words.slice(0, 3).join(' ')
      activeChat.value.title = titleWords + (words.length > 3 ? '...' : '')
      apiRenameChat(activeChat.value.id, activeChat.value.title).catch(err => console.error('[Chat] failed to save title:', err))
    }
    return msg
  }

  async function sendMessage(userText: string) {
    if (streaming.value || !userText.trim()) return
    if (needsProvider.value) return
    error.value = null
    console.info('[Chat] sendMessage:', userText.slice(0, 60))

    if (!activeChat.value) {
      await createChat()
      // Small delay to ensure UI updates
      await new Promise(resolve => setTimeout(resolve, 0))
    }

    // Build context BEFORE mutating messages
    const historyMessages = params.value.useContext
      ? messages.value.filter((m) => m.role !== 'system').slice(-params.value.contextDepth)
      : []

    const request = buildStreamRequest(
      [...historyMessages, { id: '', role: 'user', content: userText, createdAt: Date.now() }],
      params.value,
    )

    const currentModel = settingsStore.health?.model ?? settingsStore.activeModel ?? settingsStore.activeProvider ?? ''
    abortController = new AbortController()
    streaming.value = true
    const userMsg = addMessage('user', userText)
    const assistantMsg = addMessage('assistant', '', currentModel)
    assistantMsg.createdAt = userMsg.createdAt + 1

    // Save user message immediately (incremental — no DELETE/INSERT)
    if (activeChatId.value) {
      addMessageToChat(activeChatId.value, userMsg).catch(err => console.error('[Chat] failed to save user msg:', err))
    }

    const MAX_RETRIES = 3
    let attempt = 0
    let lastError: Error | null = null

    while (attempt < MAX_RETRIES) {
      attempt++
      assistantMsg.content = ''
      lastError = null

      console.log(`[Chat] attempt ${attempt}/${MAX_RETRIES}`)

      let succeeded = false
      await new Promise<void>((resolve) => {
        streamChat(
          request,
          (token) => { assistantMsg.content += token },
          () => {
            console.info('[Chat] streaming done, total length:', assistantMsg.content.length)
            succeeded = true
            resolve()
          },
          (err) => {
            if (err.name === 'AbortError') {
              succeeded = true // user stopped intentionally
            } else {
              console.error(`[Chat] attempt ${attempt} error:`, err.message)
              lastError = err
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
          addMessageToChat(activeChatId.value, assistantMsg).catch(err => console.error('[Chat] failed to save assistant msg:', err))
        }
        return
      }

      if (attempt < MAX_RETRIES) {
        console.info(`[Chat] retrying in 1s... (${attempt}/${MAX_RETRIES})`)
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
      addMessageToChat(activeChatId.value, assistantMsg).catch(err => console.error('[Chat] failed to save error msg:', err))
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
          if (!activeChatId.value || !chatList.find(c => c.id === activeChatId.value)) {
            activeChatId.value = chatList[0].id
          }
          // Load messages for active chat
          const messages = await getChatMessages(activeChatId.value, 10)
          console.log('[Store loadChats] messages after getChatMessages:', messages.map(m => `${m.role}@${m.createdAt}`))
          const chatIndex = chats.value.findIndex(c => c.id === activeChatId.value)
          if (chatIndex !== -1) {
            chats.value[chatIndex].messages = messages
          }
        }
      } catch (err) {
        console.error('Failed to load chats from backend:', err)
        // Don't fallback to localStorage - show error instead
        error.value = 'Failed to load chats from server'
      }
    } catch (err) {
      error.value = 'Не удалось загрузить чаты'
      console.error('Failed to load chats:', err)
    } finally {
      loading.value = false
    }
  }

  async function loadMoreMessages(before: number) {
    if (!activeChatId.value) return
    try {
      const messages = await getChatMessages(activeChatId.value, 10, before)
      console.log('[Store loadMoreMessages] messages after getChatMessages:', messages.map(m => `${m.role}@${m.createdAt}`))
      if (messages.length > 0) {
        const chatIndex = chats.value.findIndex(c => c.id === activeChatId.value)
        if (chatIndex !== -1) {
          chats.value[chatIndex].messages = [...messages, ...chats.value[chatIndex].messages]
        }
      }
    } catch (err) {
      console.error('Failed to load more messages:', err)
    }
  }

  async function saveChatToBackend() {
    if (!activeChat.value) return
    try {
      await saveChat(activeChat.value)
    } catch (err) {
      console.error('Failed to save chat:', err)
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
    saveChatToBackend,
  }
})
