<template>
  <div class="chat-layout">
    <ChatTopbar
      :title="chatStore.activeChat?.title ?? 'PulsarAI'"
      :subtitle="subtitle"
      :health="settingsStore.health"
      @clear-chat="chatStore.clearMessages()"
      @open-settings="emit('openSettings')"
    />
    <ChatParamsStrip :params="chatStore.params" @open-params="tuneOpen = true" />
    <div class="msgs-wrap">
      <div class="zoom-controls">
        <button class="zoom-btn zoom-btn--out" title="Уменьшить текст" @click="changeFontSize(-1)">−</button>
        <button class="zoom-btn zoom-btn--in" title="Увеличить текст" @click="changeFontSize(1)">+</button>
      </div>
      <ChatMessages
        :messages="chatStore.messages"
        :streaming="chatStore.streaming"
        :needs-provider="chatStore.needsProvider"
        :health-loaded="settingsStore.health !== null"
        :font-size="fontSize"
        @open-settings="emit('openSettings')"
        @load-more="chatStore.loadMoreMessages"
      />
    </div>
    <ChatInput
      :streaming="chatStore.streaming"
      :tune-open="tuneOpen"
      @send="chatStore.sendMessage"
      @stop="chatStore.stopStreaming"
      @toggle-tune="tuneOpen = !tuneOpen"
      @attach="showToast('📎', 'Файл', 'Вставьте файл или изображение')"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useSettingsStore } from '@/stores/settings'
import { useToast } from '@/composables/useToast'
import ChatTopbar from '@/components/chat/ChatTopbar.vue'
import ChatParamsStrip from '@/components/chat/ChatParamsStrip.vue'
import ChatMessages from '@/components/chat/ChatMessages.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

const chatStore = useChatStore()
const settingsStore = useSettingsStore()
const { show: showToast } = useToast()

const props = defineProps<{ tuneOpen: boolean }>()
const emit = defineEmits<{
  'update:tuneOpen': [val: boolean]
  'openSettings': []
}>()
const tuneOpen = computed({
  get: () => props.tuneOpen,
  set: (v) => emit('update:tuneOpen', v),
})

const fontSize = ref(14)
function changeFontSize(delta: number) {
  fontSize.value = Math.min(22, Math.max(10, fontSize.value + delta))
}

const subtitle = computed(() => {
  const count = chatStore.messages.length
  const ctx = chatStore.params.useContext ? 'Контекстный режим' : 'Без контекста'
  return `${ctx} · ${count} сообщений`
})

watch(() => chatStore.error, (err) => {
  if (err) showToast('⚠️', 'Ошибка', err)
})

onMounted(async () => {
  await settingsStore.loadProviderConfig()
  await chatStore.loadChats()
  if (!chatStore.activeChat) chatStore.createChat()
})
</script>

<style scoped>
.chat-layout {
  flex: 1; display: flex; flex-direction: column; overflow: hidden;
}
.msgs-wrap {
  flex: 1; position: relative; overflow: hidden; display: flex; flex-direction: column;
}
.zoom-controls {
  position: absolute; top: 12px; right: 16px; z-index: 20;
  display: flex; align-items: stretch;
  border: 1px solid rgba(255,255,255,0.15); border-radius: 8px;
  background: rgba(20,20,35,0.75);
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 10px rgba(0,0,0,0.4);
}
.zoom-btn {
  width: 40px; height: 30px;
  background: transparent; border: none;
  color: var(--t1); font-size: 17px; font-weight: 500;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background .15s, color .15s;
}
.zoom-btn:first-child { border-radius: 7px 0 0 7px; border-right: 1px solid rgba(255,255,255,0.12); }
.zoom-btn:last-child  { border-radius: 0 7px 7px 0; }
.zoom-btn:hover { background: rgba(255,255,255,0.1); }
</style>
