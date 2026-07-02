<template>
  <Teleport to="body">
    <div
      v-if="menuState.visible"
      ref="menuRef"
      class="context-menu"
      :style="{ top: `${menuState.y}px`, left: `${menuState.x}px` }"
      @contextmenu.prevent
    >
      <button
        type="button"
        class="context-menu__item"
        :disabled="!menuState.items.copy"
        @click="copySelection()"
      >
        {{ t('context_menu.copy') }}
      </button>
      <template v-if="menuState.zone === 'editable'">
        <button
          type="button"
          class="context-menu__item"
          :disabled="!menuState.items.cut"
          @click="cutSelection()"
        >
          {{ t('context_menu.cut') }}
        </button>
        <button
          type="button"
          class="context-menu__item"
          :disabled="!menuState.items.paste"
          @click="pasteFromClipboard()"
        >
          {{ t('context_menu.paste') }}
        </button>
      </template>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useI18n } from '@/composables/useI18n'
import { useContextMenuProvider } from '@/composables/useContextMenu'

const { t } = useI18n()
const {
  menuState,
  closeContextMenu,
  copySelection,
  cutSelection,
  pasteFromClipboard,
  setMenuElement,
} = useContextMenuProvider()

const menuRef = ref<HTMLElement | null>(null)

const onDocClick = (e: MouseEvent) => {
  if (!menuState.value.visible) return
  if (menuRef.value?.contains(e.target as Node)) return
  closeContextMenu()
}
const onKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') closeContextMenu()
}
const onScroll = () => closeContextMenu()

watch(
  () => menuState.value.visible,
  async (visible) => {
    if (!visible) {
      setMenuElement(null)
      return
    }
    await nextTick()
    setMenuElement(menuRef.value)
  },
)

onMounted(() => {
  document.addEventListener('click', onDocClick, true)
  document.addEventListener('keydown', onKeyDown)
  window.addEventListener('scroll', onScroll, true)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocClick, true)
  document.removeEventListener('keydown', onKeyDown)
  window.removeEventListener('scroll', onScroll, true)
})
</script>

<style scoped>
.context-menu {
  position: fixed;
  z-index: 9000;
  min-width: 148px;
  padding: 4px;
  border-radius: var(--rs);
  background: var(--bg-panel);
  border: 1px solid var(--brd);
  box-shadow: var(--shadow-pop);
  backdrop-filter: var(--blur);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.context-menu__item {
  width: 100%;
  text-align: left;
  padding: 7px 10px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--t1);
  font-size: 12.5px;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}

.context-menu__item:hover:not(:disabled) {
  background: var(--bg-gh);
}

.context-menu__item:disabled {
  color: var(--t3);
  cursor: default;
  opacity: 0.55;
}
</style>
