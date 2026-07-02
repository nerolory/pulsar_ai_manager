<template>
  <div ref="wrapperRef" class="model-select-wrapper">
    <div class="model-select-trigger" @click="toggleOpen" :class="{ open: isOpen }">
      <div class="selected-model">
        <span v-if="selectedModel" class="model-name">{{ selectedModel.name }}</span>
        <span v-else class="placeholder">{{ t('model_select.placeholder') }}</span>
      </div>
      <div class="select-arrow">▼</div>
    </div>

    <Teleport to="body">
      <Transition name="dropdown">
        <div
          v-if="isOpen"
          ref="dropdownRef"
          class="model-select-dropdown"
          :style="dropdownStyle"
        >
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
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import type { ModelInfo } from '@/types'
import { useI18n } from '@/composables/useI18n'

interface Props {
  models: ModelInfo[]
  modelId?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{ select: [model: ModelInfo] }>()
const { t } = useI18n()

const isOpen = ref(false)
const wrapperRef = ref<HTMLElement | null>(null)
const dropdownRef = ref<HTMLElement | null>(null)
const dropdownStyle = ref<Record<string, string>>({})
const selectedModel = computed(() => props.models.find(m => m.id === props.modelId))

function updateDropdownPosition() {
  if (!wrapperRef.value || !isOpen.value) return

  const rect = wrapperRef.value.getBoundingClientRect()
  const viewportPadding = 8
  const gap = 4
  const maxHeight = 300
  const spaceBelow = window.innerHeight - rect.bottom - viewportPadding
  const spaceAbove = rect.top - viewportPadding
  const openUpward = spaceBelow < 160 && spaceAbove > spaceBelow

  let top = openUpward ? rect.top - gap : rect.bottom + gap
  let maxDropdownHeight = openUpward
    ? Math.min(maxHeight, spaceAbove - gap)
    : Math.min(maxHeight, spaceBelow - gap)

  if (maxDropdownHeight < 120) {
    maxDropdownHeight = Math.max(120, Math.min(maxHeight, Math.max(spaceBelow, spaceAbove) - gap))
  }

  if (openUpward) {
    top = rect.top - gap - maxDropdownHeight
  }

  dropdownStyle.value = {
    position: 'fixed',
    top: `${Math.max(viewportPadding, top)}px`,
    left: `${rect.left}px`,
    width: `${rect.width}px`,
    maxHeight: `${maxDropdownHeight}px`,
    zIndex: '8000',
  }
}

function toggleOpen() {
  isOpen.value = !isOpen.value
}

function selectModel(model: ModelInfo) {
  emit('select', model)
  isOpen.value = false
}

function handleDocumentClick(event: MouseEvent) {
  const target = event.target as Node
  if (wrapperRef.value?.contains(target) || dropdownRef.value?.contains(target)) {
    return
  }
  isOpen.value = false
}

watch(isOpen, async (open) => {
  if (!open) return
  await nextTick()
  updateDropdownPosition()
})

watch(() => props.models.length, () => {
  if (isOpen.value) {
    nextTick(updateDropdownPosition)
  }
})

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  window.addEventListener('resize', updateDropdownPosition)
  window.addEventListener('scroll', updateDropdownPosition, true)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
  window.removeEventListener('resize', updateDropdownPosition)
  window.removeEventListener('scroll', updateDropdownPosition, true)
})

function getStatusText(model: ModelInfo): string {
  if (model.is_free) return t('model_select.free')
  if (model.requires_payment) return t('model_select.paid')
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
    return t('model_select.tokens_limit', { count: formatNumber(model.limit_tokens) })
  }
  if (model.daily_limit) {
    return t('model_select.per_day', { count: formatNumber(model.daily_limit) })
  }
  return t('model_select.balance_not_tracked')
}

function formatNumber(num: number): string {
  return num.toLocaleString('ru-RU')
}
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
  overflow-y: auto;
  background: var(--bg-panel);
  border: 1px solid var(--brd);
  border-radius: var(--rs);
  box-shadow: var(--shadow-pop);
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
  background: var(--success-bg);
  color: var(--success);
  border: 1px solid var(--success-dim);
}

.badge-paid {
  background: var(--info-bg);
  color: var(--info);
  border: 1px solid var(--info-dim);
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
