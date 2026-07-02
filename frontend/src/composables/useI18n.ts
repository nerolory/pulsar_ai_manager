import { ref, computed, watch } from 'vue'
import type { LocaleData } from '@/types'
import { loadLocale, getAvailableLanguages, detectBrowserLanguage } from '@/locales'

const STORAGE_KEY = 'pulsar_language'

const currentLanguage = ref<string>(localStorage.getItem(STORAGE_KEY) || detectBrowserLanguage())
const translations = ref<LocaleData | null>(null)
const isLoading = ref(true)
const availableLanguages = computed(() => getAvailableLanguages())

// Load initial locale
loadLocale(currentLanguage.value).then(data => {
  translations.value = data
  isLoading.value = false
}).catch(error => {
  console.error('Failed to load initial locale:', error)
  isLoading.value = false
})

// Watch for language changes
watch(currentLanguage, async (newLang) => {
  isLoading.value = true
  translations.value = await loadLocale(newLang)
  isLoading.value = false
})

export function useI18n() {
  function setLanguage(lang: string) {
    currentLanguage.value = lang
    localStorage.setItem(STORAGE_KEY, lang)
  }

  function t(key: string, params?: Record<string, string | number>): string {
    if (!translations.value) return key
    const result = key.split('.').reduce<unknown>((obj, k) => {
      if (obj && typeof obj === 'object' && k in obj) {
        return (obj as Record<string, unknown>)[k]
      }
      return undefined
    }, translations.value as unknown)
    if (typeof result !== 'string') return key
    
    // Replace parameters in the translation string
    if (params) {
      return result.replace(/\{(\w+)\}/g, (match: string, paramKey: string) => {
        return String(params[paramKey] ?? match)
      })
    }
    return result
  }

  function parseErrorCode(
    errorCode: string,
    explicitParams?: Record<string, string | number>,
  ): string {
    const parts = errorCode.split(':')
    const code = parts[0]

    const params: Record<string, string | number> = { ...explicitParams }
    if (parts.length > 1 && params.provider === undefined) {
      params.provider = parts[1]
    }
    if (parts.length > 2 && params.model === undefined) {
      params.model = parts[2]
    }
    if (parts.length > 3 && params.error === undefined) {
      params.error = parts.slice(3).join(':')
    }

    const key = `errors.${code}`
    const translated = t(key, Object.keys(params).length ? params : undefined)

    return translated === key ? errorCode : translated
  }

  return {
    currentLanguage,
    availableLanguages,
    isLoading,
    translations,
    setLanguage,
    t,
    parseErrorCode,
  }
}
