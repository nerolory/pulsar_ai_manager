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
          v-for="section in sections" :key="section.id"
          class="sn-item" :class="{ on: activeSection === section.id }"
          @click="activeSection = section.id"
        >
          <span class="sn-icon">{{ section.icon }}</span>{{ section.label }}
        </div>
      </nav>

      <!-- Content -->
      <div class="settings-content">

        <!-- Providers -->
        <template v-if="activeSection === 'providers'">
          <div class="s-section">
            <div class="s-section-title">🤖 Настройка провайдера ИИ</div>
            <div class="info-box">
              Выберите провайдер, модель и введите API-ключ для подключения.
            </div>

            <!-- Current provider status -->
            <div v-if="settingsStore.activeProvider" class="current-provider">
              <div class="cp-info">
                <div class="cp-label">Провайдер:</div>
                <div class="cp-value">{{ providers?.find(p => p.id === settingsStore.activeProvider)?.name }}</div>
                <div class="cp-balance">Баланс: {{ getProviderBalance(settingsStore.activeProvider) }}</div>
              </div>
              <div class="cp-divider" />
              <div class="cp-info">
                <div class="cp-label">Модель:</div>
                <div class="cp-value">{{ settingsStore.activeModel }}</div>
              </div>
              <button class="btn btn-primary" @click="openSetup()">Изменить</button>
            </div>
            <div v-else class="current-provider">
              <div class="cp-label">Провайдер не настроен</div>
              <button class="btn btn-primary" @click="openSetup()">Настроить</button>
            </div>

            <!-- Capabilities display -->
            <div v-if="settingsStore.capabilities && settingsStore.activeProvider" class="capabilities-section">
              <div class="s-section-title">📋 Возможности провайдера</div>
              <div class="capabilities-grid">
                <div class="cap-item" :class="{ on: settingsStore.capabilities.supports_caching }">
                  <span class="cap-icon">{{ settingsStore.capabilities.supports_caching ? '✅' : '❌' }}</span>
                  <span class="cap-label">Кеширование промптов</span>
                </div>
                <div class="cap-item" :class="{ on: settingsStore.capabilities.supports_images }">
                  <span class="cap-icon">{{ settingsStore.capabilities.supports_images ? '✅' : '❌' }}</span>
                  <span class="cap-label">Изображения</span>
                </div>
                <div class="cap-item" :class="{ on: settingsStore.capabilities.supports_pdf }">
                  <span class="cap-icon">{{ settingsStore.capabilities.supports_pdf ? '✅' : '❌' }}</span>
                  <span class="cap-label">PDF файлы</span>
                </div>
                <div class="cap-item" :class="{ on: settingsStore.capabilities.free_tier_available }">
                  <span class="cap-icon">{{ settingsStore.capabilities.free_tier_available ? '✅' : '❌' }}</span>
                  <span class="cap-label">Бесплатный тариф</span>
                </div>
                <div class="cap-item">
                  <span class="cap-icon">📊</span>
                  <span class="cap-label">Контекст: {{ formatNumber(settingsStore.capabilities.max_context_tokens) }} токенов</span>
                </div>
                <div class="cap-item">
                  <span class="cap-icon">💰</span>
                  <span class="cap-label">Оплата: {{ settingsStore.capabilities.pricing_model === 'per_token' ? 'за токен' : 'за запрос' }}</span>
                </div>
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

        <!-- Appearance -->
        <template v-else-if="activeSection === 'appearance'">
          <div class="s-section">
            <div class="s-section-title">🎨 Тема оформления</div>
            <div class="theme-grid">
              <div
                v-for="theme in themes"
                :key="theme.id"
                class="theme-card"
                :class="{ active: currentTheme.id === theme.id }"
                @click="setTheme(theme.id)"
              >
                <div class="theme-preview" :class="`theme-preview--${theme.id}`">
                  <div class="tp-sidebar">
                    <div class="tp-line" />
                    <div class="tp-line tp-line--active" />
                    <div class="tp-line" />
                  </div>
                  <div class="tp-main">
                    <div class="tp-bubble tp-bubble--ai">
                      <div class="tp-dot" />
                    </div>
                    <div class="tp-bubble tp-bubble--user">
                      <div class="tp-dot" />
                    </div>
                    <div class="tp-input" />
                  </div>
                </div>
                <div class="theme-meta">
                  <div class="theme-name">{{ theme.name }}</div>
                  <div class="theme-desc">{{ theme.description }}</div>
                </div>
                <div v-if="currentTheme.id === theme.id" class="theme-check">✓</div>
              </div>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="s-section">
            <div class="s-section-title">{{ activeSectionMeta?.icon }} {{ activeSectionMeta?.label }}</div>
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
            <div class="modal-title">Настройка провайдера</div>
            <button class="modal-close" @click="setupModal.open = false">✕</button>
          </div>
          <div class="modal-body">
            <!-- Mode toggle -->
            <div class="mode-toggle">
              <button
                class="mode-btn"
                :class="{ active: setupModal.mode === 'simple' }"
                @click="setupModal.mode = 'simple'"
              >
                Простой режим
              </button>
              <button
                class="mode-btn"
                :class="{ active: setupModal.mode === 'manual' }"
                @click="setupModal.mode = 'manual'"
              >
                Ручной ввод
              </button>
            </div>

            <!-- Simple mode -->
            <template v-if="setupModal.mode === 'simple'">
              <!-- Provider selector -->
              <div class="field-group">
                <label class="field-label">Провайдер</label>
                <select
                  v-model="setupModal.provider"
                  class="field-input"
                  @change="onProviderChange"
                >
                  <option value="">Выберите провайдера</option>
                  <option v-for="provider in providers" :key="provider.id" :value="provider.id">
                    {{ provider.name }}
                  </option>
                </select>
              </div>

              <!-- Model selector -->
              <div class="field-group">
                <label class="field-label">Модель</label>
                <div v-if="setupModal.providerModels.length > 1" class="model-select-wrapper">
                  <select
                    v-model="setupModal.model"
                    class="field-input"
                  >
                    <option value="">Выберите модель</option>
                    <option v-for="model in setupModal.providerModels" :key="model.id" :value="model.id">
                      {{ model.name }} {{ model.free_tier ? '(бесплатно)' : '' }}
                    </option>
                  </select>
                  <button
                    class="refresh-models-btn"
                    @click="refreshProviderModels"
                    :disabled="setupModal.loadingModels"
                    title="Обновить список моделей"
                  >
                    🔄
                  </button>
                </div>
                <div v-else-if="setupModal.providerModels.length === 1" class="model-display">
                  {{ setupModal.providerModels[0].name }} {{ setupModal.providerModels[0].free_tier ? '(бесплатно)' : '' }}
                </div>
                <div v-else class="model-display">
                  {{ providers?.find(p => p.id === setupModal.provider)?.modelName || 'Модель по умолчанию' }}
                </div>
                <div v-if="setupModal.modelsSource && setupModal.providerModels.length > 0" class="models-source">
                  Источник: {{ setupModal.modelsSource === 'cache' ? 'кешировано' : 'API' }}
                </div>
              </div>

              <!-- API key -->
              <div class="field-group">
                <label class="field-label">API-ключ</label>
                <div class="password-input-wrapper">
                  <input
                    v-model="setupModal.apiKey"
                    class="field-input"
                    :type="setupModal.showApiKey ? 'text' : 'password'"
                    :disabled="!setupModal.model"
                    :placeholder="providers?.find(provider => provider.id === setupModal.provider)?.keyPlaceholder ?? 'sk-...'"
                  >
                  <button
                    class="toggle-password-btn"
                    @click="setupModal.showApiKey = !setupModal.showApiKey"
                    :disabled="!setupModal.model"
                    type="button"
                  >
                    {{ setupModal.showApiKey ? '🙈' : '👁️' }}
                  </button>
                </div>
              </div>
            </template>

            <!-- Manual mode -->
            <template v-else>
              <!-- Base URL -->
              <div class="field-group">
                <label class="field-label">API адрес (Base URL)</label>
                <input
                  v-model="setupModal.baseUrl"
                  class="field-input"
                  type="text"
                  placeholder="https://api.example.com/v1"
                  @blur="onBaseUrlChange"
                >
                <div v-if="setupModal.providerDetection" class="provider-detection">
                  <span v-if="setupModal.providerDetection.detected" class="detection-success">
                    ✓ Обнаружен: {{ providers.value?.find(p => p.id === setupModal.providerDetection.provider)?.name }}
                  </span>
                  <span v-else-if="setupModal.providerDetection.compatible" class="detection-info">
                    ℹ️ {{ setupModal.providerDetection.message }}
                  </span>
                  <span v-else class="detection-error">
                    ⚠️ Несовместимый провайдер. Укажите OpenAI-совместимый провайдер.
                  </span>
                </div>
              </div>

              <!-- Model -->
              <div class="field-group">
                <label class="field-label">Модель</label>
                <input
                  v-model="setupModal.model"
                  class="field-input"
                  type="text"
                  placeholder="gpt-4o-mini"
                >
              </div>

              <!-- API key -->
              <div class="field-group">
                <label class="field-label">API-ключ</label>
                <div class="password-input-wrapper">
                  <input
                    v-model="setupModal.apiKey"
                    class="field-input"
                    :type="setupModal.showApiKey ? 'text' : 'password'"
                    placeholder="sk-..."
                  >
                  <button
                    class="toggle-password-btn"
                    @click="setupModal.showApiKey = !setupModal.showApiKey"
                    type="button"
                  >
                    {{ setupModal.showApiKey ? '🙈' : '👁️' }}
                  </button>
                </div>
              </div>
            </template>

            <div v-if="setupModal.error" class="modal-error">{{ setupModal.error }}</div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="setupModal.open = false">Отмена</button>
            <button class="btn btn-primary" :disabled="settingsStore.loading || (setupModal.mode === 'simple' ? !setupModal.model : !setupModal.baseUrl || !setupModal.model)" @click="saveProvider">
              {{ settingsStore.loading ? 'Подключение...' : 'Сохранить' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useChatStore } from '@/stores/chat'
import { useToast } from '@/composables/useToast'
import { useTheme } from '@/composables/useTheme'
import { testPrompt, getModels, refreshModels, detectProvider, getBalance } from '@/api/settings'
import type { ProviderName, ModelInfo } from '@/types'

const emit = defineEmits<{ back: [] }>()

const settingsStore = useSettingsStore()
const chatStore = useChatStore()
const { show: showToast } = useToast()
const { themes, currentTheme, setTheme } = useTheme()

const activeSection = ref('providers')
const activeSectionMeta = computed(() => sections.find(section => section.id === activeSection.value))
const providerBalance = ref<string | null>(null)

const sections = [
  { id: 'providers', icon: '🤖', label: 'Провайдеры ИИ' },
  { id: 'chat',      icon: '💬', label: 'Чат' },
  { id: 'appearance',icon: '🎨', label: 'Внешний вид' },
  { id: 'privacy',   icon: '🔒', label: 'Приватность' },
]

const providers = computed(() => {
  const data = settingsStore.providersMetadata.providers || {}
  const result = Object.entries(data).map(([id, meta]) => ({
    id,
    name: meta.name || id,
    desc: meta.desc,
    keyPlaceholder: meta.key_placeholder,
    defaultModel: meta.default_model,
    modelName: meta.model_name || meta.default_model,
  }))
  return result
})

const setupModal = reactive({
  open: false,
  mode: 'simple' as 'simple' | 'manual',
  provider: '' as ProviderName,
  apiKey: '',
  model: '',
  baseUrl: '',
  error: '',
  providerModels: [] as ModelInfo[],
  loadingModels: false,
  modelsSource: 'cache' as 'cache' | 'api',
  detectingProvider: false,
  providerDetection: null as { provider: string | null; detected: boolean; compatible: boolean; message?: string } | null,
  showApiKey: false,
})


onMounted(async () => {
  await settingsStore.loadProvidersMetadata()
  await settingsStore.loadProviderConfig()
  if (settingsStore.activeProvider) {
    await settingsStore.loadCapabilities()
    await settingsStore.loadModels()
  }
})

function openSetup() {
  if (!providers.value || providers.value.length === 0) {
    showToast('⚠️', 'PulsarAI', 'Список провайдеров загружается...', 3000)
    return
  }
  setupModal.mode = 'simple'
  setupModal.provider = settingsStore.activeProvider || ''
  setupModal.apiKey = settingsStore.savedProviders[setupModal.provider]?.api_key ?? ''
  setupModal.model = settingsStore.activeModel || ''
  setupModal.baseUrl = ''
  setupModal.error = ''
  setupModal.providerModels = []
  setupModal.modelsSource = 'cache'
  setupModal.providerDetection = null
  setupModal.open = true

  if (setupModal.provider) {
    onProviderChange()
  }
}

async function onProviderChange() {
  setupModal.providerModels = []
  if (!setupModal.provider) return

  // Update API key for the selected provider
  setupModal.apiKey = settingsStore.savedProviders[setupModal.provider]?.api_key ?? ''

  // Get saved model for this provider
  const savedModel = settingsStore.savedProviders[setupModal.provider]?.model ?? ''

  setupModal.loadingModels = true
  try {
    const response = await getModels(false, setupModal.provider)
    setupModal.providerModels = response.models
    setupModal.modelsSource = response.source

    // Auto-select model based on available models
    if (response.models.length === 1) {
      setupModal.model = response.models[0].id
    } else if (response.models.length === 0) {
      // No models available - use saved model or default
      setupModal.model = savedModel || providers.value?.find(p => p.id === setupModal.provider)?.defaultModel || ''
    } else {
      // Multiple models - use saved model if it exists in the list
      const modelExists = response.models.find(m => m.id === savedModel)
      if (modelExists) {
        setupModal.model = savedModel
      } else {
        setupModal.model = ''
      }
    }
  } catch (error) {
    console.error('Failed to load models:', error)
  } finally {
    setupModal.loadingModels = false
  }
}

async function refreshProviderModels() {
  if (!setupModal.provider) return

  setupModal.loadingModels = true
  try {
    const response = await getModels(true, setupModal.provider)
    setupModal.providerModels = response.models
    setupModal.modelsSource = response.source
    showToast('🔄', 'PulsarAI', 'Список моделей обновлён', 3000)
  } catch (error) {
    showToast('❌', 'PulsarAI', 'Не удалось обновить список моделей', 3000)
  } finally {
    setupModal.loadingModels = false
  }
}

function getProviderBalance(providerId: string): string {
  if (!providerBalance.value) return 'не отслеживается'
  return providerBalance.value
}

async function loadProviderBalance() {
  if (!settingsStore.activeProvider) return
  console.log('Loading balance for provider:', settingsStore.activeProvider)
  try {
    const response = await getBalance()
    console.log('Balance response:', response)
    if (response.balance !== null && response.balance !== undefined) {
      const balance = response.balance
      if (balance.currency === 'USD') {
        providerBalance.value = `$${balance.balance}`
      } else {
        providerBalance.value = `${balance.balance} ${balance.currency}`
      }
    } else {
      providerBalance.value = response.message || 'не отслеживается'
    }
  } catch (error) {
    console.error('Failed to load balance:', error)
    providerBalance.value = 'не отслеживается'
  }
}

async function onBaseUrlChange() {
  if (!setupModal.baseUrl) {
    setupModal.providerDetection = null
    return
  }

  setupModal.detectingProvider = true
  try {
    const result = await detectProvider(setupModal.baseUrl)
    setupModal.providerDetection = result

    // If provider detected, auto-switch to simple mode
    if (result.detected && result.provider) {
      setupModal.provider = result.provider as ProviderName
      setupModal.mode = 'simple'
      await onProviderChange()
    }
  } catch (error) {
    console.error('Failed to detect provider:', error)
  } finally {
    setupModal.detectingProvider = false
  }
}

async function saveProvider() {
  setupModal.error = ''
  try {
    await settingsStore.applyProvider({
      provider: setupModal.mode === 'manual' ? 'openai' as ProviderName : setupModal.provider,
      apiKey: setupModal.apiKey || undefined,
      model: setupModal.model || undefined,
      baseUrl: setupModal.mode === 'manual' ? setupModal.baseUrl : undefined,
    })
    setupModal.open = false
    showToast('✅', 'Провайдер подключён', providers.value?.find(provider => provider.id === setupModal.provider)?.name ?? 'Custom')
    await settingsStore.loadCapabilities()
    await loadProviderBalance()
    runPromptTest()
  } catch (error) {
    setupModal.error = (error as Error).message
  }
}

async function runPromptTest() {
  showToast('⏳', 'PulsarAI', 'Проверяю поддержку системных промптов...', 8000)
  try {
    const response = await testPrompt()
    if (response.follows_instructions) {
      showToast('✅', 'PulsarAI', 'Модель поддерживает системные промпты', 6000)
    } else {
      showToast('⚠️', 'PulsarAI', `Модель может игнорировать скрипты. Ответ: "${response.model_answer}"`, 8000)
    }
  } catch {
    showToast('❌', 'PulsarAI', 'Не удалось проверить поддержку промптов', 5000)
  }
}

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

async function refreshModels() {
  try {
    await settingsStore.refreshModelsList()
    showToast('🔄', 'PulsarAI', 'Список моделей обновлён', 3000)
  } catch {
    showToast('❌', 'PulsarAI', 'Не удалось обновить список моделей', 3000)
  }
}

onMounted(async () => {
  await settingsStore.loadProvidersMetadata()
  await settingsStore.loadProviderConfig()
  if (settingsStore.activeProvider) {
    await settingsStore.loadCapabilities()
    await settingsStore.loadModels()
    await loadProviderBalance()
  }
})

watch(() => settingsStore.activeProvider, async (newProvider) => {
  if (newProvider) {
    providerBalance.value = null
    await loadProviderBalance()
  }
})
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
.modal-close:hover { color: var(--error); border-color: var(--error-dim); background: var(--error-bg); }
.modal-body { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 16px; border-top: 1px solid var(--brd);
}
.modal-error {
  padding: 8px 10px; border-radius: var(--rs);
  background: var(--error-bg); border: 1px solid var(--error-dim);
  color: var(--error); font-size: 12px;
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
.field-input option {
  color: var(--t1);
  background: var(--bg-s);
}

.password-input-wrapper {
  display: flex;
  gap: 8px;
}
.password-input-wrapper .field-input {
  flex: 1;
}
.toggle-password-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--rs);
  background: var(--bg-s);
  border: 1px solid var(--brd);
  color: var(--t2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all .15s;
}
.toggle-password-btn:hover:not(:disabled) {
  background: var(--bg-gh);
  color: var(--t1);
}
.toggle-password-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mode-toggle {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding: 4px;
  background: var(--bg-s);
  border-radius: var(--rs);
  border: 1px solid var(--brd);
}
.mode-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: calc(var(--rs) - 2px);
  background: transparent;
  color: var(--t2);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all .15s;
}
.mode-btn.active {
  background: var(--bg-gh);
  color: var(--t1);
  font-weight: 600;
}
.mode-btn:hover:not(.active) {
  background: var(--bg-gh);
}

.provider-detection {
  margin-top: 6px;
  font-size: 11px;
}
.detection-success {
  color: var(--success);
}
.detection-info {
  color: var(--t2);
}
.detection-error {
  color: var(--error);
}

.current-provider {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: var(--rs);
  background: var(--bg-s);
  border: 1px solid var(--brd);
  margin-top: 16px;
}
.cp-info {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
}
.cp-label {
  font-size: 11px;
  color: var(--t3);
  font-weight: 500;
}
.cp-value {
  font-size: 11px;
  color: var(--t1);
  font-weight: 600;
}
.cp-balance {
  font-size: 11px;
  color: var(--t2);
  font-weight: 400;
}
.cp-divider {
  width: 1px;
  height: 40px;
  background: var(--brd);
}

.model-select-wrapper {
  display: flex;
  gap: 8px;
  align-items: center;
}
.model-select-wrapper select {
  flex: 1;
}
.model-display {
  padding: 8px 10px;
  background: var(--bg-s);
  border: 1px solid var(--brd);
  border-radius: var(--rs);
  color: var(--t1);
  font-size: 13px;
}
.refresh-models-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--rs);
  background: var(--bg-s);
  border: 1px solid var(--brd);
  color: var(--t2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all .15s;
}
.refresh-models-btn:hover:not(:disabled) {
  color: var(--t1);
  border-color: var(--brd-a);
  background: var(--bg-gh);
}
.refresh-models-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.models-source {
  font-size: 10px;
  color: var(--t3);
  margin-top: 2px;
}

.capabilities-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--brd);
}
.capabilities-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 12px;
}
.cap-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: var(--rs);
  background: var(--bg-s);
  border: 1px solid var(--brd);
  font-size: 11px;
  color: var(--t2);
}
.cap-item.on {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
}
.cap-icon {
  font-size: 14px;
  flex-shrink: 0;
}
.cap-label {
  flex: 1;
}


.modal-enter-active, .modal-leave-active { transition: opacity .2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .modal, .modal-leave-active .modal { transition: transform .2s ease; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: scale(0.95); }

/* Theme gallery */
.theme-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.theme-card {
  position: relative;
  border-radius: 10px;
  border: 2px solid var(--brd);
  overflow: hidden;
  cursor: pointer;
  transition: border-color .2s, transform .15s;
}
.theme-card:hover { transform: translateY(-2px); border-color: var(--brd-a); }
.theme-card.active { border-color: var(--accent); }

.theme-preview {
  height: 90px;
  display: flex;
  overflow: hidden;
}
.tp-sidebar {
  width: 28%;
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 8px 6px;
}
.tp-line {
  height: 4px;
  border-radius: 2px;
  opacity: 0.5;
}
.tp-line--active { opacity: 1; }
.tp-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 8px 6px;
  justify-content: flex-end;
}
.tp-bubble {
  border-radius: 5px;
  border: 1px solid;
  padding: 4px 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.tp-bubble--ai { align-self: flex-start; width: 65%; }
.tp-bubble--user { align-self: flex-end; width: 55%; }
.tp-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.tp-input {
  height: 12px;
  border-radius: 4px;
  border: 1px solid;
  margin-top: 2px;
}
.theme-meta {
  padding: 7px 10px 8px;
  background: var(--bg-s);
}
.theme-name { font-size: 12px; font-weight: 600; color: var(--t1); }
.theme-desc { font-size: 10px; color: var(--t3); margin-top: 1px; }
.theme-check {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--bg-inv);
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── Responsive styles ──────────────────────────── */

/* Legacy desktop / laptops (1024px - 1440px) */
@media (max-width: 1440px) {
  .settings-content { padding: 16px; }
  .s-section { margin-bottom: 20px; padding-bottom: 20px; }
}

/* Tablet (768px - 1024px) */
@media (max-width: 1024px) {
  .settings-nav { width: 180px; padding: 12px 8px; }
  .settings-content { padding: 14px; }
  .theme-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }
}

/* Mobile (< 768px) */
@media (max-width: 768px) {
  .settings-body {
    flex-direction: column;
  }

  .settings-nav {
    width: 100%;
    flex-direction: row;
    border-right: none;
    border-bottom: 1px solid var(--brd);
    padding: 8px;
    gap: 4px;
    overflow-x: auto;
  }

  .sn-item {
    white-space: nowrap;
    padding: 8px 12px;
  }

  .sb-label { display: none; }

  .settings-content {
    padding: 16px;
  }

  .theme-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .modal-body {
    width: 90vw;
    max-height: 80vh;
  }
}

/* Small mobile (< 480px) */
@media (max-width: 480px) {
  .topbar { padding: 10px 12px; }
  .tb-title { font-size: 13px; }
  .settings-content { padding: 12px; }

  .theme-grid {
    grid-template-columns: 1fr;
  }

  .s-section-title { font-size: 12px; }
}

/* Mobile landscape */
@media (max-width: 768px) and (orientation: landscape) {
  .settings-nav {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .theme-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Touch devices */
@media (hover: none) and (pointer: coarse) {
  .sn-item { min-height: 44px; }
  .btn { min-height: 44px; }
}
</style>
