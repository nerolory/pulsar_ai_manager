export type ContextZone = 'readonly' | 'editable'

export interface ContextMenuItems {
  copy: boolean
  cut: boolean
  paste: boolean
  show: boolean
}

export function getSelectedText(): string {
  return window.getSelection()?.toString() ?? ''
}

export function isEditableElement(el: HTMLElement | null): el is HTMLInputElement | HTMLTextAreaElement {
  return el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement
}

export function getInputSelection(el: HTMLInputElement | HTMLTextAreaElement): {
  start: number
  end: number
  text: string
} {
  const start = el.selectionStart ?? 0
  const end = el.selectionEnd ?? 0
  return { start, end, text: el.value.substring(start, end) }
}

export function resolveContextMenuItems(
  zone: ContextZone,
  opts: {
    hasSelection: boolean
    isFocused: boolean
    clipboardAvailable: boolean
  },
): ContextMenuItems {
  if (zone === 'readonly') {
    return {
      copy: opts.hasSelection,
      cut: false,
      paste: false,
      show: opts.hasSelection,
    }
  }

  const show = opts.isFocused || opts.hasSelection
  return {
    copy: opts.hasSelection,
    cut: opts.hasSelection && opts.isFocused,
    paste: opts.isFocused && opts.clipboardAvailable,
    show,
  }
}

export function clampMenuPosition(
  x: number,
  y: number,
  menuWidth: number,
  menuHeight: number,
  padding = 8,
): { x: number; y: number } {
  const maxX = window.innerWidth - menuWidth - padding
  const maxY = window.innerHeight - menuHeight - padding
  return {
    x: Math.max(padding, Math.min(x, maxX)),
    y: Math.max(padding, Math.min(y, maxY)),
  }
}
