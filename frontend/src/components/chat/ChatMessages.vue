<template>
  <div ref="container" class="msgs" :class="`msgs--fs-${fontSize ?? 14}`" @click="handleMsgsClick">
    <div v-if="healthLoaded && needsProvider" class="no-provider-banner">
      <div class="npb-icon">⚙️</div>
      <div class="npb-text">
        <b>Провайдер не настроен</b>
        <span>Перейдите в <b>Настройки → Провайдеры ИИ</b> и подключите один из сервисов (VseLLM, OpenRouter или Mock для тестирования).</span>
      </div>
      <button class="npb-btn" @click="emit('openSettings')">Открыть настройки</button>
    </div>

    <div v-else-if="!messages.length" class="msgs-empty">
      <div class="empty-icon">◉</div>
      <div class="empty-title">Чем могу помочь?</div>
      <div class="empty-sub">Напишите вопрос или выберите чат из истории</div>
    </div>

    <div
      v-for="message in messages"
      :key="message.id"
      :data-msg-id="message.id"
      class="msg"
      :class="message.role === 'user' ? 'u' : 'a'"
    >
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
        <div v-if="isProviderError(message)" class="bub bub--hint">
          <span class="hint-icon">⚙️</span>
          <span>Провайдер не настроен. Перейдите в
            <button class="hint-link" @click="emit('openSettings')">Настройки → Провайдеры ИИ</button>
            и подключите один из сервисов.</span>
        </div>
        <div v-else-if="isBalanceError(message)" class="bub bub--hint bub--balance">
          <span class="hint-icon">💰</span>
          <span>{{ message.content }}</span>
          <button v-if="message.rowid" class="hint-btn" @click="switchToFreeModel(message.rowid)">Переключиться</button>
          <button class="hint-link" @click="emit('openSettings')">Пополнить баланс</button>
        </div>
        <div v-else-if="message.role === 'assistant' && isLast(message.id) && !message.content" class="bub">
          <div class="typing"><div class="td" /><div class="td" /><div class="td" /></div>
        </div>
        <div v-else class="bub">
          <div v-for="(part, partIndex) in getImageParts(message.content)" :key="partIndex" class="msg-img">
            <img :src="part.image_url!.url" />
          </div>
          <span v-if="getTextContent(message.content)" v-html="renderContent(getTextContent(message.content))" />
        </div>
        <div v-if="message.role === 'assistant' && streaming && isLast(message.id) && message.content" class="cursor-blink" />
        <div v-if="message.role === 'assistant' && !streaming && message.content && ttsSupported" class="msg-actions">
          <button
            class="msg-act-btn"
            :class="{ active: speakingMessageId === message.id }"
            :title="speakingMessageId === message.id ? 'Остановить' : 'Прочитать вслух'"
            @click="toggleSpeak(message)"
          >
            <svg v-if="speakingMessageId !== message.id" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import type { ChatMessage, ContentPart, MessageContent } from '@/types'
import { useMarkdown } from '@/composables/useMarkdown'
import { switchModel } from '@/api/settings'
import { useSettingsStore } from '@/stores/settings'
import { useTTS } from '@/composables/useVoice'

const props = defineProps<{
  messages: ChatMessage[]
  streaming: boolean
  needsProvider: boolean
  healthLoaded: boolean
  fontSize?: number
}>()
const emit = defineEmits<{ openSettings: []; loadMore: [before: number] }>()

const container = ref<HTMLElement | null>(null)
const { render: renderContent } = useMarkdown()
const settingsStore = useSettingsStore()
const { speak, stop: stopTTS, isSpeaking, isSupported: ttsSupported } = useTTS()
const speakingMessageId = ref<string | null>(null)

function toggleSpeak(message: ChatMessage) {
  const text = getTextContent(message.content)
  if (!text) return
  if (speakingMessageId.value === message.id) {
    stopTTS()
    speakingMessageId.value = null
  } else {
    stopTTS()
    speakingMessageId.value = message.id
    speak(text)
    const unsub = watch(isSpeaking, (val) => {
      if (!val) { speakingMessageId.value = null; unsub() }
    })
  }
}
const isLoadingMore = ref(false)
const hasMoreMessages = ref(true)
const isProgrammaticScroll = ref(false)

const PROVIDER_ERROR_PATTERNS = [
  'No provider configured',
  'no_provider',
]

const BALANCE_ERROR_PATTERNS = [
  'balance-error-',
]

function isProviderError(message: ChatMessage): boolean {
  return PROVIDER_ERROR_PATTERNS.some(pattern => 
    message.content?.toLowerCase().includes(pattern.toLowerCase())
  )
}

function isBalanceError(message: ChatMessage): boolean {
  return BALANCE_ERROR_PATTERNS.some(pattern => 
    message.id?.startsWith(pattern)
  )
}

async function switchToFreeModel(modelId: string) {
  try {
    await switchModel(modelId)
    await settingsStore.loadAllSettings()
    // Reload page or refresh UI to reflect the change
    window.location.reload()
  } catch (error) {
    console.error('Failed to switch model:', error)
  }
}

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

function isLast(id: string): boolean {
  return props.messages.at(-1)?.id === id
}

watch(
  () => props.messages.length,
  async () => {
    if (isLoadingMore.value) return
    await nextTick()
    if (!container.value) return

    const lastMsg = props.messages.at(-1)
    if (!lastMsg) return

    isProgrammaticScroll.value = true
    if (lastMsg.role === 'assistant') {
      const el = container.value.querySelector(`[data-msg-id="${lastMsg.id}"]`) as HTMLElement | null
      if (el) {
        el.scrollIntoView({ block: 'start', behavior: 'smooth' })
      }
    } else {
      container.value.scrollTop = container.value.scrollHeight
    }
    setTimeout(() => { isProgrammaticScroll.value = false }, 600)
  },
)

// Infinite scroll up handler
async function handleScroll() {
  if (!container.value || isLoadingMore.value || !hasMoreMessages.value || isProgrammaticScroll.value) return

  if (container.value.scrollTop < 100) {
    const oldestMsg = props.messages[0]
    const before = oldestMsg?.rowid
    if (!before) return // no rowid = nothing to paginate

    isLoadingMore.value = true
    const prevCount = props.messages.length
    try {
      emit('loadMore', before)
      await new Promise(resolve => setTimeout(resolve, 400))
      if (props.messages.length <= prevCount) {
        hasMoreMessages.value = false
      }
    } catch (error) {
      console.error('Failed to load more messages:', error)
    } finally {
      isLoadingMore.value = false
    }
  }
}

// Add scroll listener and initial scroll
onMounted(() => {
  if (container.value) {
    container.value.addEventListener('scroll', handleScroll, { passive: true })
    // Start at bottom
    nextTick(() => {
      container.value!.scrollTop = container.value!.scrollHeight
    })
  }
})

onUnmounted(() => {
  if (container.value) {
    container.value.removeEventListener('scroll', handleScroll)
  }
})

function handleMsgsClick(e: MouseEvent) {
  const btn = (e.target as HTMLElement).closest('.code-copy')
  if (!btn) return
  const codeEl = btn.closest('.code-block')?.querySelector('code')
  if (codeEl) {
    navigator.clipboard.writeText((codeEl as HTMLElement).innerText)
  }
}
</script>

<style scoped>
.msgs {
  flex: 1; overflow-y: auto; padding: 20px 32px 20px 32px;
  padding-top: 52px;
  display: flex; flex-direction: column; gap: 16px;
  scrollbar-width: thin; scrollbar-color: var(--brd) transparent;
  position: relative;
}
.no-provider-banner {
  display: flex; align-items: flex-start; gap: 14px;
  margin: 24px; padding: 16px 18px;
  border-radius: var(--r);
  background: rgba(99, 102, 241, 0.07);
  border: 1px solid var(--accent-border);
}
.npb-icon { font-size: 22px; flex-shrink: 0; margin-top: 1px; }
.npb-text {
  flex: 1; display: flex; flex-direction: column; gap: 5px;
}
.npb-text b { font-size: 0.93em; font-weight: 600; color: var(--t1); }
.npb-text span { font-size: 0.86em; color: var(--t2); line-height: 1.5; }
.npb-btn {
  flex-shrink: 0; align-self: center;
  padding: 6px 14px; border-radius: var(--rs);
  background: var(--accent); border: none;
  color: #fff; font-size: 0.86em; font-weight: 500;
  cursor: pointer; white-space: nowrap; transition: background .15s;
}
.npb-btn:hover { background: var(--accent-l); }

.msgs-empty {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 10px;
  color: var(--t3); text-align: center; padding: 60px 0;
}
.empty-icon { font-size: 2.57em; opacity: 0.3; }
.empty-title { font-size: 1.14em; font-weight: 600; color: var(--t2); }
.empty-sub { font-size: 0.86em; }

.msgs { font-size: 14px; }
.msgs--fs-12 { font-size: 12px; }
.msgs--fs-13 { font-size: 13px; }
.msgs--fs-14 { font-size: 14px; }
.msgs--fs-15 { font-size: 15px; }
.msgs--fs-16 { font-size: 16px; }
.msgs--fs-18 { font-size: 18px; }
.msgs--fs-20 { font-size: 20px; }
.msg { display: flex; gap: 10px; max-width: 780px; }
.msg.u { flex-direction: row-reverse; margin-left: auto; }
.msg.a { margin-right: auto; }

.mav {
  width: 2.14em; height: 2.14em; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.93em; font-weight: 700;
}
.mav.ai {
  background: linear-gradient(135deg, var(--accent), #8B5CF6);
  color: #fff; font-size: 0.79em;
  box-shadow: 0 0 12px rgba(99,102,241,0.4);
}
.mav.user { background: var(--bg-gh); color: var(--t2); border: 1px solid var(--brd); }

.mc { display: flex; flex-direction: column; gap: 4px; min-width: 0; }

.mm { display: flex; align-items: center; gap: 6px; }
.mn { font-size: 0.86em; font-weight: 600; }
.mn.ai { color: var(--accent-l); }
.mn.u { color: var(--t2); }
.mt { font-size: 0.71em; color: var(--t3); }

.bub {
  padding: 10px 14px; border-radius: 12px;
  font-size: 1em; line-height: 1.6; color: var(--t1);
  background: var(--bg-s); border: 1px solid var(--brd);
  word-break: break-word;
}
.msg.u .bub {
  background: var(--accent-dim); border-color: var(--accent-border);
}
.msg.a .bub {
  background: transparent; border: none; padding-left: 0; padding-right: 0;
}

.bub--hint {
  display: flex; align-items: baseline; gap: 7px;
  background: rgba(99, 102, 241, 0.07);
  border-color: var(--accent-border);
  color: var(--t2); font-size: 0.93em; line-height: 1.5;
}
.hint-icon { flex-shrink: 0; font-size: 1em; }
.hint-link {
  background: none; border: none; padding: 0;
  color: var(--accent-l); cursor: pointer; font-size: inherit;
  text-decoration: underline; text-underline-offset: 2px;
  transition: color .14s;
}
.hint-link:hover { color: #fff; }

.msg-img { margin-bottom: 6px; }
.msg-img img {
  max-width: 320px; max-height: 320px;
  border-radius: 8px; border: 1px solid var(--brd);
  display: block; object-fit: contain;
}

.msg-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  opacity: 0;
  transition: opacity .15s;
}
.mc:hover .msg-actions { opacity: 1; }
.msg-act-btn {
  display: flex; align-items: center; justify-content: center;
  width: 24px; height: 24px; border-radius: 6px;
  background: none; border: 1px solid transparent;
  color: var(--t3); cursor: pointer; transition: all .14s;
}
.msg-act-btn:hover { color: var(--t1); border-color: var(--brd); background: var(--bg-s); }
.msg-act-btn.active { color: var(--accent-l); border-color: rgba(99,102,241,0.4); background: rgba(99,102,241,0.1); }

.cursor-blink {
  display: inline-block; width: 2px; height: 1em;
  background: var(--accent-l); margin-left: 2px; vertical-align: middle;
  animation: blink .7s step-end infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

.typing { display: flex; gap: 4px; padding: 3px 0; }
.td { width: 6px; height: 6px; border-radius: 50%; background: var(--accent-l); opacity: .4; animation: tp 1.2s infinite; }
.td:nth-child(2) { animation-delay: .2s; }
.td:nth-child(3) { animation-delay: .4s; }
@keyframes tp { 0%,60%,100% { opacity:.4; transform:translateY(0) } 30% { opacity:1; transform:translateY(-4px) } }

/* ── Responsive styles ──────────────────────────── */

/* Legacy desktop / laptops (1024px - 1440px) */
@media (max-width: 1440px) {
  .msgs { padding: 16px 12px; }
  .msg { gap: 8px; }
}

/* Tablet (768px - 1024px) */
@media (max-width: 1024px) {
  .msgs { padding: 14px 10px; }
  .mav { width: 2em; height: 2em; }
  .bub { padding: 8px 12px; }
}

/* Mobile (< 768px) */
@media (max-width: 768px) {
  .msgs {
    padding: 12px 8px;
    max-width: 100%;
  }

  .no-provider-banner {
    margin: 8px;
    padding: 12px;
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }

  .npb-btn {
    width: 100%;
    justify-content: center;
  }

  .msg { gap: 6px; }
  .msg.u { margin-left: 20px; }
  .msg.a { margin-right: 20px; }

  .mav {
    width: 1.86em;
    height: 1.86em;
    font-size: 0.86em;
  }

  .bub {
    padding: 8px 10px;
    border-radius: 10px;
  }

  .mm { gap: 4px; }
  .mn { font-size: 0.79em; }
  .mt { font-size: 0.64em; }
}

/* Small mobile (< 480px) */
@media (max-width: 480px) {
  .msgs { padding: 10px 6px; }
  .msg.u { margin-left: 10px; }
  .msg.a { margin-right: 10px; }
  .mav { display: none; }
  .bub { padding: 10px 8px 6px; font-size: 0.93em; }
}

/* Mobile landscape */
@media (max-width: 768px) and (orientation: landscape) {
  .msgs { padding: 10px 16px; }
  .mav { display: flex; }
}

/* Touch devices */
@media (hover: none) and (pointer: coarse) {
  .bub { min-height: 44px; }
  .hint-link { min-height: 44px; padding: 8px 12px; }
}

/* Old monitors 4:3 and 5:4 - more compact layout */
@media (min-aspect-ratio: 4/3) and (max-aspect-ratio: 16/10) {
  .msgs { padding: 12px 16px; }
  .msg { max-width: 680px; }
}

/* Limited height screens */
@media (max-height: 900px) {
  .msgs { padding: 10px 12px; }
  .msg-img img { max-height: 200px; }
}
</style>
