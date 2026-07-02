import type { LocaleData } from '@/types'
import en from './en.json'
import ru from './ru.json'

const localeModules: Record<string, LocaleData> = {
  en: en as LocaleData,
  ru: ru as LocaleData,
}

const localeCache = new Map<string, LocaleData>()

export async function loadLocale(code: string): Promise<LocaleData> {
  if (localeCache.has(code)) {
    return localeCache.get(code)!
  }

  const data = localeModules[code] ?? localeModules.en ?? { name: code }
  localeCache.set(code, data)
  return data
}

export function getAvailableLanguages(): Array<{ code: string; name: string }> {
  return Object.entries(localeModules).map(([code, data]) => ({
    code,
    name: data.name || code,
  }))
}

export function detectBrowserLanguage(): string {
  const browserLang = navigator.language.split('-')[0]
  const available = getAvailableLanguages()
  const matched = available.find((lang) => lang.code === browserLang)
  return matched?.code || 'en'
}
