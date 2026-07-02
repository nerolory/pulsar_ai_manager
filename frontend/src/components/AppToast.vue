<template>
  <TransitionGroup name="toast" tag="div" class="toast-stack">
    <div v-for="toast in toasts" :key="toast.id" class="toast">
      <div class="toast-icon">{{ toast.icon }}</div>
      <div class="toast-text">
        <b>{{ toast.title }}</b>
        <span>{{ toast.message }}</span>
      </div>
      <button class="toast-close" @click="dismiss(toast.id)">✕</button>
    </div>
  </TransitionGroup>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'
const { toasts, dismiss } = useToast()
</script>

<style scoped>
.toast-stack {
  position: fixed; bottom: 24px; right: 24px;
  z-index: 8000; display: flex; flex-direction: column; gap: 8px;
}
.toast {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: var(--r);
  background: var(--bg-panel); border: 1px solid var(--brd);
  backdrop-filter: var(--blur);
  box-shadow: var(--shadow-pop);
  min-width: 240px; max-width: 340px;
}
.toast-close {
  margin-left: auto; flex-shrink: 0;
  background: var(--bg-s); border: 1px solid var(--brd); color: var(--t2);
  font-size: 11px; cursor: pointer; padding: 3px 6px;
  border-radius: 5px; line-height: 1; transition: all .15s;
}
.toast-close:hover { color: var(--error); border-color: var(--error-dim); background: var(--error-bg); }
.toast-icon { font-size: 18px; flex-shrink: 0; }
.toast-text { display: flex; flex-direction: column; gap: 2px; }
.toast-text b { font-size: 12px; font-weight: 600; color: var(--t1); }
.toast-text span { font-size: 11px; color: var(--t2); }

.toast-enter-active, .toast-leave-active { transition: all .25s ease; }
.toast-enter-from { opacity: 0; transform: translateX(20px); }
.toast-leave-to   { opacity: 0; transform: translateX(20px); }

/* ── Responsive styles ──────────────────────────── */

/* Mobile (< 768px) */
@media (max-width: 768px) {
  .toasts {
    left: 12px;
    right: 12px;
    top: 12px;
  }

  .toast {
    min-width: auto;
    max-width: none;
    width: 100%;
  }
}

/* Small mobile (< 480px) */
@media (max-width: 480px) {
  .toast {
    padding: 10px 12px;
    gap: 8px;
  }

  .toast-text b { font-size: 11px; }
  .toast-text span { font-size: 10px; }
  .toast-close { width: 24px; height: 24px; }
}
</style>
