<template>
  <AppPreloader v-if="loading" @done="loading = false" />

  <div v-else class="app">
    <TheSidebar ref="sidebarRef" @open-settings="page = 'settings'" />
    <button
      class="sb-toggle"
      :style="{ left: sidebarWidth + 'px' }"
      :title="sidebarCollapsed ? 'Развернуть' : 'Свернуть'"
      @click="sidebarRef?.toggle()"
    >
      {{ sidebarCollapsed ? '›' : '‹' }}
    </button>

    <main class="main">
      <ChatView
        v-if="page === 'chat'"
        v-model:tune-open="tuneOpen"
        @open-settings="page = 'settings'"
      />
      <SettingsView v-else-if="page === 'settings'" @back="page = 'chat'" />
    </main>

    <TheRightPanel
      v-if="page === 'chat'"
      :open="tuneOpen"
      @close="tuneOpen = false"
    />
  </div>

  <AppToast />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import AppPreloader from '@/components/AppPreloader.vue'
import AppToast from '@/components/AppToast.vue'
import TheSidebar from '@/components/TheSidebar.vue'
import TheRightPanel from '@/components/TheRightPanel.vue'
import ChatView from '@/views/ChatView.vue'
import SettingsView from '@/views/SettingsView.vue'

const loading = ref(true)
const page = ref<'chat' | 'settings'>('chat')
const tuneOpen = ref(false)
const sidebarRef = ref<InstanceType<typeof TheSidebar> | null>(null)
const sidebarCollapsed = computed(() => sidebarRef.value?.collapsed ?? false)
const sidebarWidth = computed(() => sidebarCollapsed.value ? 58 : 260)
</script>

<style>
.app {
  display: flex; height: 100vh; position: relative; z-index: 1;
}
.main {
  flex: 1; display: flex; flex-direction: column; overflow: hidden;
  min-width: 0;
}
.sb-toggle {
  position: fixed; top: 50%; z-index: 200;
  transform: translateY(-50%) translateX(-50%);
  transition: left .2s ease;
  width: 20px; height: 40px; border-radius: 0 8px 8px 0;
  background: var(--bg-panel); border: 1px solid var(--brd); border-left: none;
  color: var(--t2); font-size: 18px; font-weight: 200;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  padding: 0; line-height: 1;
  box-shadow: 2px 0 8px rgba(0,0,0,0.3);
  transition: left .2s ease, color .15s, background .15s;
}
.sb-toggle:hover { color: var(--t1); background: var(--bg-gh); }
</style>
