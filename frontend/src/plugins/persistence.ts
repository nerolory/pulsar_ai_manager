import type { PiniaPluginContext } from 'pinia'

const STORAGE_VERSION = 'v4'
const VERSION_KEY = 'pulsarai:version'

const PERSIST_STORES: Record<string, string[]> = {
  chat: ['params'],
}

/** Call once before createPinia() — wipes stale data on version mismatch */
export function initStorage() {
  if (localStorage.getItem(VERSION_KEY) !== STORAGE_VERSION) {
    Object.keys(PERSIST_STORES).forEach((id) => localStorage.removeItem(`pulsarai:${id}`))
    localStorage.setItem(VERSION_KEY, STORAGE_VERSION)
  }
  // Clear old chat data that was previously persisted
  localStorage.removeItem('pulsarai:chat')
}

export function persistencePlugin({ store }: PiniaPluginContext) {
  const keys = PERSIST_STORES[store.$id]
  if (!keys) return

  const storageKey = `pulsarai:${store.$id}`

  try {
    const saved = localStorage.getItem(storageKey)
    if (saved) {
      const parsed = JSON.parse(saved)
      store.$patch((state) => {
        keys.forEach((k) => {
          if (k in parsed) (state as Record<string, unknown>)[k] = parsed[k]
        })
      })
    }
  } catch { /* ignore corrupt storage */ }

  store.$subscribe(() => {
    try {
      const snapshot: Record<string, unknown> = {}
      keys.forEach((k) => { snapshot[k] = (store.$state as Record<string, unknown>)[k] })
      localStorage.setItem(storageKey, JSON.stringify(snapshot))
    } catch { /* quota exceeded or SSR */ }
  }, { detached: true })
}
