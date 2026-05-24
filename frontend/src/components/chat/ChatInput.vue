<template>
  <div class="inp-zone">
    <div class="inp-wrap">
      <textarea
        ref="ta"
        v-model="text"
        class="inp-ta"
        placeholder="Напишите сообщение..."
        rows="1"
        @keydown.enter.exact.prevent="submit"
        @keydown.enter.shift.exact="newline"
        @input="autoResize"
      />
      <div class="inp-acts">
        <button class="ia-btn" title="Прикрепить файл" @click="emit('attach')">📎</button>
        <button
          class="tune-btn"
          :class="{ on: tuneOpen }"
          data-tip="Тонкая настройка"
          title=""
          @click="emit('toggleTune')"
        >⚙</button>
        <button
          class="snd"
          :class="{ stop: streaming }"
          :title="streaming ? 'Остановить' : 'Отправить'"
          @click="streaming ? emit('stop') : submit()"
        >
          {{ streaming ? '■' : '↑' }}
        </button>
      </div>
    </div>
    <div class="inp-hint">Enter — отправить · Shift+Enter — перенос строки</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ streaming: boolean; tuneOpen: boolean }>()
const emit = defineEmits<{
  send: [text: string]
  stop: []
  attach: []
  toggleTune: []
}>()

const text = ref('')
const ta = ref<HTMLTextAreaElement | null>(null)

function submit() {
  const t = text.value.trim()
  if (!t) return
  emit('send', t)
  text.value = ''
  if (ta.value) { ta.value.style.height = 'auto' }
}

function newline() {
  text.value += '\n'
}

function autoResize() {
  if (!ta.value) return
  ta.value.style.height = 'auto'
  ta.value.style.height = Math.min(ta.value.scrollHeight, 200) + 'px'
}
</script>

<style scoped>
.inp-zone {
  padding: 12px 16px 14px; border-top: 1px solid var(--brd);
  background: rgba(255,255,255,0.02); flex-shrink: 0;
}
.inp-wrap {
  display: flex; align-items: flex-end; gap: 8px;
  background: var(--bg-g); border: 1px solid var(--brd);
  border-radius: var(--r); padding: 8px 10px;
  transition: border-color .15s;
}
.inp-wrap:focus-within { border-color: var(--brd-a); }

.inp-ta {
  flex: 1; background: none; border: none; outline: none; resize: none;
  font-family: inherit; font-size: 13.5px; color: var(--t1);
  line-height: 1.5; min-height: 24px; max-height: 200px;
  scrollbar-width: thin;
}
.inp-ta::placeholder { color: var(--t3); }

.inp-acts { display: flex; align-items: center; gap: 5px; flex-shrink: 0; }

.ia-btn {
  width: 28px; height: 28px; border-radius: 8px;
  background: var(--bg-s); border: 1px solid var(--brd);
  color: var(--t2); font-size: 13px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .14s;
}
.ia-btn:hover { color: var(--t1); border-color: var(--brd-a); background: var(--bg-gh); }

.tune-btn {
  position: relative; width: 28px; height: 28px; border-radius: 8px;
  background: var(--bg-s); border: 1px solid var(--brd);
  color: var(--t2); font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all .14s; flex-shrink: 0;
}
.tune-btn:hover { color: var(--t1); border-color: var(--brd-a); background: var(--bg-gh); }
.tune-btn.on { color: var(--accent-l); border-color: rgba(99,102,241,0.5); background: rgba(99,102,241,0.1); }
.tune-btn::after {
  content: attr(data-tip);
  position: absolute; bottom: calc(100% + 6px); left: 50%; transform: translateX(-50%);
  background: var(--bg-panel); border: 1px solid var(--brd); border-radius: 6px;
  padding: 4px 9px; font-size: 11px; color: var(--t1); white-space: nowrap;
  pointer-events: none; opacity: 0; transition: opacity .15s;
}
.tune-btn:hover::after { opacity: 1; }

.snd {
  width: 30px; height: 30px; border-radius: 9px;
  background: var(--accent); border: none; color: #fff;
  font-size: 14px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s; flex-shrink: 0;
}
.snd:hover { background: var(--accent-l); }
.snd.stop { background: rgba(239,68,68,0.8); }
.snd.stop:hover { background: #ef4444; }

.inp-hint { font-size: 10px; color: var(--t3); margin-top: 6px; text-align: center; }
</style>
