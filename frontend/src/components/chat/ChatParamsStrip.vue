<template>
  <div class="params-strip">
    <div class="ps-chip" :title="tips.temperature" @click="emit('openParams')">
      <b>{{ t('params_strip.creativity') }}</b> {{ params.temperature.toFixed(1) }}<span class="tip">(?)</span>
    </div>
    <div class="ps-chip" :title="tips.maxTokens" @click="emit('openParams')">
      <b>{{ t('params_strip.response_length') }}</b> {{ t('common.tokens', { count: params.maxTokens }) }}
    </div>
    <div class="ps-chip" :title="tips.topP" @click="emit('openParams')">
      <b>{{ t('params_strip.word_diversity') }}</b> {{ params.topP.toFixed(1) }}
    </div>
    <div class="ps-chip" :title="tips.context">
      <b>{{ t('params_strip.chat_memory') }}</b> {{ params.useContext ? t('common.on') : t('common.off') }}
    </div>
    <div class="ps-chip ps-chip--stream" :title="tips.streaming">
      <b>{{ t('params_strip.streaming') }}</b> {{ t('common.on') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ChatParams } from '@/types'
import { useI18n } from '@/composables/useI18n'

defineProps<{ params: ChatParams }>()
const emit = defineEmits<{ openParams: [] }>()
const { t } = useI18n()

const tips = computed(() => ({
  temperature: t('params_strip.tip_temperature'),
  maxTokens: t('params_strip.tip_max_tokens'),
  topP: t('params_strip.tip_top_p'),
  context: t('params_strip.tip_context'),
  streaming: t('params_strip.tip_streaming'),
}))
</script>

<style scoped>
.params-strip {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 16px; border-bottom: 1px solid var(--brd);
  background: var(--topbar-bg);
  overflow-x: auto; scrollbar-width: none; flex-shrink: 0;
}
.params-strip::-webkit-scrollbar { display: none; }

.ps-chip {
  display: flex; align-items: center; gap: 4px;
  padding: 3px 9px; border-radius: 20px;
  border: 1px solid var(--brd); background: var(--bg-s);
  font-size: 11px; color: var(--t2); white-space: nowrap;
  cursor: pointer; transition: all .14s; user-select: none;
}
.ps-chip:hover { border-color: var(--brd-a); color: var(--t1); background: var(--bg-gh); }
.ps-chip b { font-weight: 500; color: var(--t1); }
.ps-chip--stream { cursor: default; }
.ps-chip--stream:hover { border-color: var(--brd); color: var(--t2); background: var(--bg-s); }
.tip { color: var(--t3); font-size: 10px; margin-left: 2px; }
</style>
