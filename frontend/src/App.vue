<template>
  <!-- SVG defs — строго по прототипу shared/svg-defs.html -->
  <svg class="svg-defs" width="0" height="0" aria-hidden="true">
    <defs>
      <radialGradient id="brassGrad" cx="35%" cy="30%" r="75%">
        <stop offset="0%"   stop-color="#f0d78c"/>
        <stop offset="45%"  stop-color="#c9923a"/>
        <stop offset="100%" stop-color="#5a3a18"/>
      </radialGradient>
      <radialGradient id="copperGrad" cx="35%" cy="30%" r="75%">
        <stop offset="0%"   stop-color="#e8b87c"/>
        <stop offset="50%"  stop-color="#9b5028"/>
        <stop offset="100%" stop-color="#3a1a08"/>
      </radialGradient>
      <symbol id="gear-12" viewBox="-60 -60 120 120">
        <g class="gear-fill">
          <rect x="-7" y="-58" width="14" height="14" rx="2"/>
          <g transform="rotate(30)"><rect  x="-7" y="-58" width="14" height="14" rx="2"/></g>
          <g transform="rotate(60)"><rect  x="-7" y="-58" width="14" height="14" rx="2"/></g>
          <g transform="rotate(90)"><rect  x="-7" y="-58" width="14" height="14" rx="2"/></g>
          <g transform="rotate(120)"><rect x="-7" y="-58" width="14" height="14" rx="2"/></g>
          <g transform="rotate(150)"><rect x="-7" y="-58" width="14" height="14" rx="2"/></g>
          <g transform="rotate(180)"><rect x="-7" y="-58" width="14" height="14" rx="2"/></g>
          <g transform="rotate(210)"><rect x="-7" y="-58" width="14" height="14" rx="2"/></g>
          <g transform="rotate(240)"><rect x="-7" y="-58" width="14" height="14" rx="2"/></g>
          <g transform="rotate(270)"><rect x="-7" y="-58" width="14" height="14" rx="2"/></g>
          <g transform="rotate(300)"><rect x="-7" y="-58" width="14" height="14" rx="2"/></g>
          <g transform="rotate(330)"><rect x="-7" y="-58" width="14" height="14" rx="2"/></g>
        </g>
        <circle r="46" class="gear-fill"/>
        <circle r="38" fill="none" stroke="#5a3a18" stroke-width="1" stroke-dasharray="2 3" opacity="0.6"/>
        <g stroke="#5a3a18" stroke-width="3" stroke-linecap="round">
          <line x1="-34" y1="0"   x2="-14" y2="0"/>
          <line x1="14"  y1="0"   x2="34"  y2="0"/>
          <line x1="0"   y1="-34" x2="0"   y2="-14"/>
          <line x1="0"   y1="14"  x2="0"   y2="34"/>
        </g>
        <circle r="14" fill="url(#copperGrad)" stroke="#3a1a08" stroke-width="1.5"/>
        <circle r="3" fill="#2a1a0a"/>
      </symbol>
      <symbol id="gear-8" viewBox="-50 -50 100 100">
        <g class="gear-fill">
          <rect x="-6" y="-48" width="12" height="12" rx="2"/>
          <g transform="rotate(45)"><rect  x="-6" y="-48" width="12" height="12" rx="2"/></g>
          <g transform="rotate(90)"><rect  x="-6" y="-48" width="12" height="12" rx="2"/></g>
          <g transform="rotate(135)"><rect x="-6" y="-48" width="12" height="12" rx="2"/></g>
          <g transform="rotate(180)"><rect x="-6" y="-48" width="12" height="12" rx="2"/></g>
          <g transform="rotate(225)"><rect x="-6" y="-48" width="12" height="12" rx="2"/></g>
          <g transform="rotate(270)"><rect x="-6" y="-48" width="12" height="12" rx="2"/></g>
          <g transform="rotate(315)"><rect x="-6" y="-48" width="12" height="12" rx="2"/></g>
        </g>
        <circle r="38" class="gear-fill"/>
        <circle r="30" fill="none" stroke="#5a3a18" stroke-width="1" stroke-dasharray="2 3" opacity="0.6"/>
        <circle r="10" fill="url(#copperGrad)" stroke="#3a1a08" stroke-width="1.5"/>
        <circle r="2.5" fill="#2a1a0a"/>
      </symbol>
      <symbol id="pulsar-logo" viewBox="0 0 64 64">
        <rect x="2" y="2" width="60" height="60" rx="10" fill="url(#brassGrad)" stroke="#5a3a18" stroke-width="2"/>
        <rect x="5" y="5" width="54" height="54" rx="8" fill="none" stroke="#3a2008" stroke-width="0.8" stroke-dasharray="2 2"/>
        <circle cx="9"  cy="9"  r="2" fill="#5a3a18"/>
        <circle cx="55" cy="9"  r="2" fill="#5a3a18"/>
        <circle cx="9"  cy="55" r="2" fill="#5a3a18"/>
        <circle cx="55" cy="55" r="2" fill="#5a3a18"/>
        <text x="32" y="46" text-anchor="middle"
              font-family="IM Fell English SC, Cinzel, serif"
              font-weight="700" font-size="38" fill="#2a1a0a">P</text>
      </symbol>
    </defs>
  </svg>

  <AppPreloader v-if="loading" @done="loading = false" />

  <div v-else class="app" :class="{ 'app--steampunk': isSteampunk }">
    <!-- Steampunk: titlebar -->
    <div v-if="isSteampunk" class="sp-titlebar">
      <div class="sp-titlebar__logo">
        <span class="sp-titlebar__badge">P</span>
        <span>PULSAR<em>AI</em></span>
      </div>
      <div class="sp-titlebar__title">— THE CLOCKWORK COURIER · {{ page === 'chat' ? 'НОВЫЙ ЧАТ' : 'НАСТРОЙКИ' }} —</div>
      <div class="sp-titlebar__controls">
        <button class="sp-win-btn">─</button>
        <button class="sp-win-btn">□</button>
        <button class="sp-win-btn sp-win-btn--close">✕</button>
      </div>
    </div>

    <div class="app__workspace">
      <TheSidebar ref="sidebarRef" @open-settings="page = 'settings'" />
      <div
        v-if="sidebarRef?.isOpen"
        class="sb-overlay visible"
        @click="sidebarRef?.toggle()"
      />
      <button
        class="sb-toggle"
        :class="{ 'mobile-open': sidebarRef?.isOpen, 'settings-open': page === 'settings', 'sb-toggle--collapsed': sidebarCollapsed }"
        :title="sidebarCollapsed ? 'Развернуть' : 'Свернуть'"
        @click="sidebarRef?.toggle()"
      >
        {{ arrowDirection }}
      </button>

      <main class="main">
        <ChatView
          v-if="page === 'chat'"
          v-model:tune-open="tuneOpen"
          @open-settings="page = 'settings'"
        />
        <SettingsView v-else-if="page === 'settings'" @back="page = 'chat'" />
      </main>

      <TheRightPanel
        v-if="page === 'chat'"
        :open="tuneOpen"
        @close="tuneOpen = false"
      />
    </div>

    <!-- Steampunk: statusbar -->
    <div v-if="isSteampunk" class="sp-statusbar">
      <span class="sp-statusbar__dot"></span>
      <span>СИСТЕМА ИСПРАВНА</span>
      <span class="sp-statusbar__spacer"></span>
      <span>VseLLM · подключено</span>
      <span>·</span>
      <span>{{ new Date().toLocaleDateString('ru', {day:'2-digit',month:'2-digit',year:'numeric'}).replace(/\//g,'·') }} · {{ new Date().toLocaleTimeString('ru', {hour:'2-digit',minute:'2-digit'}) }}</span>
    </div>

    <!-- Corner gears -->
    <template v-if="isSteampunk">
      <svg class="corner-gear tl anim-spin-slow" viewBox="-60 -60 120 120"><use href="#gear-12"/></svg>
      <svg class="corner-gear tr anim-spin-rev"  viewBox="-60 -60 120 120"><use href="#gear-12"/></svg>
      <svg class="corner-gear bl anim-spin-rev"  viewBox="-50 -50 100 100"><use href="#gear-8"/></svg>
      <svg class="corner-gear br anim-spin-slow" viewBox="-50 -50 100 100"><use href="#gear-8"/></svg>
    </template>
  </div>

  <AppToast />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTheme } from '@/composables/useTheme'
import AppPreloader from '@/components/AppPreloader.vue'
import AppToast from '@/components/AppToast.vue'
import TheSidebar from '@/components/TheSidebar.vue'
import TheRightPanel from '@/components/TheRightPanel.vue'
import ChatView from '@/views/ChatView.vue'
import SettingsView from '@/views/SettingsView.vue'

const { initTheme, currentThemeId } = useTheme()
initTheme()

const isSteampunk = computed(() => currentThemeId.value === 'steampunk')

const loading = ref(true)
const page = ref<'chat' | 'settings'>('chat')
const tuneOpen = ref(false)
const sidebarRef = ref<InstanceType<typeof TheSidebar> | null>(null)
const sidebarCollapsed = computed(() => sidebarRef.value?.collapsed ?? false)
const isMobile = computed(() => window.innerWidth < 768)
const arrowDirection = computed(() => {
  if (isMobile.value) {
    console.log(!sidebarRef.value?.isOpen, sidebarCollapsed.value, 1)
    return !sidebarRef.value?.isOpen ? '›' : '‹'
  }
  return sidebarCollapsed ? '›' : '‹'
})
</script>

<style>
.svg-defs { position: absolute; }
.app {
  display: flex; flex-direction: column; height: 100vh; position: relative;
  overflow: hidden;
}
.app__workspace {
  display: flex; flex: 1; overflow: hidden; position: relative;
}
.main {
  flex: 1; display: flex; flex-direction: column; overflow: hidden;
  min-width: 0;
}
.sb-toggle {
  position: fixed; top: 50%; z-index: 200;
  left: 260px;
  transform: translateY(-50%) translateX(-50%);
  width: 20px; height: 40px; border-radius: 0 8px 8px 0;
  background: var(--bg-panel); border: 1px solid var(--brd); border-left: none;
  color: var(--t2); font-size: 18px; font-weight: 200;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  padding: 0; line-height: 1;
  box-shadow: 2px 0 8px rgba(0,0,0,0.3);
  transition: left .2s ease, color .15s, background .15s;
}
.sb-toggle--collapsed { left: 58px; }
.sb-toggle.settings-open { display: none; }
.sb-toggle:hover { color: var(--t1); background: var(--bg-gh); }

/* ── Steampunk: titlebar ─────────────────────────── */
.sp-titlebar { display: none; }
.sp-statusbar { display: none; }

.app--steampunk {
  background: var(--tex-paper);
  background-color: var(--paper-1);
  border: 12px solid transparent;
  background-clip: padding-box;
  outline: 2px solid var(--brass-2);
  outline-offset: -14px;
  box-shadow:
    var(--shadow-deep),
    inset 0 0 60px rgba(74, 44, 24, 0.35),
    inset 0 0 200px rgba(184, 138, 60, 0.08);
}
.app--steampunk .sp-titlebar {
  display: flex;
  align-items: center;
  height: var(--titlebar-h);
  background: var(--tex-wood);
  border-bottom: 2px solid var(--brass-2);
  padding: 0 12px;
  position: relative;
  z-index: 10;
  flex-shrink: 0;
  box-shadow: inset 0 -1px 0 rgba(0,0,0,0.4), 0 2px 6px rgba(0,0,0,0.4);
}
.app--steampunk .sp-titlebar::after {
  content: '';
  position: absolute;
  left: 0; right: 0; bottom: -1px; height: 1px;
  background: linear-gradient(90deg, transparent, var(--brass-4) 50%, transparent);
}
.sp-titlebar__logo {
  display: flex; align-items: center; gap: 10px;
  font-family: var(--font-display);
  color: var(--paper-0);
  font-size: 13px;
  letter-spacing: 0.18em;
  text-shadow: 0 1px 0 rgba(0,0,0,0.6);
}
.sp-titlebar__logo em { font-style: normal; color: var(--brass-5); }
.sp-titlebar__badge {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--tex-brass);
  display: grid; place-items: center;
  box-shadow: 0 0 0 1px var(--brass-1), inset 0 1px 2px rgba(255,220,160,0.6);
  color: var(--ink-1);
  font-weight: 700;
  font-family: var(--font-display);
  font-size: 11px;
}
.sp-titlebar__title {
  position: absolute; left: 50%; transform: translateX(-50%);
  font-family: var(--font-display);
  color: var(--paper-0);
  letter-spacing: 0.35em;
  font-size: 13px;
  text-shadow: 0 1px 0 rgba(0,0,0,0.7);
}
.sp-titlebar__controls {
  margin-left: auto; display: flex; gap: 8px;
}
.sp-win-btn {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--tex-brass);
  border: 1px solid var(--brass-1);
  box-shadow: inset 0 1px 2px rgba(255,220,160,0.5), 0 1px 2px rgba(0,0,0,0.5);
  display: grid; place-items: center;
  color: var(--ink-1);
  cursor: pointer;
  font-size: 11px;
  line-height: 1;
}
.sp-win-btn--close {
  background: linear-gradient(180deg, #c87038, #6b3a1a);
  color: var(--paper-0);
}
.sp-win-btn:hover { filter: brightness(1.1); }

/* ── Steampunk: statusbar ────────────────────────── */
.app--steampunk .sp-statusbar {
  display: flex;
  align-items: center;
  height: var(--statusbar-h);
  background: var(--tex-wood);
  border-top: 2px solid var(--brass-2);
  padding: 0 16px;
  gap: 18px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--paper-0);
  text-shadow: 0 1px 0 rgba(0,0,0,0.6);
  letter-spacing: 0.08em;
  z-index: 10;
  flex-shrink: 0;
  box-shadow: 0 -2px 6px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,220,160,0.2);
}
.sp-statusbar__dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #cfe8b9, var(--verdigris));
  box-shadow: 0 0 6px var(--verdigris-2), 0 0 0 1px rgba(0,0,0,0.4);
}
.sp-statusbar__spacer { flex: 1; }

/* ── Steampunk: wooden frame rivets ──────────────── */
.app--steampunk::before,
.app--steampunk::after {
  content: '';
  position: absolute;
  inset: 4px;
  pointer-events: none;
  z-index: 50;
}
.app--steampunk::before {
  background:
    radial-gradient(circle at 12px 12px, var(--brass-4) 0 4px, var(--brass-1) 5px 6px, transparent 7px),
    radial-gradient(circle at calc(100% - 12px) 12px, var(--brass-4) 0 4px, var(--brass-1) 5px 6px, transparent 7px),
    radial-gradient(circle at 12px calc(100% - 12px), var(--brass-4) 0 4px, var(--brass-1) 5px 6px, transparent 7px),
    radial-gradient(circle at calc(100% - 12px) calc(100% - 12px), var(--brass-4) 0 4px, var(--brass-1) 5px 6px, transparent 7px);
}
.app--steampunk::after {
  background:
    radial-gradient(ellipse at center, transparent 55%, rgba(74,44,24,0.25) 100%);
  z-index: 1;
}

/* ── Responsive breakpoints ─────────────────────── */

/* Legacy desktop / laptops (1024px - 1440px) */
@media (max-width: 1440px) {
  :root {
    --sw: 240px;
    --rw: 260px;
  }
}

/* Tablet (768px - 1024px) */
@media (max-width: 1024px) {
  :root {
    --sw: 220px;
    --rw: 0px;
  }

  .sb-toggle {
    width: 18px;
    height: 36px;
    font-size: 16px;
  }
}

/* Tablet portrait */
@media (max-width: 1024px) and (orientation: portrait) {
  :root {
    --sw: 280px;
  }
}

/* Mobile (< 768px) */
@media (max-width: 768px) {
  :root {
    --sw: 0px;
    --rw: 0px;
  }

  .app__workspace {
    position: relative;
  }

  /* Sidebar becomes overlay on mobile */
  .sb {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sb.open {
    transform: translateX(0);
  }

  /* Overlay backdrop */
  .sb-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 99;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s ease;
  }

  .sb-overlay.visible {
    opacity: 1;
    visibility: visible;
  }

  .sb-toggle {
    left: 8px;
    transform: translateY(-50%);
    border-radius: 8px;
    border: 1px solid var(--brd);
    border-left: 1px solid var(--brd);
    width: 32px;
    height: 32px;
    font-size: 16px;
    z-index: 201;
    transition: left 0.3s ease, transform 0.3s ease;
  }

  .sb-toggle.mobile-open {
    left: 210px;
  }

  .main {
    padding-left: 0;
  }
}

/* Mobile landscape */
@media (max-width: 768px) and (orientation: landscape) {
  :root {
    --sw: 200px;
  }

  .sb {
    width: var(--sw);
  }
}

/* Small mobile (< 480px) */
@media (max-width: 480px) {
  :root {
    --r: 10px;
    --rs: 6px;
  }

  .sb-toggle {
    width: 16px;
    height: 32px;
    font-size: 14px;
  }
}

/* Touch devices - larger touch targets */
@media (hover: none) and (pointer: coarse) {
  .sb-toggle {
    width: 44px;
    height: 44px;
  }
}

/* Old monitors 4:3 aspect ratio */
@media (min-aspect-ratio: 4/3) and (max-aspect-ratio: 5/4) {
  :root {
    --sw: 220px;
    --rw: 240px;
  }
}

/* Old monitors 5:4 aspect ratio */
@media (min-aspect-ratio: 5/4) and (max-aspect-ratio: 16/10) {
  :root {
    --sw: 240px;
    --rw: 260px;
  }
}

/* Limited height screens */
@media (max-height: 900px) {
  .sp-titlebar { height: 36px; }
  .sp-statusbar { height: 26px; }
}

@media (max-height: 768px) {
  :root {
    --sw: 200px;
    --rw: 220px;
  }
}
</style>
