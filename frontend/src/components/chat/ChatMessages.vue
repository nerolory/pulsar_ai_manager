<template>
  <div ref="container" class="msgs" data-v="typing-test-123" :style="{ fontSize: (fontSize ?? 14) + 'px' }">
    <div v-if="healthLoaded && needsProvider" class="no-provider-banner">
      <div class="npb-icon">⚙️</div>
      <div class="npb-text">
        <b>Провайдер не настроен</b>
        <span>Перейдите в <b>Настройки → Провайдеры ИИ</b> и подключите один из сервисов (VseLLM, OpenRouter или Mock для тестирования).</span>
      </div>
      <button class="npb-btn" @click="emit('openSettings')">Открыть настройки</button>
    </div>

    <div v-else-if="!messages.length" class="msgs-empty">
      <div class="empty-icon">✦</div>
      <div class="empty-title">Чем могу помочь?</div>
      <div class="empty-sub">Напишите вопрос или выберите чат из истории</div>
    </div>

    <div
      v-for="msg in messages"
      :key="msg.id"
      :data-msg-id="msg.id"
      class="msg"
      :class="msg.role === 'user' ? 'u' : 'a'"
    >
      <div class="mav" :class="msg.role === 'user' ? 'user' : 'ai'">
        {{ msg.role === 'user' ? 'U' : '✦' }}
      </div>
      <div class="mc">
        <div class="mm">
          <span class="mn" :class="msg.role === 'user' ? 'u' : 'ai'">
            {{ msg.role === 'user' ? 'Вы' : ('Ответ от ' + (msg.model || 'AI')) }}
          </span>
          <span class="mt">{{ formatTime(msg.createdAt) }}</span>
        </div>
        <div v-if="isProviderError(msg)" class="bub bub--hint">
          <span class="hint-icon">⚙️</span>
          <span>Провайдер не настроен. Перейдите в
            <button class="hint-link" @click="emit('openSettings')">Настройки → Провайдеры ИИ</button>
            и подключите один из сервисов.</span>
        </div>
        <div v-else-if="msg.role === 'assistant' && isLast(msg.id) && !msg.content" class="bub">
          <div class="typing"><div class="td" /><div class="td" /><div class="td" /></div>
        </div>
        <div v-else class="bub" v-html="renderContent(msg.content)" />
        <div v-if="msg.role === 'assistant' && streaming && isLast(msg.id) && msg.content" class="cursor-blink" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import type { ChatMessage } from '@/types'
import { useMarkdown } from '@/composables/useMarkdown'

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
const isInitialLoad = ref(true)
const isLoadingMore = ref(false)
const hasMoreMessages = ref(true)
const isProgrammaticScroll = ref(false)

const PROVIDER_ERROR_PATTERNS = [
  'No provider configured',
  'no_provider',
]

function isProviderError(msg: ChatMessage): boolean {
  if (msg.role !== 'assistant') return false
  return PROVIDER_ERROR_PATTERNS.some((p) => msg.content.includes(p))
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
</script>

<style scoped>
.msgs {
  flex: 1; overflow-y: auto; padding: 20px 32px;
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
</style>
