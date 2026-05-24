<template>
  <div class="settings-page">
    <!-- Topbar -->
    <div class="topbar">
      <div class="tb-info">
        <div class="tb-title">Настройки</div>
        <div class="tb-sub">Управление приложением и провайдерами</div>
      </div>
      <button class="tb-btn" title="Закрыть" @click="emit('back')">✕</button>
    </div>

    <div class="settings-body">
      <!-- Nav -->
      <nav class="settings-nav">
        <div class="sb-label">Разделы</div>
        <div
          v-for="s in sections" :key="s.id"
          class="sn-item" :class="{ on: activeSection === s.id }"
          @click="activeSection = s.id"
        >
          <span class="sn-icon">{{ s.icon }}</span>{{ s.label }}
        </div>
      </nav>

      <!-- Content -->
      <div class="settings-content">

        <!-- Providers -->
        <template v-if="activeSection === 'providers'">
          <div class="s-section">
            <div class="s-section-title">🤖 Подключённые провайдеры ИИ</div>
            <div class="info-box">
              Провайдер — это сервис, который предоставляет модель ИИ.
              Выберите провайдера и введите API-ключ.
            </div>
            <div class="provider-list">
              <div
                v-for="p in providers" :key="p.id"
                class="prov-row"
                :class="{ connected: settingsStore.activeProvider === p.id }"
              >
                <div class="prov-dot" :class="{ active: settingsStore.activeProvider === p.id }" />
                <div class="prov-info">
                  <div class="prov-name">
                    {{ p.name }}
                    <span class="prov-badge" :class="settingsStore.activeProvider === p.id ? 'ok' : 'off'">
                      {{ settingsStore.activeProvider === p.id ? 'ПОДКЛЮЧЁН' : 'НЕ НАСТРОЕН' }}
                    </span>
                  </div>
                  <div class="prov-desc">{{ p.desc }}</div>
                </div>
                <button
                  class="btn" :class="settingsStore.activeProvider === p.id ? 'btn-secondary' : 'btn-primary'"
                  @click="openSetup(p.id)"
                >
                  {{ settingsStore.activeProvider === p.id ? 'Изменить' : 'Настроить' }}
                </button>
              </div>
            </div>
          </div>
        </template>

        <!-- Chat defaults -->
        <template v-else-if="activeSection === 'chat'">
          <div class="s-section">
            <div class="s-section-title">💬 Параметры чата по умолчанию</div>
            <div class="sl-g">
              <div class="sl-row">
                <div class="sl-label">Креативность ответов<span class="sl-hint">0 = строго · 2 = творчески</span></div>
                <span class="sl-val">{{ chatStore.params.temperature.toFixed(1) }}</span>
              </div>
              <input v-model.number="chatStore.params.temperature" type="range" min="0" max="2" step="0.1">
            </div>
            <div class="sl-g">
              <div class="sl-row">
                <div class="sl-label">Максимальная длина ответа<span class="sl-hint">В токенах</span></div>
                <span class="sl-val">{{ chatStore.params.maxTokens }}</span>
              </div>
              <input v-model.number="chatStore.params.maxTokens" type="range" min="256" max="8192" step="256">
            </div>
          </div>
        </template>

        <template v-else>
          <div class="s-section">
            <div class="s-section-title">{{ sections.find(s => s.id === activeSection)?.icon }} {{ sections.find(s => s.id === activeSection)?.label }}</div>
            <p class="coming-soon">Раздел в разработке</p>
          </div>
        </template>
      </div>
    </div>
  </div>

  <!-- Provider setup modal -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="setupModal.open" class="overlay" @click.self="setupModal.open = false">
        <div class="modal">
          <div class="modal-header">
            <div class="modal-title">Настройка {{ providers.find(p => p.id === setupModal.provider)?.name }}</div>
            <button class="modal-close" @click="setupModal.open = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="field-group">
              <label class="field-label">API-ключ</label>
              <input
                v-model="setupModal.apiKey"
                class="field-input"
                type="password"
                :placeholder="providers.find(p => p.id === setupModal.provider)?.keyPlaceholder ?? 'sk-...'"
              >
            </div>
            <div class="field-group">
              <label class="field-label">Модель (опционально)</label>
              <input
                v-model="setupModal.model"
                class="field-input"
                type="text"
                :placeholder="providers.find(p => p.id === setupModal.provider)?.defaultModel ?? ''"
              >
            </div>
            <div v-if="setupModal.error" class="modal-error">{{ setupModal.error }}</div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="setupModal.open = false">Отмена</button>
            <button class="btn btn-primary" :disabled="settingsStore.loading" @click="saveProvider">
              {{ settingsStore.loading ? 'Подключение...' : 'Сохранить' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useChatStore } from '@/stores/chat'
import { useToast } from '@/composables/useToast'
import { testPrompt } from '@/api/settings'
import type { ProviderName } from '@/types'

const emit = defineEmits<{ back: [] }>()

const settingsStore = useSettingsStore()
const chatStore = useChatStore()
const { show: showToast } = useToast()

const activeSection = ref('providers')

const sections = [
  { id: 'providers', icon: '🤖', label: 'Провайдеры ИИ' },
  { id: 'chat',      icon: '💬', label: 'Чат' },
  { id: 'appearance',icon: '🎨', label: 'Внешний вид' },
  { id: 'privacy',   icon: '🔒', label: 'Приватность' },
]

const providers = [
  { id: 'vsellm',     name: 'VseLLM',         desc: 'GPT-4o, Claude, Gemini и другие · api.vsellm.ru',          keyPlaceholder: 'sk-...',          defaultModel: 'openai/gpt-4o-mini' },
  { id: 'openrouter', name: 'OpenRouter',      desc: 'Qwen3, LLaMA 3.3, Mistral и 200+ моделей · Бесплатные доступны', keyPlaceholder: 'sk-or-v1-...',   defaultModel: 'qwen/qwen3-235b-a22b:free' },
  { id: 'openai',     name: 'OpenAI',          desc: 'GPT-4o, GPT-4.1, o1 — требуется API-ключ',                keyPlaceholder: 'sk-proj-...',     defaultModel: 'gpt-4o-mini' },
  { id: 'mock',       name: 'Mock (тест)',      desc: 'Тестовый провайдер без ключа — для разработки',           keyPlaceholder: '',                defaultModel: '' },
]

const setupModal = reactive({
  open: false,
  provider: 'vsellm' as ProviderName,
  apiKey: '',
  model: '',
  error: '',
})


onMounted(async () => {
  await settingsStore.loadProviderConfig()
})

function openSetup(id: string) {
  setupModal.provider = id as ProviderName
  setupModal.apiKey = ''
  setupModal.model = settingsStore.activeModel ?? providers.find(p => p.id === id)?.defaultModel ?? ''
  setupModal.error = ''
  setupModal.open = true
}

async function saveProvider() {
  setupModal.error = ''
  try {
    await settingsStore.applyProvider({
      provider: setupModal.provider,
      apiKey: setupModal.apiKey || undefined,
      model: setupModal.model || undefined,
    })
    await settingsStore.checkHealth()
    setupModal.open = false
    showToast('✅', 'Провайдер подключён', providers.find(p => p.id === setupModal.provider)?.name ?? '')
    runPromptTest()
  } catch (err) {
    setupModal.error = (err as Error).message
  }
}

async function runPromptTest() {
  showToast('⏳', 'PulsarAI', 'Проверяю поддержку системных промптов...', 8000)
  try {
    const res = await testPrompt()
    if (res.follows_instructions) {
      showToast('✅', 'PulsarAI', 'Модель поддерживает системные промпты', 6000)
    } else {
      showToast('⚠️', 'PulsarAI', `Модель может игнорировать скрипты. Ответ: "${res.model_answer}"`, 8000)
    }
  } catch {
    showToast('❌', 'PulsarAI', 'Не удалось проверить поддержку промптов', 5000)
  }
}
</script>

<style scoped>
.settings-page { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.topbar {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 20px; border-bottom: 1px solid var(--brd);
  background: rgba(255,255,255,0.02); flex-shrink: 0;
}
.tb-info { flex: 1; }
.tb-title { font-size: 14px; font-weight: 600; }
.tb-sub { font-size: 11px; color: var(--t3); margin-top: 1px; }
.tb-btn {
  width: 30px; height: 30px; border-radius: var(--rs);
  background: none; border: 1px solid var(--brd); color: var(--t3);
  font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.tb-btn:hover { color: var(--t1); border-color: var(--brd-a); background: var(--bg-gh); }

.settings-body { flex: 1; display: flex; overflow: hidden; }

.settings-nav {
  width: 200px; flex-shrink: 0; padding: 14px 10px;
  border-right: 1px solid var(--brd); display: flex; flex-direction: column; gap: 2px;
}
.sb-label {
  font-size: 10px; font-weight: 600; color: var(--t3);
  letter-spacing: 1px; text-transform: uppercase; padding: 6px 10px 3px;
}
.sn-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px; border-radius: var(--rs);
  font-size: 12.5px; color: var(--t2); cursor: pointer; transition: all .15s;
}
.sn-item:hover { background: var(--bg-gh); color: var(--t1); }
.sn-item.on { background: var(--accent-dim); color: var(--t1); }
.sn-icon { font-size: 14px; }

.settings-content { flex: 1; overflow-y: auto; padding: 20px; }

.s-section { display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; }
.s-section-title { font-size: 13px; font-weight: 600; color: var(--t1); }
.info-box {
  padding: 10px 12px; border-radius: var(--rs);
  background: var(--accent-dim); border: 1px solid var(--accent-border);
  font-size: 12px; color: var(--t2); line-height: 1.5;
}
.coming-soon { font-size: 13px; color: var(--t3); }

.provider-list { display: flex; flex-direction: column; gap: 6px; }
.prov-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: var(--rs);
  border: 1px solid var(--brd); background: var(--bg-s); transition: border-color .15s;
}
.prov-row.connected { border-color: rgba(52,211,153,0.3); background: rgba(52,211,153,0.05); }
.prov-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--t3); flex-shrink: 0; transition: all .2s;
}
.prov-dot.active { background: #34D399; box-shadow: 0 0 6px rgba(52,211,153,0.5); }
.prov-info { flex: 1; }
.prov-name { font-size: 13px; font-weight: 600; color: var(--t1); display: flex; align-items: center; gap: 6px; }
.prov-badge {
  font-size: 10px; padding: 1px 5px; border-radius: 3px;
}
.prov-badge.ok { background: rgba(52,211,153,0.1); color: #34D399; }
.prov-badge.off { background: rgba(255,255,255,0.06); color: var(--t3); }
.prov-desc { font-size: 11px; color: var(--t3); margin-top: 2px; }

.btn {
  padding: 5px 12px; border-radius: var(--rs); font-size: 11px; font-weight: 500;
  cursor: pointer; border: none; transition: all .15s; white-space: nowrap;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--accent); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--accent-l); }
.btn-secondary { background: var(--bg-gh); color: var(--t2); border: 1px solid var(--brd); }
.btn-secondary:hover { color: var(--t1); border-color: var(--brd-a); }

.sl-g { display: flex; flex-direction: column; gap: 4px; }
.sl-row { display: flex; align-items: center; justify-content: space-between; }
.sl-label { font-size: 12px; color: var(--t2); display: flex; flex-direction: column; gap: 1px; }
.sl-hint { font-size: 10px; color: var(--t3); }
.sl-val { font-size: 12px; color: var(--accent-l); font-weight: 600; }
input[type=range] { width: 100%; accent-color: var(--accent); }

/* Modal */
.overlay {
  position: fixed; inset: 0; z-index: 7000;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
}
.modal {
  width: 420px; border-radius: var(--r);
  background: var(--bg-panel); border: 1px solid var(--brd);
  box-shadow: var(--shadow-pop); overflow: hidden;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; border-bottom: 1px solid var(--brd);
}
.modal-title { font-size: 14px; font-weight: 600; }
.modal-close {
  background: var(--bg-s); border: 1px solid var(--brd); color: var(--t2);
  font-size: 13px; cursor: pointer; padding: 4px 7px; border-radius: 6px; line-height: 1;
  transition: all .15s;
}
.modal-close:hover { color: #ef4444; border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.08); }
.modal-body { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 16px; border-top: 1px solid var(--brd);
}
.modal-error {
  padding: 8px 10px; border-radius: var(--rs);
  background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3);
  color: #fca5a5; font-size: 12px;
}
.field-group { display: flex; flex-direction: column; gap: 5px; }
.field-label { font-size: 11px; color: var(--t2); font-weight: 500; }
.field-input {
  width: 100%; padding: 8px 10px;
  background: var(--bg-s); border: 1px solid var(--brd); border-radius: var(--rs);
  color: var(--t1); font-size: 13px; font-family: inherit; outline: none;
  transition: border-color .15s;
}
.field-input:focus { border-color: var(--brd-a); }
.field-input::placeholder { color: var(--t3); }


.modal-enter-active, .modal-leave-active { transition: opacity .2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .modal, .modal-leave-active .modal { transition: transform .2s ease; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: scale(0.95); }
</style>
