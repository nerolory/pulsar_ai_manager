import { ref, computed } from 'vue'
import { useI18n } from '@/composables/useI18n'

interface Preset {
  icon: string
  label: string
  text: string
  usedAt?: number
}

const STORAGE_KEY = 'pulsarai:recent-presets'
const MAX_RECENT = 10

export function usePresets() {
  const { translations } = useI18n()
  const recentPresets = ref<Preset[]>([])

  const defaultPresets = computed<Preset[]>(() => {
    const list = translations.value?.presets?.list
    if (!Array.isArray(list)) return []
    return list.map((item) => ({
      icon: String(item.icon ?? ''),
      label: String(item.label ?? ''),
      text: String(item.text ?? ''),
    }))
  })

  function loadRecentPresets() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        recentPresets.value = parsed || []
      }
    } catch {
      recentPresets.value = []
    }
  }

  function saveRecentPreset(preset: Preset) {
    const presetWithTime = { ...preset, usedAt: Date.now() }

    recentPresets.value = recentPresets.value.filter((item) => item.text !== preset.text)
    recentPresets.value.unshift(presetWithTime)

    if (recentPresets.value.length > MAX_RECENT) {
      recentPresets.value = recentPresets.value.slice(0, MAX_RECENT)
    }

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(recentPresets.value))
    } catch {
      // Quota exceeded or other storage error
    }
  }

  const presets = computed(() => {
    const recent = recentPresets.value.map((preset) => ({
      icon: preset.icon,
      label: preset.label,
      text: preset.text,
    }))
    const defaultsWithoutRecent = defaultPresets.value.filter(
      (defaultPreset) => !recentPresets.value.some((recentPreset) => recentPreset.text === defaultPreset.text),
    )
    return [...recent, ...defaultsWithoutRecent]
  })

  return {
    presets,
    loadRecentPresets,
    saveRecentPreset,
  }
}
