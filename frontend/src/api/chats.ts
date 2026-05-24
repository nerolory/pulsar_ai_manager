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

export async function listChats(): Promise<ChatResponse[]> {
  const data = await api.get<ChatResponse[]>('/chats')
  if (!data) return []
  return data.map(chat => ({
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
): Promise<MessageResponse[]> {
  const params = new URLSearchParams()
  if (limit !== undefined) params.append('limit', limit.toString())
  if (before !== undefined) params.append('before', before.toString())
  
  const data = await api.get<MessageResponse[]>(`/chats/${chatId}/messages?${params}`)
  console.log(`[API getChatMessages] chatId=${chatId} limit=${limit} before=${before} raw order:`, data.map(m => `${m.role}@${m.createdAt}`))
  return data.map(msg => ({
    id: msg.id,
    role: msg.role as 'user' | 'assistant' | 'system',
    content: msg.content,
    createdAt: msg.createdAt,
    model: msg.model,
    rowid: msg.rowid,
  }))
}

export async function createChat(title: string, id?: string): Promise<ChatResponse> {
  const data = await api.post<ChatResponse>('/chats', { title, id })
  if (!data) {
    throw new Error('Failed to create chat: No response data')
  }
  return {
    id: data.id,
    title: data.title,
    messages: [],
    createdAt: data.createdAt,
    updatedAt: data.updatedAt
  }
}

export async function addMessageToChat(chatId: string, msg: ChatMessage): Promise<void> {
  await api.post(`/chats/${chatId}/messages`, {
    id: msg.id,
    role: msg.role,
    content: msg.content,
    createdAt: msg.createdAt,
    model: msg.model ?? null,
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
