<template>
  <div class="params-strip">
    <div class="ps-chip" :title="tips.temperature" @click="emit('openParams')">
      <b>Креативность</b> {{ params.temperature.toFixed(1) }}<span class="tip">(?)</span>
    </div>
    <div class="ps-chip" :title="tips.maxTokens" @click="emit('openParams')">
      <b>Длина ответа</b> {{ params.maxTokens }} токенов
    </div>
    <div class="ps-chip" :title="tips.topP" @click="emit('openParams')">
      <b>Разнообразие слов</b> {{ params.topP.toFixed(1) }}
    </div>
    <div class="ps-chip" :title="tips.context">
      <b>Память чата</b> {{ params.useContext ? 'ВКЛ' : 'ВЫКЛ' }}
    </div>
    <div class="ps-chip ps-chip--stream" title="Ответ появляется постепенно, как набор текста">
      <b>Потоковый вывод</b> ВКЛ
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatParams } from '@/types'

defineProps<{ params: ChatParams }>()
const emit = defineEmits<{ openParams: [] }>()

const tips = {
  temperature: 'Креативность — насколько непредсказуемы ответы. 0 = точно по теме, 2 = очень творчески',
  maxTokens:   'Длина ответа — максимальное количество слов в одном ответе',
  topP:        'Разнообразие слов — насколько широко ИИ выбирает слова. Выше = разнообразнее',
  context:     'Память чата — использовать ли историю предыдущих сообщений',
}
</script>

<style scoped>
.params-strip {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 16px; border-bottom: 1px solid var(--brd);
  background: rgba(255,255,255,0.015);
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
