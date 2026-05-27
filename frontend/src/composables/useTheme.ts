import { ref } from 'vue'
import { THEMES, DEFAULT_THEME_ID, type Theme } from '@/themes'

export const STORAGE_KEY = 'llm-chat-theme'

const currentThemeId = ref<string>(
  localStorage.getItem(STORAGE_KEY) ?? DEFAULT_THEME_ID
)

let hljsLinkEl: HTMLLinkElement | null = null
let themeCssLinkEl: HTMLLinkElement | null = null

// Theme-specific CSS files (Vite will bundle them)
const THEME_CSS_MODULES: Record<string, () => Promise<unknown>> = {
  steampunk: () => import('@/themes/steampunk/steampunk.scss'),
}
let loadedThemeCss: string | null = null

async function loadThemeCss(themeId: string) {
  if (loadedThemeCss === themeId) return
  // Remove previous theme CSS link if any
  if (themeCssLinkEl) {
    themeCssLinkEl.remove()
    themeCssLinkEl = null
  }
  if (THEME_CSS_MODULES[themeId]) {
    await THEME_CSS_MODULES[themeId]()
  }
  loadedThemeCss = themeId
}

function applyTheme(theme: Theme) {
  const root = document.documentElement
  const v = theme.vars

  root.style.setProperty('--accent',        v.accent)
  root.style.setProperty('--accent-l',      v.accentL)
  root.style.setProperty('--accent-dim',    v.accentDim)
  root.style.setProperty('--accent-border', v.accentBorder)
  root.style.setProperty('--bg',            v.bg)
  root.style.setProperty('--bg-s',          v.bgS)
  root.style.setProperty('--bg-g',          v.bgG)
  root.style.setProperty('--bg-gh',         v.bgGh)
  root.style.setProperty('--bg-panel',      v.bgPanel)
  root.style.setProperty('--brd',           v.brd)
  root.style.setProperty('--brd-a',         v.brdA)
  root.style.setProperty('--t1',            v.t1)
  root.style.setProperty('--t2',            v.t2)
  root.style.setProperty('--t3',            v.t3)
  root.style.setProperty('--blur',          v.blur)
  root.style.setProperty('--shadow-pop',    v.shadowPop)
  root.style.setProperty('--body-gradient',     v.bodyGradient)
  root.style.setProperty('--code-inline-color', v.codeInlineColor)

  // data-theme attribute for light/dark body::before
  root.setAttribute('data-theme', theme.id)
  root.setAttribute('data-dark', theme.dark ? '1' : '0')

  // hljs stylesheet swap
  const hljsHref = `https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/${v.hljsStyle}.min.css`
  if (!hljsLinkEl) {
    hljsLinkEl = document.querySelector('link[data-hljs]') as HTMLLinkElement | null
    if (!hljsLinkEl) {
      hljsLinkEl = document.createElement('link')
      hljsLinkEl.rel = 'stylesheet'
      hljsLinkEl.setAttribute('data-hljs', '1')
      document.head.appendChild(hljsLinkEl)
    }
  }
  if (hljsLinkEl.href !== hljsHref) {
    hljsLinkEl.href = hljsHref
  }
}

export function useTheme() {
  const themes = THEMES.filter(theme => theme.id !== 'steampunk')

  const currentTheme = ref<Theme>(
    THEMES.find(theme => theme.id === currentThemeId.value) ?? THEMES[0]
  )

  async function setTheme(id: string) {
    const theme = THEMES.find(theme => theme.id === id)
    if (!theme) return
    currentThemeId.value = id
    currentTheme.value = theme
    localStorage.setItem(STORAGE_KEY, id)
    await loadThemeCss(id)
    applyTheme(theme)
  }

  async function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY) ?? DEFAULT_THEME_ID
    const theme = THEMES.find(theme => theme.id === saved) ?? THEMES[0]
    currentThemeId.value = theme.id
    currentTheme.value = theme
    await loadThemeCss(theme.id)
    applyTheme(theme)
  }

  return { themes, currentTheme, currentThemeId, setTheme, initTheme }
}
