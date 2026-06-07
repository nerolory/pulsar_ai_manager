<template>
  <div class="model-select-wrapper">
    <div class="model-select-trigger" @click="isOpen = !isOpen" :class="{ open: isOpen }">
      <div class="selected-model">
        <span v-if="selectedModel" class="model-name">{{ selectedModel.name }}</span>
        <span v-else class="placeholder">Выберите модель</span>
      </div>
      <div class="select-arrow">▼</div>
    </div>
    
    <Transition name="dropdown">
      <div v-if="isOpen" class="model-select-dropdown">
        <div
          v-for="model in models"
          :key="model.id"
          class="model-option"
          :class="{ selected: model.id === selectedModel?.id }"
          @click="selectModel(model)"
        >
          <div class="model-option-content">
            <div class="model-main">
              <span class="model-name">{{ model.name }}</span>
              <span v-if="getStatusText(model)" class="model-badge" :class="getStatusClass(model)">
                {{ getStatusText(model) }}
              </span>
            </div>
            <div class="model-meta">
              <span class="model-balance">
                {{ getBalanceText(model) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ModelInfo } from '@/types'

interface Props {
  models: ModelInfo[]
  modelId?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{ select: [model: ModelInfo] }>()

const isOpen = ref(false)
const selectedModel = computed(() => props.models.find(m => m.id === props.modelId))

function selectModel(model: ModelInfo) {
  emit('select', model)
  isOpen.value = false
}

function getStatusText(model: ModelInfo): string {
  if (model.is_free) return 'Бесплатно'
  if (model.requires_payment) return 'Платный'
  return ''
}

function getStatusClass(model: ModelInfo): string {
  if (model.is_free) return 'badge-free'
  if (model.requires_payment) return 'badge-paid'
  return ''
}

function getBalanceText(model: ModelInfo): string {
  if (model.balance !== undefined && model.balance !== null) {
    return `$${model.balance.toFixed(2)}`
  }
  if (model.limit_tokens) {
    return `${formatNumber(model.limit_tokens)} токенов`
  }
  if (model.daily_limit) {
    return `${formatNumber(model.daily_limit)}/день`
  }
  return 'не отслеживается'
}

function formatNumber(num: number): string {
  return num.toLocaleString('ru-RU')
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
  if (!(e.target as Element).closest('.model-select-wrapper')) {
    isOpen.value = false
  }
})
</script>

<style scoped>
.model-select-wrapper {
  position: relative;
  width: 100%;
}

.model-select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  background: var(--bg-s);
  border: 1px solid var(--brd);
  border-radius: var(--rs);
  cursor: pointer;
  transition: border-color .15s;
}

.model-select-trigger:hover {
  border-color: var(--brd-a);
}

.model-select-trigger.open {
  border-color: var(--accent);
}

.selected-model {
  flex: 1;
}

.model-name {
  font-size: 13px;
  color: var(--t1);
}

.placeholder {
  font-size: 13px;
  color: var(--t3);
}

.select-arrow {
  font-size: 10px;
  color: var(--t3);
  transition: transform .2s;
}

.model-select-trigger.open .select-arrow {
  transform: rotate(180deg);
}

.model-select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background: var(--bg-panel);
  border: 1px solid var(--brd);
  border-radius: var(--rs);
  box-shadow: var(--shadow-pop);
  z-index: 100;
}

.model-option {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--brd);
  transition: background .15s;
}

.model-option:last-child {
  border-bottom: none;
}

.model-option:hover {
  background: var(--bg-gh);
}

.model-option.selected {
  background: var(--accent-dim);
}

.model-option-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.model-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.badge-free {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.badge-paid {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.model-meta {
  font-size: 11px;
  color: var(--t3);
}

.model-balance {
  font-weight: 500;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity .2s, transform .2s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
