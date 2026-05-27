<template>
  <div class="topbar">
    <div class="tb-info">
      <div class="tb-title">{{ title }}</div>
      <div class="tb-sub">{{ subtitle }}</div>
    </div>

    <button
      v-if="health"
      class="llm-badge"
      :title="'Настройть провайдер'"
      @click="emit('openSettings')"
    >
      <span class="llm-dot" :class="health.status === 'ok' ? 'ok' : 'err'" />
      <span class="llm-name">{{ health.model ?? health.provider }}</span>
      <span class="llm-gear">⚙</span>
    </button>
    <button v-else class="llm-badge llm-badge--warn" @click="emit('openSettings')">
      <span class="llm-dot err" />
      <span class="llm-name">Нет провайдера</span>
      <span class="llm-gear">⚙</span>
    </button>

    <button class="tb-btn" title="Очистить историю" @click="emit('clearChat')">🗑</button>
  </div>
</template>

<script setup lang="ts">
import type { HealthStatus } from '@/types'

defineProps<{
  title: string
  subtitle: string
  health: HealthStatus | null
}>()
const emit = defineEmits<{ clearChat: []; openSettings: [] }>()
</script>

<style scoped>
.topbar {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 20px; border-bottom: 1px solid var(--brd);
  background: rgba(255,255,255,0.02); flex-shrink: 0;
}
.tb-info { flex: 1; }
.tb-title { font-size: 14px; font-weight: 600; color: var(--t1); }
.tb-sub { font-size: 11px; color: var(--t3); margin-top: 1px; }

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
.llm-dot.ok { background: #22c55e; box-shadow: 0 0 6px rgba(34,197,94,0.5); }
.llm-dot.err { background: #ef4444; }
.llm-name { color: var(--t2); }
.llm-gear { color: var(--t3); font-size: 11px; }

.tb-btn {
  width: 30px; height: 30px; border-radius: var(--rs);
  background: var(--bg-s); border: 1px solid var(--brd);
  color: var(--t2); font-size: 13px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.tb-btn:hover { color: #ef4444; border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.08); }

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
