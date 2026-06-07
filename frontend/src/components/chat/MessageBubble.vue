<template>
  <div :data-msg-id="message.id" class="msg" :class="message.role === 'user' ? 'u' : 'a'">
    <div class="mav" :class="message.role === 'user' ? 'user' : 'ai'">
      {{ message.role === 'user' ? 'U' : '◉' }}
    </div>
    <div class="mc">
      <div class="mm">
        <span class="mn" :class="message.role === 'user' ? 'u' : 'ai'">
          {{ message.role === 'user' ? 'Вы' : ('Ответ от ' + (message.model || 'AI')) }}
        </span>
        <span class="mt">{{ formatTime(message.createdAt) }}</span>
      </div>

      <!-- Provider not configured hint -->
      <div v-if="isProviderError" class="bub bub--hint">
        <span class="hint-icon">⚙️</span>
        <span>Провайдер не настроен. Перейдите в
          <button class="hint-link" @click="emit('openSettings')">Настройки → Провайдеры ИИ</button>
          и подключите один из сервисов.</span>
      </div>

      <!-- Balance error with switch suggestion -->
      <div v-else-if="isBalanceError" class="bub bub--hint bub--balance">
        <span class="hint-icon">💰</span>
        <span>{{ textContent }}</span>
        <button v-if="message.freeModelId" class="hint-btn" @click="emit('switchModel', message.freeModelId)">Переключиться</button>
        <button class="hint-link" @click="emit('openSettings')">Пополнить баланс</button>
      </div>

      <!-- Typing indicator -->
      <div v-else-if="message.role === 'assistant' && isLast && !message.content" class="bub">
        <div class="typing"><div class="td" /><div class="td" /><div class="td" /></div>
      </div>

      <!-- Normal message content -->
      <div v-else class="bub">
        <div v-for="(part, idx) in imageParts" :key="idx" class="msg-img">
          <img :src="part.image_url!.url" />
        </div>
        <span v-if="textContent" v-html="renderedContent" />
      </div>

      <!-- Streaming cursor -->
      <div v-if="message.role === 'assistant' && streaming && isLast && message.content" class="cursor-blink" />

      <!-- TTS action -->
      <div v-if="showTtsButton" class="msg-actions">
        <button
          class="msg-act-btn"
          :class="{ active: isSpeaking }"
          :title="isSpeaking ? 'Остановить' : 'Прочитать вслух'"
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
