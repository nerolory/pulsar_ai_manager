export interface ThemeVars {
  accent: string
  accentL: string
  accentDim: string
  accentBorder: string
  bg: string
  bgS: string
  bgG: string
  bgGh: string
  bgPanel: string
  brd: string
  brdA: string
  t1: string
  t2: string
  t3: string
  blur: string
  shadowPop: string
  bodyGradient: string
  codeInlineColor: string
  hljsStyle: 'github-dark' | 'github' | 'base16-tomorrow' | 'atom-one-light'
}

export interface Theme {
  id: string
  name: string
  description: string
  dark: boolean
  vars: ThemeVars
}

export const THEMES: Theme[] = [
  {
    id: 'dark-space',
    name: 'Dark Space',
    description: 'Тёмный с фиолетовым акцентом',
    dark: true,
    vars: {
      accent:       '#6366F1',
      accentL:      '#818CF8',
      accentDim:    'rgba(99,102,241,0.18)',
      accentBorder: 'rgba(99,102,241,0.45)',
      bg:           '#0a0a0f',
      bgS:          'rgba(255,255,255,0.06)',
      bgG:          'rgba(255,255,255,0.08)',
      bgGh:         'rgba(255,255,255,0.13)',
      bgPanel:      '#13131f',
      brd:          'rgba(255,255,255,0.13)',
      brdA:         'rgba(99,102,241,0.55)',
      t1:           '#F1F1F5',
      t2:           '#A9A9C0',
      t3:           '#6B6B85',
      blur:         'blur(20px)',
      shadowPop:    '0 20px 60px rgba(0,0,0,0.6),0 0 0 1px rgba(255,255,255,0.07)',
      bodyGradient: 'radial-gradient(ellipse 60% 50% at 15% 20%,rgba(99,102,241,0.12) 0%,transparent 60%),radial-gradient(ellipse 50% 40% at 85% 75%,rgba(139,92,246,0.10) 0%,transparent 55%)',
      codeInlineColor: '#e2b96f',
      hljsStyle:    'github-dark',
    },
  },
  {
    id: 'neutral-gray',
    name: 'Neutral Gray',
    description: 'Нейтральный серый, без лишнего',
    dark: true,
    vars: {
      accent:       '#64748B',
      accentL:      '#94A3B8',
      accentDim:    'rgba(100,116,139,0.18)',
      accentBorder: 'rgba(100,116,139,0.45)',
      bg:           '#111318',
      bgS:          'rgba(255,255,255,0.05)',
      bgG:          'rgba(255,255,255,0.07)',
      bgGh:         'rgba(255,255,255,0.11)',
      bgPanel:      '#1a1d24',
      brd:          'rgba(255,255,255,0.10)',
      brdA:         'rgba(148,163,184,0.5)',
      t1:           '#E2E8F0',
      t2:           '#94A3B8',
      t3:           '#4B5563',
      blur:         'blur(16px)',
      shadowPop:    '0 16px 48px rgba(0,0,0,0.55),0 0 0 1px rgba(255,255,255,0.06)',
      bodyGradient: 'none',
      codeInlineColor: '#e2b96f',
      hljsStyle:    'github-dark',
    },
  },
  {
    id: 'light-clean',
    name: 'Light Clean',
    description: 'Светлый, минималистичный',
    dark: false,
    vars: {
      accent:       '#4F46E5',
      accentL:      '#6366F1',
      accentDim:    'rgba(79,70,229,0.10)',
      accentBorder: 'rgba(79,70,229,0.30)',
      bg:           '#F8F9FC',
      bgS:          'rgba(0,0,0,0.04)',
      bgG:          'rgba(0,0,0,0.06)',
      bgGh:         'rgba(0,0,0,0.09)',
      bgPanel:      '#FFFFFF',
      brd:          'rgba(0,0,0,0.10)',
      brdA:         'rgba(79,70,229,0.40)',
      t1:           '#111827',
      t2:           '#4B5563',
      t3:           '#9CA3AF',
      blur:         'blur(16px)',
      shadowPop:    '0 16px 48px rgba(0,0,0,0.12),0 0 0 1px rgba(0,0,0,0.06)',
      bodyGradient: 'radial-gradient(ellipse 60% 50% at 15% 20%,rgba(79,70,229,0.06) 0%,transparent 60%),radial-gradient(ellipse 50% 40% at 85% 75%,rgba(139,92,246,0.05) 0%,transparent 55%)',
      codeInlineColor: '#6366F1',
      hljsStyle:    'github',
    },
  },
  {
    id: 'ocean-dark',
    name: 'Ocean Dark',
    description: 'Тёмно-синий, глубокий',
    dark: true,
    vars: {
      accent:       '#0EA5E9',
      accentL:      '#38BDF8',
      accentDim:    'rgba(14,165,233,0.15)',
      accentBorder: 'rgba(14,165,233,0.40)',
      bg:           '#04091a',
      bgS:          'rgba(255,255,255,0.05)',
      bgG:          'rgba(255,255,255,0.07)',
      bgGh:         'rgba(255,255,255,0.11)',
      bgPanel:      '#0a1128',
      brd:          'rgba(255,255,255,0.10)',
      brdA:         'rgba(56,189,248,0.5)',
      t1:           '#E0F2FE',
      t2:           '#7DD3FC',
      t3:           '#334E68',
      blur:         'blur(20px)',
      shadowPop:    '0 20px 60px rgba(0,0,0,0.7),0 0 0 1px rgba(14,165,233,0.12)',
      bodyGradient: 'radial-gradient(ellipse 60% 50% at 15% 20%,rgba(14,165,233,0.12) 0%,transparent 60%),radial-gradient(ellipse 50% 40% at 85% 75%,rgba(6,182,212,0.08) 0%,transparent 55%)',
      codeInlineColor: '#38BDF8',
      hljsStyle:    'github-dark',
    },
  },
  {
    id: 'forest',
    name: 'Forest',
    description: 'Зелёный, природный',
    dark: true,
    vars: {
      accent:       '#10B981',
      accentL:      '#34D399',
      accentDim:    'rgba(16,185,129,0.15)',
      accentBorder: 'rgba(16,185,129,0.40)',
      bg:           '#060f0a',
      bgS:          'rgba(255,255,255,0.05)',
      bgG:          'rgba(255,255,255,0.07)',
      bgGh:         'rgba(255,255,255,0.11)',
      bgPanel:      '#0d1f14',
      brd:          'rgba(255,255,255,0.10)',
      brdA:         'rgba(52,211,153,0.5)',
      t1:           '#ECFDF5',
      t2:           '#6EE7B7',
      t3:           '#2D5A3D',
      blur:         'blur(20px)',
      shadowPop:    '0 20px 60px rgba(0,0,0,0.7),0 0 0 1px rgba(16,185,129,0.10)',
      bodyGradient: 'radial-gradient(ellipse 60% 50% at 15% 20%,rgba(16,185,129,0.10) 0%,transparent 60%),radial-gradient(ellipse 50% 40% at 85% 75%,rgba(5,150,105,0.08) 0%,transparent 55%)',
      codeInlineColor: '#34D399',
      hljsStyle:    'github-dark',
    },
  },
  {
    id: 'light-warm',
    name: 'Light Warm',
    description: 'Тёплый светлый, кремовый',
    dark: false,
    vars: {
      accent:       '#D97706',
      accentL:      '#F59E0B',
      accentDim:    'rgba(217,119,6,0.10)',
      accentBorder: 'rgba(217,119,6,0.30)',
      bg:           '#FFFBF5',
      bgS:          'rgba(0,0,0,0.04)',
      bgG:          'rgba(0,0,0,0.05)',
      bgGh:         'rgba(0,0,0,0.08)',
      bgPanel:      '#FFFFFF',
      brd:          'rgba(0,0,0,0.10)',
      brdA:         'rgba(217,119,6,0.35)',
      t1:           '#1C1917',
      t2:           '#57534E',
      t3:           '#A8A29E',
      blur:         'blur(16px)',
      shadowPop:    '0 16px 48px rgba(0,0,0,0.10),0 0 0 1px rgba(0,0,0,0.06)',
      bodyGradient: 'radial-gradient(ellipse 60% 50% at 15% 20%,rgba(251,191,36,0.08) 0%,transparent 60%),radial-gradient(ellipse 50% 40% at 85% 75%,rgba(234,179,8,0.06) 0%,transparent 55%)',
      codeInlineColor: '#D97706',
      hljsStyle:    'atom-one-light',
    },
  },
  {
    id: 'steampunk',
    name: 'Steampunk',
    description: 'Старая газета, шестерни и верёвки',
    dark: false,
    vars: {
      accent:          '#B87333',
      accentL:         '#CD9B5A',
      accentDim:       'rgba(184,115,51,0.15)',
      accentBorder:    'rgba(184,115,51,0.50)',
      bg:              '#E8DFC0',
      bgS:             'rgba(101,67,33,0.08)',
      bgG:             'rgba(101,67,33,0.12)',
      bgGh:            'rgba(101,67,33,0.18)',
      bgPanel:         '#D4C49A',
      brd:             'rgba(101,67,33,0.35)',
      brdA:            'rgba(184,115,51,0.70)',
      t1:              '#2C1A0E',
      t2:              '#5C3D1E',
      t3:              '#8B6347',
      blur:            'blur(0px)',
      shadowPop:       '0 4px 16px rgba(0,0,0,0.35),0 0 0 1px rgba(101,67,33,0.2)',
      bodyGradient:    'none',
      codeInlineColor: '#8B4513',
      hljsStyle:       'atom-one-light',
    },
  },
]

export const DEFAULT_THEME_ID = 'dark-space'
