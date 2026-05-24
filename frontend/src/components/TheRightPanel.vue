<template>
  <Transition name="rp">
    <aside v-if="open" class="rp">
      <div class="rp-header">
        <div class="rp-title">Тонкая настройка</div>
        <button class="rp-close" @click="emit('close')">✕</button>
      </div>

      <!-- Context toggle -->
      <div class="rp-block">
        <div class="rp-t">Контекст</div>
        <div class="ctx-row">
          <div class="ctx-label">
            Помнить историю чата
            <small>ИИ учитывает предыдущие сообщения</small>
          </div>
          <label class="tog">
            <input v-model="params.useContext" type="checkbox">
            <span class="tog-sl" />
          </label>
        </div>
        <div v-if="params.useContext" class="sl-g">
          <div class="sl-row">
            <div class="sl-label">🧠 Глубина памяти<span class="sl-hint">Сообщений в контексте</span></div>
            <span class="sl-val">{{ params.contextDepth }}</span>
          </div>
          <input v-model.number="params.contextDepth" type="range" min="2" max="40" step="2">
        </div>
      </div>

      <!-- System prompt -->
      <div class="rp-block">
        <div class="rp-t">Системный промпт</div>
        <div class="rp-hint">Задаёт роль и поведение ИИ для этого чата</div>
        <div class="sys-ta-wrapper">
          <textarea
            v-model="params.systemPrompt"
            class="sys-ta"
            placeholder="Например: Отвечай только фактами, без домыслов..."
            @focus="showPresets = true"
            @blur="hidePresets"
          />
          <Transition name="preset-dropdown">
            <div v-if="showPresets" class="preset-dropdown-list">
              <div
                v-for="p in presets"
                :key="p.label"
                class="preset-item"
                @mousedown="selectPreset(p)"
              >
                <span class="preset-icon">{{ p.icon }}</span>
                <span class="preset-label">{{ p.label }}</span>
              </div>
            </div>
          </Transition>
        </div>
        <div class="preset-hint">Начните вводить — появятся быстрые пресеты</div>
      </div>

      <!-- Params -->
      <div class="rp-block">
        <div class="rp-t">Параметры ответа</div>
        <div class="sl-g">
          <div class="sl-row">
            <div class="sl-label">🎨 Креативность<span class="sl-hint">0 = точно, 2 = творчески</span></div>
            <span class="sl-val">{{ params.temperature.toFixed(1) }}</span>
          </div>
          <input v-model.number="params.temperature" type="range" min="0" max="2" step="0.1">
        </div>
        <div class="sl-g">
          <div class="sl-row">
            <div class="sl-label">📏 Длина ответа<span class="sl-hint">Максимум токенов</span></div>
            <span class="sl-val">{{ params.maxTokens }}</span>
          </div>
          <input v-model.number="params.maxTokens" type="range" min="256" max="8192" step="256">
        </div>
      </div>
    </aside>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { storeToRefs } from 'pinia'
import { usePresets } from '@/composables/usePresets'

defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()

const chatStore = useChatStore()
const { params } = storeToRefs(chatStore)
const showPresets = ref(false)
const { presets, loadRecentPresets, saveRecentPreset } = usePresets()

function selectPreset(preset: { icon: string; label: string; text: string }) {
  params.value.systemPrompt = preset.text
  saveRecentPreset(preset)
  showPresets.value = false
}

function hidePresets() {
  setTimeout(() => {
    showPresets.value = false
  }, 200)
}

onMounted(() => {
  loadRecentPresets()
})
</script>

<style scoped>
.rp {
  width: var(--rw); flex-shrink: 0;
  background: var(--bg-g); backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border-left: 1px solid var(--brd);
  display: flex; flex-direction: column;
  overflow-y: auto; overflow-x: hidden;
  scrollbar-width: thin;
}
.rp-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px 10px; border-bottom: 1px solid var(--brd); flex-shrink: 0;
}
.rp-title { font-size: 12px; font-weight: 600; color: var(--t1); }
.rp-close {
  background: var(--bg-s); border: 1px solid var(--brd); color: var(--t2);
  font-size: 13px; cursor: pointer; padding: 4px 7px; border-radius: 6px; line-height: 1;
  transition: all .15s;
}
.rp-close:hover { color: #ef4444; border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.08); }

.rp-block {
  padding: 12px 14px; border-bottom: 1px solid var(--brd);
  display: flex; flex-direction: column; gap: 8px;
}
.rp-t { font-size: 10px; font-weight: 600; color: var(--t3); text-transform: uppercase; letter-spacing: 1px; }
.sys-ta-wrapper { position: relative; }
.sys-ta {
  width: 100%; min-height: 80px; padding: 8px 10px;
  background: var(--bg-s); border: 1px solid var(--brd); border-radius: var(--rs);
  color: var(--t1); font-size: 12px; font-family: inherit; resize: vertical;
  transition: border-color .15s;
}
.sys-ta:focus { border-color: var(--brd-a); outline: none; }
.sys-ta::placeholder { color: var(--t3); }

.preset-dropdown-list {
  position: absolute; top: 100%; left: 0; right: 0;
  z-index: 100; margin-top: 4px;
  background: var(--bg-panel); border: 1px solid var(--brd); border-radius: var(--rs);
  box-shadow: var(--shadow-pop); max-height: 200px; overflow-y: auto;
}
.preset-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; cursor: pointer; transition: background .15s;
}
.preset-item:hover { background: var(--bg-gh); }
.preset-icon { font-size: 14px; }
.preset-label { font-size: 12px; color: var(--t1); }

.preset-dropdown-enter-active, .preset-dropdown-leave-active {
  transition: all .2s ease;
}
.preset-dropdown-enter-from {
  opacity: 0; transform: translateY(-8px);
}
.preset-dropdown-leave-to {
  opacity: 0; transform: translateY(-8px);
}

.rp-hint { font-size: 11px; color: var(--t3); }

.ctx-row { display: flex; align-items: center; justify-content: space-between; }
.ctx-label { font-size: 12px; color: var(--t2); }
.ctx-label small { display: block; font-size: 10px; color: var(--t3); margin-top: 1px; }

.tog { position: relative; width: 36px; height: 20px; flex-shrink: 0; }
.tog input { opacity: 0; width: 0; height: 0; }
.tog-sl {
  position: absolute; inset: 0; background: var(--bg-g); border: 1px solid var(--brd);
  border-radius: 20px; cursor: pointer; transition: background .2s, border-color .2s;
}
.tog-sl::before {
  content: ''; position: absolute; width: 14px; height: 14px; border-radius: 50%;
  background: var(--t3); left: 2px; top: 2px; transition: transform .2s, background .2s;
}
.tog input:checked + .tog-sl { background: rgba(99,102,241,0.25); border-color: rgba(99,102,241,0.5); }
.tog input:checked + .tog-sl::before { transform: translateX(16px); background: var(--accent-l); }

.sys-ta {
  width: 100%; min-height: 72px; padding: 8px 10px;
  background: var(--bg-s); border: 1px solid var(--brd); border-radius: var(--rs);
  color: var(--t1); font-size: 12px; font-family: inherit; resize: vertical;
  outline: none; transition: border-color .15s;
}
.sys-ta:focus { border-color: var(--brd-a); }
.sys-ta::placeholder { color: var(--t3); }

.preset-hint { font-size: 10px; color: var(--t3); font-style: italic; }

.sl-g { display: flex; flex-direction: column; gap: 4px; }
.sl-row { display: flex; align-items: center; justify-content: space-between; }
.sl-label { font-size: 11px; color: var(--t2); display: flex; flex-direction: column; gap: 1px; }
.sl-hint { font-size: 10px; color: var(--t3); }
.sl-val { font-size: 11px; color: var(--accent-l); font-weight: 600; }
input[type=range] { width: 100%; accent-color: var(--accent); }

.rp-enter-active, .rp-leave-active { transition: width .2s ease, opacity .2s ease; overflow: hidden; }
.rp-enter-from, .rp-leave-to { width: 0 !important; opacity: 0; }
</style>
