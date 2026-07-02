/**
 * Type re-exports for backward compatibility.
 *
 * New code should import from specific submodules:
 *   import type { ChatMessage, Chat } from '@/types/chat'
 *   import type { ProviderConfig, ModelInfo } from '@/types/provider'
 */

export type {
  MessageRole,
  ContentImageUrl,
  ContentPart,
  MessageContent,
  ChatMessage,
  Chat,
  ChatParams,
  StreamChunk,
} from './chat'

export type {
  ProviderName,
  ProviderConfig,
  ProviderCapabilities,
  ModelInfo,
  HealthStatus,
} from './provider'

export type { LocaleData } from './i18n'
