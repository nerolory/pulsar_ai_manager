import { describe, expect, it } from 'vitest'
import { clampMenuPosition, resolveContextMenuItems } from '@/utils/contextMenuActions'

describe('resolveContextMenuItems', () => {
  it('readonly zone shows copy only when text is selected', () => {
    expect(resolveContextMenuItems('readonly', {
      hasSelection: true,
      isFocused: false,
      clipboardAvailable: true,
    })).toEqual({ copy: true, cut: false, paste: false, show: true })

    expect(resolveContextMenuItems('readonly', {
      hasSelection: false,
      isFocused: false,
      clipboardAvailable: true,
    })).toEqual({ copy: false, cut: false, paste: false, show: false })
  })

  it('editable zone enables cut/copy with selection and paste when focused', () => {
    expect(resolveContextMenuItems('editable', {
      hasSelection: true,
      isFocused: true,
      clipboardAvailable: true,
    })).toEqual({ copy: true, cut: true, paste: true, show: true })

    expect(resolveContextMenuItems('editable', {
      hasSelection: false,
      isFocused: true,
      clipboardAvailable: true,
    })).toEqual({ copy: false, cut: false, paste: true, show: true })
  })
})

describe('clampMenuPosition', () => {
  it('keeps menu inside viewport', () => {
    const originalInnerWidth = window.innerWidth
    const originalInnerHeight = window.innerHeight
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 400 })
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: 300 })

    expect(clampMenuPosition(390, 290, 160, 100)).toEqual({ x: 232, y: 192 })

    Object.defineProperty(window, 'innerWidth', { configurable: true, value: originalInnerWidth })
    Object.defineProperty(window, 'innerHeight', { configurable: true, value: originalInnerHeight })
  })
})
