import { ref } from 'vue'
import {
  type ContextZone,
  type ContextMenuItems,
  getSelectedText,
  isEditableElement,
  getInputSelection,
  resolveContextMenuItems,
  clampMenuPosition,
} from '@/utils/contextMenuActions'

export interface ContextMenuState {
  visible: boolean
  x: number
  y: number
  zone: ContextZone
  target: HTMLElement | null
  items: ContextMenuItems
}

const menuState = ref<ContextMenuState>({
  visible: false,
  x: 0,
  y: 0,
  zone: 'readonly',
  target: null,
  items: { copy: false, cut: false, paste: false, show: false },
})

let menuEl: HTMLElement | null = null

function computeItems(zone: ContextZone, target: HTMLElement): ContextMenuItems {
  const hasSelection = zone === 'editable' && isEditableElement(target)
    ? getInputSelection(target).text.length > 0
    : getSelectedText().length > 0

  const isFocused = document.activeElement === target
  const clipboardAvailable = typeof navigator !== 'undefined' && !!navigator.clipboard

  return resolveContextMenuItems(zone, {
    hasSelection,
    isFocused,
    clipboardAvailable,
  })
}

function closeContextMenu() {
  menuState.value.visible = false
  menuState.value.target = null
}

function openContextMenu(event: MouseEvent, zone: ContextZone, target: HTMLElement) {
  if (zone === 'editable' && isEditableElement(target)) {
    target.focus()
  }

  const items = computeItems(zone, target)
  if (!items.show) return false

  event.preventDefault()
  event.stopPropagation()

  const estimatedWidth = 160
  const estimatedHeight = zone === 'editable' ? 108 : 40
  const { x, y } = clampMenuPosition(event.clientX, event.clientY, estimatedWidth, estimatedHeight)

  menuState.value = {
    visible: true,
    x,
    y,
    zone,
    target,
    items,
  }
  return true
}

async function copySelection() {
  const { target, zone, items } = menuState.value
  if (!items.copy) return

  if (zone === 'editable' && target && isEditableElement(target)) {
    const { text } = getInputSelection(target)
    if (text) {
      await navigator.clipboard.writeText(text)
      closeContextMenu()
      return
    }
  }

  const text = getSelectedText()
  if (text) {
    await navigator.clipboard.writeText(text)
  }
  closeContextMenu()
}

async function cutSelection() {
  const { target, items } = menuState.value
  if (!items.cut || !target || !isEditableElement(target)) return

  const { start, end, text } = getInputSelection(target)
  if (!text) return

  await navigator.clipboard.writeText(text)
  target.setRangeText('', start, end, 'end')
  target.dispatchEvent(new Event('input', { bubbles: true }))
  closeContextMenu()
}

async function pasteFromClipboard() {
  const { target, items } = menuState.value
  if (!items.paste || !target || !isEditableElement(target)) return

  try {
    const text = await navigator.clipboard.readText()
    if (!text) return

    const start = target.selectionStart ?? target.value.length
    const end = target.selectionEnd ?? start
    target.setRangeText(text, start, end, 'end')
    target.dispatchEvent(new Event('input', { bubbles: true }))
    target.focus()
  } catch {
    document.execCommand('paste')
  }
  closeContextMenu()
}

function handleContextMenuEvent(event: MouseEvent, zone: ContextZone, target?: HTMLElement) {
  const el = target ?? (event.currentTarget as HTMLElement | null)
  if (!el) return
  openContextMenu(event, zone, el)
}

function setMenuElement(el: HTMLElement | null) {
  menuEl = el
  if (el && menuState.value.visible) {
    const rect = el.getBoundingClientRect()
    const { x, y } = clampMenuPosition(menuState.value.x, menuState.value.y, rect.width, rect.height)
    menuState.value.x = x
    menuState.value.y = y
  }
}

export function useContextMenuProvider() {
  return {
    menuState,
    closeContextMenu,
    handleContextMenuEvent,
    copySelection,
    cutSelection,
    pasteFromClipboard,
    setMenuElement,
  }
}

export function useContextMenu() {
  return useContextMenuProvider()
}
