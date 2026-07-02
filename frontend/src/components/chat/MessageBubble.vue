<template>
  <div :data-msg-id="message.id" class="message" :class="message.role === 'user' ? 'message--user' : 'message--assistant'">
    <div class="message__avatar" :class="message.role === 'user' ? 'message__avatar--user' : 'message__avatar--assistant'">
      {{ message.role === 'user' ? 'U' : '◉' }}
    </div>
    <div class="message__content" @contextmenu="onContextMenu">
      <div class="message__meta">
        <span class="message__name" :class="message.role === 'user' ? 'message__name--user' : 'message__name--assistant'">
          {{ message.role === 'user' ? t('message.you') : (t('message.response_from') + ' ' + (message.model || t('message.ai'))) }}
        </span>
        <span class="message__time">{{ formatTime(message.createdAt) }}</span>
      </div>

      <!-- Provider not configured hint -->
      <div v-if="isProviderError" class="message__bubble message__bubble--hint">
        <span class="message__hint-icon">⚙️</span>
        <span>{{ t('chat_messages.provider_error') }}</span>
      </div>

      <!-- Balance error with switch suggestion -->
      <div v-else-if="isBalanceError" class="message__bubble message__bubble--hint message__bubble--balance">
        <span class="message__hint-icon">💰</span>
        <span>{{ textContent }}</span>
        <button v-if="message.freeModelId" class="message__hint-btn" @click="emit('switchModel', message.freeModelId)">{{ t('chat_messages.switch_to_free') }}</button>
        <button class="message__hint-link" @click="emit('openSettings')">{{ t('chat_messages.replenish_balance') }}</button>
      </div>

      <!-- Typing indicator -->
      <div v-else-if="message.role === 'assistant' && isLast && !message.content" class="message__bubble">
        <div class="message__typing"><div class="message__typing-dot" /><div class="message__typing-dot" /><div class="message__typing-dot" /></div>
      </div>

      <!-- Normal message content -->
      <div v-else class="message__bubble">
        <div v-for="(part, idx) in imageParts" :key="idx" class="message__image">
          <img :src="part.image_url!.url" />
        </div>
        <span v-if="textContent" v-html="renderedContent" />
      </div>

      <!-- Streaming cursor -->
      <div v-if="message.role === 'assistant' && streaming && isLast && message.content" class="message__cursor" />

      <!-- TTS action -->
      <div v-if="showTtsButton" class="message__actions">
        <button
          class="message__action-btn"
          :class="{ 'message__action-btn--active': isSpeaking }"
          :title="isSpeaking ? t('message.stop_reading') : t('message.read_aloud')"
          @click="emit('toggleSpeak', message.id)"
        >
          <svg v-if="!isSpeaking" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
          </svg>
          <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="6" y="4" width="4" height="16"/>
            <rect x="14" y="4" width="4" height="16"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage, ContentPart, MessageContent } from '@/types'
import { useMarkdown } from '@/composables/useMarkdown'
import { useI18n } from '@/composables/useI18n'
import { useContextMenuProvider } from '@/composables/useContextMenu'

const props = defineProps<{
  message: ChatMessage
  streaming: boolean
  isLast: boolean
  isSpeaking: boolean
  ttsSupported: boolean
}>()

const emit = defineEmits<{
  openSettings: []
  switchModel: [modelId: string]
  toggleSpeak: [messageId: string]
}>()

const { render } = useMarkdown()
const { t } = useI18n()
const { handleContextMenuEvent } = useContextMenuProvider()

function onContextMenu(event: MouseEvent) {
  handleContextMenuEvent(event, 'readonly', event.currentTarget as HTMLElement)
}

const PROVIDER_ERROR_PATTERNS = ['No provider configured', 'no_provider']
const BALANCE_ERROR_PREFIX = 'balance-error-'

const textContent = computed(() => getTextContent(props.message.content))
const imageParts = computed(() => getImageParts(props.message.content))
const renderedContent = computed(() => render(textContent.value))

const isProviderError = computed(() =>
  PROVIDER_ERROR_PATTERNS.some(p =>
    String(props.message.content).toLowerCase().includes(p.toLowerCase())
  )
)

const isBalanceError = computed(() =>
  props.message.id?.startsWith(BALANCE_ERROR_PREFIX)
)

const showTtsButton = computed(() =>
  props.message.role === 'assistant' &&
  !props.streaming &&
  !!props.message.content &&
  props.ttsSupported
)

function getTextContent(content: MessageContent): string {
  if (typeof content === 'string') return content
  return content.filter(part => part.type === 'text').map(part => part.text ?? '').join(' ')
}

function getImageParts(content: MessageContent): ContentPart[] {
  if (typeof content === 'string') return []
  return content.filter(part => part.type === 'image_url')
}

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' })
}
</script>
