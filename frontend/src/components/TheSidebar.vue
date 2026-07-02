<template>
  <aside class="sb" :class="{ collapsed, open: isOpen }">
    <div v-if="isOpen" class="sb-close" @click="toggle">✕</div>
    <div class="logo">
      <div class="logo-icon">P</div>
      <div class="logo-txt">Pulsar<em>AI</em></div>
    </div>

    <button class="new-btn" :title="collapsed ? t('sidebar.new_chat') : ''" @click="chatStore.createChat()">
      <span>＋</span>
      <span v-if="!collapsed"> {{ t('sidebar.new_chat') }}</span>
    </button>

    <template v-if="!collapsed">
      <div
        class="chat-list"
        @dragover.prevent
        @drop="onDrop($event)"
      >
        <template v-if="today.length">
          <div class="sb-label">{{ t('sidebar.today') }}</div>
          <div
            v-for="chat in today" :key="chat.id"
            class="ci" :class="{ on: chat.id === activeChatId, dragging: dragId === chat.id }"
            draggable="true"
            @dragstart="onDragStart($event, chat.id)"
            @dragend="onDragEnd"
            @dragover.prevent="onDragOver($event, chat.id)"
            @click="handleChatClick(chat.id)"
          >
            <span class="ci-dot" />
            <input
              v-if="editingId === chat.id"
              class="ci-input"
              :ref="setRenameRef"
              v-model="editingTitle"
              @blur="commitRename"
              @keydown.enter="commitRename"
              @keydown.esc="cancelRename"
              @click.stop
            />
            <span v-else class="ci-title">{{ chat.title }}</span>
            <button class="ci-del" :title="t('sidebar.delete_chat')" @click.stop="chatStore.deleteChat(chat.id)">✕</button>
          </div>
        </template>

        <template v-if="older.length">
          <div class="sb-label">{{ t('sidebar.older') }}</div>
          <div
            v-for="chat in older" :key="chat.id"
            class="ci" :class="{ on: chat.id === activeChatId, dragging: dragId === chat.id }"
            draggable="true"
            @dragstart="onDragStart($event, chat.id)"
            @dragend="onDragEnd"
            @dragover.prevent="onDragOver($event, chat.id)"
            @click="handleChatClick(chat.id)"
          >
            <span class="ci-dot" />
            <input
              v-if="editingId === chat.id"
              class="ci-input"
              :ref="setRenameRef"
              v-model="editingTitle"
              @blur="commitRename"
              @keydown.enter="commitRename"
              @keydown.esc="cancelRename"
              @click.stop
            />
            <span v-else class="ci-title">{{ chat.title }}</span>
            <button class="ci-del" :title="t('sidebar.delete_chat')" @click.stop="chatStore.deleteChat(chat.id)">✕</button>
          </div>
        </template>
      </div>
    </template>

    <div
      class="drop-zone"
      @dragover.prevent
      @drop="onDropBottom($event)"
    />
    <div class="sb-space" />

    <!-- TODO: User block - hide for now, may become legacy -->
    <!-- <template v-if="!collapsed">
      <div class="sb-user">
        <div class="ava">U</div>
        <div class="u-info">
          <div class="u-name">{{ t('common.user') }}</div>
          <div class="u-plan">Free plan</div>
        </div>
      </div>
    </template> -->

    <button class="cfg-btn" @click="toggle(); emit('openSettings')">
      <span v-if="!collapsed">⚙ {{ t('sidebar.settings') }}</span>
      <span v-else>⚙</span>
    </button>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import type { ComponentPublicInstance } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import { useI18n } from '@/composables/useI18n'

const emit = defineEmits<{ openSettings: []; collapse: [val: boolean] }>()
const chatStore = useChatStore()
const { activeChatId } = storeToRefs(chatStore)
const { t } = useI18n()
const collapsed = ref(false)
const isOpen = ref(false)

function toggle() {
  if (window.innerWidth < 768) {
    isOpen.value = !isOpen.value
  } else {
    collapsed.value = !collapsed.value
    emit('collapse', collapsed.value)
  }
}

defineExpose({ collapsed, isOpen, toggle })

const DAY = 86_400_000
const today = computed(() =>
  chatStore.chats.filter((chat) => Date.now() - chat.createdAt < DAY),
)
const older = computed(() =>
  chatStore.chats.filter((chat) => Date.now() - chat.createdAt >= DAY),
)

// ── Rename ────────────────────────────────────────
const editingId = ref<string | null>(null)
const editingTitle = ref('')
const renameInput = ref<HTMLInputElement | null>(null)

function setRenameRef(el: Element | ComponentPublicInstance | null) {
  renameInput.value = el as HTMLInputElement | null
}

function handleChatClick(id: string) {
  if (editingId.value) return // input is open - ignore
  if (id === activeChatId.value) {
    // second click on active chat → start rename
    const chat = chatStore.chats.find((chat) => chat.id === id)
    if (chat) startRename(id, chat.title)
  } else {
    chatStore.selectChat(id)
  }
}

function startRename(id: string, title: string) {
  editingId.value = id
  editingTitle.value = title
  nextTick(() => {
    if (renameInput.value) {
      renameInput.value.focus()
      renameInput.value.select()
    }
  })
}

function commitRename() {
  if (editingId.value && editingTitle.value.trim()) {
    chatStore.renameChat(editingId.value, editingTitle.value.trim())
  }
  editingId.value = null
}

function cancelRename() {
  editingId.value = null
}

function onGlobalClick(e: MouseEvent) {
  if (!editingId.value) return
  const target = e.target as HTMLElement
  if (!target.closest('.ci-input')) {
    commitRename()
  }
}

onMounted(() => document.addEventListener('click', onGlobalClick, true))
onUnmounted(() => document.removeEventListener('click', onGlobalClick, true))

// ── Drag-and-drop reorder ─────────────────────────
const dragId = ref<string | null>(null)
const dragOverId = ref<string | null>(null)

function onDragStart(e: DragEvent, id: string) {
  dragId.value = id
  e.dataTransfer!.effectAllowed = 'move'
}

function onDragEnd() {
  dragId.value = null
  dragOverId.value = null
}

function onDragOver(e: DragEvent, id: string) {
  dragOverId.value = id
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  if (!dragId.value || !dragOverId.value || dragId.value === dragOverId.value) {
    dragId.value = null
    dragOverId.value = null
    return
  }
  chatStore.reorderChat(dragId.value, dragOverId.value)
  dragId.value = null
  dragOverId.value = null
}

function onDropBottom(e: DragEvent) {
  e.preventDefault()
  if (!dragId.value) return
  chatStore.reorderChat(dragId.value, chatStore.chats[chatStore.chats.length - 1].id)
  dragId.value = null
  dragOverId.value = null
}
</script>

<style scoped>
.sb {
  width: var(--sw); flex-shrink: 0;
  background: var(--bg-g); backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border-right: 1px solid var(--brd);
  display: flex; flex-direction: column; padding: 14px 10px; gap: 4px;
  overflow-y: auto; overflow-x: hidden;
  transition: width .2s ease;
}
.sb.collapsed { width: 58px; padding: 14px 8px; }
.logo {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 2px 14px; border-bottom: 1px solid var(--brd); margin-bottom: 6px;
}
.logo-icon {
  flex-shrink: 0;
  width: 30px; height: 30px; border-radius: 8px;
  background: linear-gradient(135deg, var(--accent), #8B5CF6);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 800; color: var(--on-accent);
  box-shadow: 0 0 14px rgba(99,102,241,0.5);
}
.logo-txt { font-size: 14px; font-weight: 700; flex: 1; white-space: nowrap; overflow: hidden; }
.logo-txt em { font-style: normal; color: var(--accent-l); }

.sb.collapsed .logo-txt { display: none; }

.new-btn {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 8px 12px; border-radius: var(--rs);
  background: var(--bg-s); border: 1px solid var(--brd);
  color: var(--t1); font-size: 12.5px; font-weight: 500; cursor: pointer;
  transition: all .2s; margin-bottom: 6px;
}
.new-btn:hover { background: var(--bg-gh); border-color: var(--brd-a); }

.sb-label {
  font-size: 10px; font-weight: 600; color: var(--t3);
  letter-spacing: 1px; text-transform: uppercase; padding: 6px 10px 3px;
}
.ci {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 10px; border-radius: var(--rs);
  font-size: 12.5px; color: var(--t2); cursor: pointer;
  transition: all .15s; overflow: hidden;
}
.ci:hover { background: var(--bg-gh); color: var(--t1); }
.ci.on { background: var(--accent-dim); color: var(--t1); }
.ci.dragging { opacity: 0.4; }
.drop-zone { min-height: 40px; flex-shrink: 0; }
.ci-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--t3); flex-shrink: 0;
}
.ci.on .ci-dot { background: var(--accent-l); }
.ci-title { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ci-del {
  flex-shrink: 0; opacity: 0; width: 20px; height: 20px; border-radius: 4px;
  background: none; border: none; color: var(--t1); font-size: 12px; font-weight: 600;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all .12s;
}
.ci:hover .ci-del { opacity: 0.7; }
.ci-del:hover { opacity: 1 !important; color: var(--error); background: var(--error-bg); }

.ci-input {
  flex: 1; background: var(--bg-s); border: 1px solid var(--accent);
  border-radius: 4px; color: var(--t1); font-size: 12.5px;
  padding: 1px 6px; outline: none; min-width: 0;
}

.sb-space { flex: 1; }
.sb-user {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 8px; border-top: 1px solid var(--brd); margin-top: 4px;
}
.ava {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #8B5CF6);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: var(--on-accent); flex-shrink: 0;
}
.u-info { flex: 1; }
.u-name { font-size: 12px; font-weight: 600; color: var(--t1); }
.u-plan { font-size: 10px; color: var(--t3); }
.cfg-btn {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  width: 100%; height: 40px; padding: 8px 12px; border-radius: var(--rs);
  background: var(--bg-s); border: 1px solid var(--brd);
  color: var(--t1); font-size: 12px; font-weight: 500; cursor: pointer;
  transition: all .15s; flex-shrink: 0;
}
.cfg-btn:hover { background: var(--bg-gh); border-color: var(--brd-a); }

/* ── Responsive styles ──────────────────────────── */

/* Legacy desktop / laptops (1024px - 1440px) */
@media (max-width: 1440px) {
  .sb { width: var(--sw); }
  .logo-txt { font-size: 15px; }
  .ci-title { font-size: 12px; }
}

/* Tablet (768px - 1024px) */
@media (max-width: 1024px) {
  .sb { width: var(--sw); }
  .logo { padding: 10px; }
  .logo-icon { width: 32px; height: 32px; font-size: 15px; }
  .new-btn { margin: 0 10px 10px; }
  .chat-list { padding: 0 10px; }
  .sb-label { padding: 10px 10px 6px; }
  .ci { padding: 8px 10px; }
}

/* Mobile (< 768px) */
@media (max-width: 768px) {
  .sb {
    width: 280px;
    background: var(--bg-panel);
    box-shadow: 2px 0 20px rgba(0, 0, 0, 0.4);
  }

  .sb.collapsed {
    width: 280px;
  }

  .sb.collapsed .logo,
  .sb.collapsed .new-btn,
  .sb.collapsed .chat-list,
  .sb.collapsed .sb-user {
    display: flex;
  }

  .sb-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid var(--brd);
  }

  .sb-close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: var(--bg-s);
    border: 1px solid var(--brd);
    border-radius: var(--rs);
    color: var(--t1);
    font-size: 18px;
    cursor: pointer;
  }

  .logo {
    padding: 16px;
    display: flex !important;
    align-items: center;
    gap: 8px;
  }

  .logo-icon {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }

  .logo-txt {
    display: block !important;
    font-size: 15px;
  }

  .new-btn { margin: 0 16px 12px; }
  .chat-list { padding: 0 16px; }
  .ci { padding: 12px 16px; }
  .ci-title { font-size: 14px; }
}

/* Small mobile (< 480px) */
@media (max-width: 480px) {
  .sb { width: 260px; }
  .logo-txt { font-size: 15px; }
  .ci-title { font-size: 13px; }
}

/* Mobile landscape */
@media (max-width: 768px) and (orientation: landscape) {
  .sb { width: 240px; }
  .chat-list { max-height: calc(100vh - 180px); }
}

/* Touch devices */
@media (hover: none) and (pointer: coarse) {
  .ci { min-height: 44px; }
  .new-btn { min-height: 44px; }
  .cfg-btn { min-height: 44px; }
  .ci-del { width: 32px; height: 32px; }
}
</style>
