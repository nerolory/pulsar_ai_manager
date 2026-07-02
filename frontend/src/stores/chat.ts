import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { nanoid } from 'nanoid'
import type { Chat, ChatMessage, ChatParams, ContentPart, MessageContent } from '@/types'
import { buildStreamRequest } from '@/api/chat'
import { listChats, createChat as apiCreateChat, renameChat as apiRenameChat, addMessageToChat, reorderChats as apiReorderChats, clearChatMessages, deleteChat as apiDeleteChat, getChatMessages } from '@/api/chats'
import { getModels } from '@/api/settings'
import { useSettingsStore } from '@/stores/settings'
import { useStreamChat } from '@/composables/useStreamChat'
import { useI18n } from '@/composables/useI18n'

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
  const error = ref<string | null>(null)
  const loading = ref(false)

  const settingsStore = useSettingsStore()
  const needsProvider = computed(() => !settingsStore.isConfigured)
  const stream = useStreamChat()
  const streaming = stream.streaming
  const { t } = useI18n()

  // ── Computed ──────────────────────────────────────
  const activeChat = computed<Chat | null>(
    () => chats.value.find((chat) => chat.id === activeChatId.value) ?? null,
  )

  const messages = computed<ChatMessage[]>(
    () => activeChat.value?.messages ?? [],
  )

  // ── Actions ───────────────────────────────────────
  function createChat(title?: string): Chat {
    const chatTitle = title ?? t('chat.new_chat')
    const chat: Chat = {
      id: nanoid(),
      title: chatTitle,
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    }
    chats.value.unshift(chat)
    selectChat(chat.id)

    // Save to backend with same id — no id swap needed
    apiCreateChat(chatTitle, chat.id).catch(error => {
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
        // Avoid overwriting messages added while the network request was in flight
        if (chat.messages.length === 0) {
          chat.messages = messages
        }
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
      const imageLabel = t('common.image')
      const textContent = typeof content === 'string' ? content : (content.find(part => part.type === 'text')?.text ?? imageLabel)
      const words = textContent.trim().split(/\s+/)
      const titleWords = words.slice(0, 3).join(' ')
      activeChat.value.title = (titleWords || imageLabel) + (words.length > 3 ? '...' : '')
      apiRenameChat(activeChat.value.id, activeChat.value.title).catch(error => console.error('[Chat] failed to save title:', error))
    }
    return message
  }

  function removeMessage(messageId: string) {
    if (!activeChat.value) return
    activeChat.value.messages = activeChat.value.messages.filter((msg) => msg.id !== messageId)
  }

  function getMessageText(content: MessageContent): string {
    if (typeof content === 'string') return content.trim()
    return content
      .filter((part) => part.type === 'text' && part.text)
      .map((part) => part.text!)
      .join('\n')
      .trim()
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
    const userMsg = addMessage('user', userContent)
    const assistantMsg = addMessage('assistant', '', currentModel)
    assistantMsg.createdAt = userMsg.createdAt + 1

    // Save user message immediately
    if (activeChatId.value) {
      addMessageToChat(activeChatId.value, userMsg).catch(e => console.error('[Chat] failed to save user msg:', e))
    }

    // Execute streaming with retry via composable
    const result = await stream.execute(request, {
      onToken: (token) => { assistantMsg.content += token },
      onRetry: () => { assistantMsg.content = '' },
    })

    if (result.success) {
      if (result.aborted) {
        if (getMessageText(assistantMsg.content)) {
          persistAssistantMsg(assistantMsg)
        } else {
          removeMessage(assistantMsg.id)
        }
        return
      }
      // Save completed assistant message
      if (activeChatId.value) {
        addMessageToChat(activeChatId.value, assistantMsg).catch(e => console.error('[Chat] failed to save assistant msg:', e))
      }
      return
    }

    // Handle balance errors — suggest free model switch
    if (result.isBalanceError) {
      const freeModel = await findFreeModelAlternative(currentModel)
      if (freeModel) {
        assistantMsg.content = t('chat_messages.insufficient_balance', { model: freeModel.name })
        assistantMsg.id = `balance-error-${nanoid()}`
        assistantMsg.freeModelId = freeModel.id
        persistAssistantMsg(assistantMsg)
        return
      }
    }

    // Generic failure
    const modelName = currentModel || t('message.ai')
    assistantMsg.content = t('chat_messages.service_unavailable', { model: modelName })
    persistAssistantMsg(assistantMsg)
  }

  /** Try to find a free model in the same group as the current one. */
  async function findFreeModelAlternative(currentModelId: string) {
    try {
      const { models } = await getModels()
      const currentModelData = models.find(m => m.id === currentModelId)
      const groupId = currentModelData?.model_group_id
      if (groupId) {
        return models.find(m => m.model_group_id === groupId && m.is_free) ?? null
      }
    } catch (e) {
      console.error('[Chat] failed to find free model:', e)
    }
    return null
  }

  /** Persist assistant message to backend (fire-and-forget). */
  function persistAssistantMsg(msg: ChatMessage) {
    if (activeChatId.value) {
      addMessageToChat(activeChatId.value, msg).catch(e => console.error('[Chat] failed to save msg:', e))
    }
  }

  function stopStreaming() {
    stream.abort()
  }

  async function loadChats() {
    loading.value = true
    try {
      const chatList = await listChats()
      chats.value = chatList
      if (chatList.length > 0) {
        if (!activeChatId.value || !chatList.find(c => c.id === activeChatId.value)) {
          activeChatId.value = chatList[0].id
        }
        const msgs = await getChatMessages(activeChatId.value!, 10)
        const idx = chats.value.findIndex(c => c.id === activeChatId.value)
        if (idx !== -1) chats.value[idx].messages = msgs
      }
    } catch (err) {
      error.value = t('chat_messages.load_chats_failed')
      console.error('Failed to load chats:', err)
    } finally {
      loading.value = false
    }
  }

  async function loadMoreMessages(before: number) {
    if (!activeChatId.value) return
    try {
      const older = await getChatMessages(activeChatId.value, 10, before)
      if (older.length > 0) {
        const idx = chats.value.findIndex(c => c.id === activeChatId.value)
        if (idx !== -1) chats.value[idx].messages = [...older, ...chats.value[idx].messages]
      }
    } catch (err) {
      console.error('Failed to load more messages:', err)
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
