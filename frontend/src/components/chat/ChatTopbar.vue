<template>
  <div class="topbar">
    <div class="tb-info">
      <div class="tb-title">{{ title }}</div>
      <div class="tb-sub">{{ subtitle }}</div>
    </div>

    <div v-if="balance" class="balance-badge" :title="t('topbar.balance_title')">
      <span class="balance-icon">💰</span>
      <span class="balance-value">{{ balance }}</span>
    </div>

    <div v-if="tokenEstimate" class="token-badge" :title="t('topbar.tokens_title')">
      <span class="token-icon">📝</span>
      <span class="token-value">{{ tokenEstimate }}</span>
    </div>

    <button
      v-if="health"
      class="llm-badge"
      :title="t('topbar.configure_provider')"
      @click="emit('openSettings')"
    >
      <span class="llm-dot" :class="health.status === 'ok' ? 'ok' : 'err'" />
      <span class="llm-name">{{ health.model ?? health.provider }}</span>
      <span class="llm-gear">⚙</span>
    </button>
    <button v-else class="llm-badge llm-badge--warn" @click="emit('openSettings')">
      <span class="llm-dot err" />
      <span class="llm-name">{{ t('topbar.no_provider') }}</span>
      <span class="llm-gear">⚙</span>
    </button>

    <button class="tb-btn" :title="t('topbar.clear_history')" @click="emit('clearChat')">🗑</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getBalance } from '@/api/settings'
import type { ProviderBalance } from '@/api/settings'
import { useSettingsStore } from '@/stores/settings'
import { useI18n } from '@/composables/useI18n'
import type { HealthStatus } from '@/types'

defineProps<{
  title: string
  subtitle: string
  health: HealthStatus | null
}>()
const emit = defineEmits<{ clearChat: []; openSettings: [] }>()

const settingsStore = useSettingsStore()
const { t } = useI18n()
const balance = ref<string | null>(null)
const tokenEstimate = ref<string | null>(null)

function calculateTokenEstimate(bal: ProviderBalance) {
  console.log('Calculating token estimate')
  console.log('Active model:', settingsStore.activeModel)
  console.log('Models:', settingsStore.models)
  
  if (settingsStore.activeModel && settingsStore.models.length > 0) {
    const currentModel = settingsStore.models.find(m => m.id === settingsStore.activeModel)
    console.log('Current model found:', currentModel)
    
    // Check if model has free tier
    if (currentModel?.free_tier) {
      tokenEstimate.value = t('topbar.free_tier')
      console.log('Model has free tier')
      return
    }
    
    if (currentModel?.pricing) {
      const pricing = currentModel.pricing as Record<string, number>
      const promptPrice = pricing.prompt || 0
      const completionPrice = pricing.completion || 0
      const avgPrice = (promptPrice + completionPrice) / 2
      
      console.log('Pricing:', { promptPrice, completionPrice, avgPrice })
      
      if (avgPrice > 0 && bal.balance > 0) {
        const estimatedTokens = Math.floor(bal.balance / avgPrice)
        tokenEstimate.value = t('topbar.estimated_tokens', { count: formatNumber(estimatedTokens) })
        console.log('Token estimate:', tokenEstimate.value)
      } else if (bal.balance <= 0) {
        tokenEstimate.value = t('topbar.zero_tokens')
        console.log('Negative or zero balance')
      }
    } else {
      console.log('No pricing data for model')
    }
  } else {
    console.log('No active model or models not loaded')
  }
}

onMounted(async () => {
  try {
    const balanceResponse = await getBalance()
    
    if (balanceResponse.balance !== null && balanceResponse.balance !== undefined) {
      const bal = balanceResponse.balance
      console.log('Balance data:', bal)
      
      if (bal.currency === 'USD') {
        balance.value = `$${bal.balance}`
        calculateTokenEstimate(bal)
      } else {
        balance.value = `${bal.balance} ${bal.currency}`
      }
    } else {
      balance.value = null
    }
  } catch {
    balance.value = null
    tokenEstimate.value = null
  }
})

watch(() => settingsStore.models, () => {
  if (balance.value) {
    // Re-calculate when models are loaded
    getBalance().then(response => {
      if (response.balance) {
        calculateTokenEstimate(response.balance)
      }
    })
  }
})

watch(() => settingsStore.activeModel, () => {
  if (balance.value) {
    // Re-calculate when model changes
    getBalance().then(response => {
      if (response.balance) {
        calculateTokenEstimate(response.balance)
      }
    })
  }
})

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>

<style scoped>
.topbar {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 20px; border-bottom: 1px solid var(--brd);
  background: var(--topbar-bg); flex-shrink: 0;
}
.tb-info { flex: 1; }
.tb-title { font-size: 14px; font-weight: 600; color: var(--t1); }
.tb-sub { font-size: 11px; color: var(--t3); margin-top: 1px; }

.balance-badge {
  display: flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 20px;
  background: var(--bg-s); border: 1px solid var(--brd);
  font-size: 11px;
}
.balance-icon { font-size: 12px; }
.balance-value { color: var(--t2); font-weight: 500; }

.token-badge {
  display: flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 20px;
  background: var(--bg-s); border: 1px solid var(--brd);
  font-size: 11px;
}
.token-icon { font-size: 12px; }
.token-value { color: var(--t2); font-weight: 500; }

.llm-badge {
  display: flex; align-items: center; gap: 5px;
  padding: 4px 10px; border-radius: 20px;
  background: var(--bg-s); border: 1px solid var(--brd);
  font-size: 11px; cursor: pointer; transition: all .15s;
}
.llm-badge:hover { border-color: var(--brd-a); background: var(--bg-gh); }
.llm-badge--warn { border-color: rgba(239,68,68,0.3); background: rgba(239,68,68,0.06); }
.llm-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--t3);
}
.llm-dot.ok { background: var(--success); box-shadow: 0 0 6px var(--success-dim); }
.llm-dot.err { background: var(--error); }
.llm-name { color: var(--t2); }
.llm-gear { color: var(--t3); font-size: 11px; }

.tb-btn {
  width: 30px; height: 30px; border-radius: var(--rs);
  background: var(--bg-s); border: 1px solid var(--brd);
  color: var(--t2); font-size: 13px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.tb-btn:hover { color: var(--error); border-color: var(--error-dim); background: var(--error-bg); }

/* ── Responsive styles ──────────────────────────── */

/* Legacy desktop / laptops (1024px - 1440px) */
@media (max-width: 1440px) {
  .topbar { padding: 10px 12px; }
  .chat-title { font-size: 13px; }
}

/* Tablet (768px - 1024px) */
@media (max-width: 1024px) {
  .topbar { padding: 8px 10px; }
  .chat-title { font-size: 12px; max-width: 180px; }
  .llm-badge { padding: 3px 8px; font-size: 10px; }
}

/* Mobile (< 768px) */
@media (max-width: 768px) {
  .topbar {
    padding: 8px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .chat-title {
    font-size: 12px;
    max-width: 150px;
    order: 3;
    width: 100%;
    justify-content: flex-start;
  }

  .llm-badge {
    padding: 4px 8px;
    font-size: 10px;
    order: 2;
  }

  .tb-btn {
    width: 32px;
    height: 32px;
    font-size: 12px;
  }
}

/* Small mobile (< 480px) */
@media (max-width: 480px) {
  .topbar { padding: 6px; }
  .chat-title {
    font-size: 11px;
    max-width: 120px;
  }
  .llm-name { max-width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .tb-btn { width: 28px; height: 28px; }
}

/* Mobile landscape */
@media (max-width: 768px) and (orientation: landscape) {
  .chat-title {
    max-width: 200px;
    order: 2;
    width: auto;
  }
  .llm-badge { order: 3; }
}

/* Touch devices */
@media (hover: none) and (pointer: coarse) {
  .llm-badge { min-height: 32px; }
  .tb-btn { min-width: 36px; min-height: 36px; }
}
</style>
