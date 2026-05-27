import { api } from './apiService'
import type { Chat, ChatMessage } from '@/types'

export interface ChatResponse {
  id: string
  title: string
  createdAt: number
  updatedAt: number
}

export interface MessageResponse {
  id: string
  role: string
  content: string
  createdAt: number
  model?: string
  rowid?: number
}

export async function listChats(): Promise<Chat[]> {
  const responseData = await api.get<ChatResponse[]>('/chats')
  if (!responseData) return []
  return responseData.map(chat => ({
    id: chat.id,
    title: chat.title,
    messages: [],
    createdAt: chat.createdAt,
    updatedAt: chat.updatedAt
  }))
}

export async function getChatMessages(
  chatId: string, 
  limit?: number, 
  before?: number
): Promise<ChatMessage[]> {
  const params = new URLSearchParams()
  if (limit !== undefined) params.append('limit', limit.toString())
  if (before !== undefined) params.append('before', before.toString())
  
  const responseData = await api.get<MessageResponse[]>(`/chats/${chatId}/messages?${params}`)
  return responseData.map(message => ({
    id: message.id,
    role: message.role as ChatMessage['role'],
    content: message.content,
    createdAt: message.createdAt,
    model: message.model,
    rowid: message.rowid,
  }))
}

export async function createChat(title: string, id?: string): Promise<Chat> {
  const responseData = await api.post<ChatResponse>('/chats', { title, id })
  if (!responseData) {
    throw new Error('Failed to create chat: No response data')
  }
  return {
    id: responseData.id,
    title: responseData.title,
    messages: [],
    createdAt: responseData.createdAt,
    updatedAt: responseData.updatedAt
  }
}

export async function addMessageToChat(chatId: string, message: ChatMessage): Promise<void> {
  await api.post(`/chats/${chatId}/messages`, {
    id: message.id,
    role: message.role,
    content: message.content,
    createdAt: message.createdAt,
    model: message.model ?? null,
  })
}

export async function renameChat(chatId: string, title: string): Promise<void> {
  await api.patch(`/chats/${chatId}`, { title })
}

export async function saveChat(chat: Chat): Promise<void> {
  await api.put(`/chats/${chat.id}`, {
    id: chat.id,
    title: chat.title,
    messages: chat.messages
  })
}

export async function reorderChats(ids: string[]): Promise<void> {
  await api.post('/chats/reorder', { ids })
}

export async function clearChatMessages(chatId: string): Promise<void> {
  await api.delete(`/chats/${chatId}/messages`)
}

export async function deleteChat(chatId: string): Promise<void> {
  await api.delete(`/chats/${chatId}`)
}
