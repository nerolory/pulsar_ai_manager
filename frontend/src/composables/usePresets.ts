import { ref, computed } from 'vue'

interface Preset {
  icon: string
  label: string
  text: string
  usedAt?: number
}

const DEFAULT_PRESETS: Preset[] = [
  { icon: '🚫', label: 'Не выдумывай', text: 'Не выдумывай. Отвечай только фактами. Если не знаешь — так и скажи.' },
  { icon: '⚡', label: 'Отвечай кратко', text: 'Отвечай максимально кратко — одно-два предложения.' },
  { icon: '🎓', label: 'Объясни просто', text: 'Объясняй как будто я новичок. Избегай сложных терминов.' },
  { icon: '🇷🇺', label: 'Только русский', text: 'Отвечай только на русском языке.' },
  { icon: '💻', label: 'Режим разработчика', text: 'Ты опытный senior-разработчик. Приводи примеры кода.' },
  { icon: '🔍', label: 'Критикуй меня', text: 'Проверяй мои утверждения. Указывай на ошибки прямо.' },
  { icon: '📋', label: 'Отвечай списком', text: 'Отвечай в формате списка с пунктами.' },
]

const STORAGE_KEY = 'pulsarai:recent-presets'
const MAX_RECENT = 10

export function usePresets() {
  const recentPresets = ref<Preset[]>([])

  // Load recent presets from localStorage
  function loadRecentPresets() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        recentPresets.value = parsed || []
      }
    } catch {
      // Ignore corrupt storage
      recentPresets.value = []
    }
  }

  // Save preset to recent list
  function saveRecentPreset(preset: Preset) {
    const presetWithTime = { ...preset, usedAt: Date.now() }
    
    // Remove if already exists
    recentPresets.value = recentPresets.value.filter(item => item.text !== preset.text)
    
    // Add to beginning
    recentPresets.value.unshift(presetWithTime)
    
    // Keep only MAX_RECENT
    if (recentPresets.value.length > MAX_RECENT) {
      recentPresets.value = recentPresets.value.slice(0, MAX_RECENT)
    }
    
    // Save to localStorage
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(recentPresets.value))
    } catch {
      // Quota exceeded or other storage error
    }
  }

  // Get combined presets (recent first, then defaults)
  const presets = computed(() => {
    const recent = recentPresets.value.map(preset => ({ icon: preset.icon, label: preset.label, text: preset.text }))
    const defaultsWithoutRecent = DEFAULT_PRESETS.filter(
      defaultPreset => !recentPresets.value.some(recentPreset => recentPreset.text === defaultPreset.text)
    )
    return [...recent, ...defaultsWithoutRecent]
  })

  return {
    presets,
    loadRecentPresets,
    saveRecentPreset,
  }
}
