<template>
  <!-- Steampunk splash — строго по прототипу 01-splash/index.html -->
  <div v-if="isSteampunk" class="splash">
    <!-- Декоративные шестерёнки (используют символы из App.vue) -->
    <svg class="bg-gear g1 anim-spin-slow"  viewBox="-60 -60 120 120"><use href="#gear-12"/></svg>
    <svg class="bg-gear g2 anim-spin-rev"   viewBox="-50 -50 100 100"><use href="#gear-8"/></svg>
    <svg class="bg-gear g3 anim-spin"       viewBox="-60 -60 120 120"><use href="#gear-12"/></svg>
    <svg class="bg-gear g4 anim-spin-rev"   viewBox="-50 -50 100 100"><use href="#gear-8"/></svg>

    <div class="splash__stage">
      <div class="splash__plate"></div>

      <div class="splash__logo">
        <div class="ring"></div>
        <div class="rivets"></div>
        <svg class="core" viewBox="0 0 64 64"><use href="#pulsar-logo"/></svg>
      </div>

      <div class="splash__brand">Pulsar<em>AI</em></div>
      <div class="splash__motto">«механический разум, заведённый ключом любопытства»</div>

      <div class="divider-ornate"></div>

      <div class="splash__bar"><div class="fill"></div></div>
      <div class="splash__status">
        {{ status }}
        <span class="splash__dots" aria-hidden="true"></span>
      </div>
    </div>
  </div>

  <!-- Default preloader for other themes -->
  <div v-else class="preloader">
    <div class="pre-logo">
      <div class="pre-icon">P</div>
      <div class="pre-name">Pulsar<span>AI</span></div>
    </div>
    <div class="pre-bar"><div class="pre-fill" /></div>
    <div class="pre-status">{{ status }}</div>
    <div class="pre-dots" aria-hidden="true"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { STORAGE_KEY } from '@/composables/useTheme'

const emit = defineEmits<{ done: [] }>()

const themeId = localStorage.getItem(STORAGE_KEY) ?? 'dark'
const isSteampunk = computed(() => themeId === 'steampunk')

const statuses = [
  'ИНИЦИАЛИЗАЦИЯ',
  'ЗАГРУЗКА КОНФИГУРАЦИИ',
  'ПОДКЛЮЧЕНИЕ К СЕРВИСАМ',
  'ПРОВЕРКА API-КЛЮЧЕЙ',
  'ГОТОВО',
]
const status = ref(statuses[0])

onMounted(() => {
  let i = 0
  const interval = setInterval(() => {
    i++
    if (i < statuses.length) status.value = statuses[i]
    if (i >= statuses.length - 1) clearInterval(interval)
  }, 500)
  setTimeout(() => emit('done'), 2800)
})
</script>

<style scoped>
/* ── Steampunk splash — pixel-perfect from 01-splash/index.html ── */
.splash {
  position: absolute; inset: 0;
  display: grid; place-items: center;
  background:
    radial-gradient(ellipse at 20% 10%, rgba(184,138,60,0.18), transparent 50%),
    radial-gradient(ellipse at 80% 90%, rgba(107,68,35,0.22), transparent 55%),
    radial-gradient(ellipse at 50% 50%, rgba(243,232,200,0.0), rgba(184,160,106,0.20)),
    repeating-linear-gradient(0deg, rgba(107,68,35,0.04) 0 1px, transparent 1px 3px),
    repeating-linear-gradient(90deg, rgba(107,68,35,0.03) 0 1px, transparent 1px 4px),
    linear-gradient(180deg, #f3e8c8, #e8dcc0 40%, #d9c89c);
  background-color: #e8dcc0;
  overflow: hidden;
  z-index: 9999;
}

.bg-gear { position: absolute; opacity: 0.45; pointer-events: none; }
.bg-gear.g1 { top: -60px; left: -60px; width: 280px; height: 280px; }
.bg-gear.g2 { top: 80px; right: -50px; width: 200px; height: 200px; }
.bg-gear.g3 { bottom: -70px; left: 25%; width: 240px; height: 240px; }
.bg-gear.g4 { bottom: 60px; right: 18%; width: 140px; height: 140px; }

.splash__stage {
  position: relative;
  width: 560px; padding: 48px 36px;
  text-align: center;
  z-index: 5;
}

.splash__plate {
  position: absolute; inset: 0;
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(243,232,200,0.85), rgba(217,200,156,0.85));
  border: 3px solid #8b6332;
  box-shadow:
    0 0 0 2px #6b4423,
    0 18px 40px rgba(74,44,24,0.45),
    inset 0 0 40px rgba(184,138,60,0.15);
  z-index: -1;
}
.splash__plate::before, .splash__plate::after {
  content: ''; position: absolute; inset: 8px;
  border: 1px dashed #8b6332;
  border-radius: 8px;
  pointer-events: none;
}
.splash__plate::after {
  background:
    radial-gradient(circle at 14px 14px, #d4a04a 0 3px, #5a3a18 4px 5px, transparent 6px),
    radial-gradient(circle at calc(100% - 14px) 14px, #d4a04a 0 3px, #5a3a18 4px 5px, transparent 6px),
    radial-gradient(circle at 14px calc(100% - 14px), #d4a04a 0 3px, #5a3a18 4px 5px, transparent 6px),
    radial-gradient(circle at calc(100% - 14px) calc(100% - 14px), #d4a04a 0 3px, #5a3a18 4px 5px, transparent 6px);
  border: none;
}

.splash__logo {
  position: relative;
  width: 140px; height: 140px;
  margin: 0 auto 22px;
  display: grid; place-items: center;
}
.splash__logo .ring {
  position: absolute; inset: 0;
  border: 3px solid #8b6332;
  border-radius: 50%;
  box-shadow:
    inset 0 0 0 2px #d4a04a,
    inset 0 0 30px rgba(74,44,24,0.4),
    0 6px 20px rgba(74,44,24,0.45);
  background: radial-gradient(circle at 30% 30%, #f3e8c8, #d9c89c 70%);
}
.splash__logo .ring::before {
  content: ''; position: absolute; inset: 8px;
  border: 1px dashed #8b6332; border-radius: 50%;
}
.splash__logo .rivets {
  position: absolute; inset: 0; border-radius: 50%;
  background:
    radial-gradient(circle at 50% 8px,  #d4a04a 0 3px, #5a3a18 4px 5px, transparent 6px),
    radial-gradient(circle at 50% calc(100% - 8px), #d4a04a 0 3px, #5a3a18 4px 5px, transparent 6px),
    radial-gradient(circle at 8px 50%, #d4a04a 0 3px, #5a3a18 4px 5px, transparent 6px),
    radial-gradient(circle at calc(100% - 8px) 50%, #d4a04a 0 3px, #5a3a18 4px 5px, transparent 6px);
}
.splash__logo .core {
  position: relative; z-index: 2;
  width: 86px; height: 86px;
}

.splash__brand {
  font-family: 'IM Fell English SC', 'Cinzel', Georgia, serif;
  font-size: 44px;
  letter-spacing: 0.22em;
  color: #2a1a0a;
  text-shadow: 0 1px 0 #f3e8c8;
}
.splash__brand em { font-style: normal; color: #9b5028; }
.splash__motto {
  font-family: 'IM Fell English', 'Cormorant Garamond', Georgia, serif;
  font-style: italic;
  color: #806244;
  letter-spacing: 0.06em;
  margin-top: 6px;
  font-size: 15px;
}

.divider-ornate {
  display: flex; align-items: center; gap: 12px;
  color: #8b6332;
  margin: 14px 0;
}
.divider-ornate::before, .divider-ornate::after {
  content: ''; flex: 1;
  border-top: 1px solid #8b6332;
  border-bottom: 1px solid #b8a06a;
  height: 3px;
}

.splash__bar {
  margin: 30px auto 14px;
  width: 360px; height: 18px;
  position: relative;
  background: linear-gradient(180deg, #d9c89c, #e8dcc0);
  border: 2px solid #5a3a18;
  border-radius: 999px;
  box-shadow: inset 0 2px 6px rgba(42,26,10,0.35), 0 0 0 2px #6b4423;
  overflow: hidden;
}
.splash__bar::before {
  content: ''; position: absolute; inset: 0;
  background: repeating-linear-gradient(90deg,
    rgba(74,44,24,0.18) 0 1px, transparent 1px 18px);
}
.splash__bar .fill {
  position: absolute; top: 0; bottom: 0; left: 0;
  width: 0;
  background: linear-gradient(180deg, #f0d78c, #b8863c 45%, #5a3a18);
  box-shadow: inset 0 1px 0 rgba(255,220,160,0.7), inset 0 -2px 4px rgba(0,0,0,0.4);
  animation: telegraph-bar 3.8s ease-in-out infinite;
}

.splash__status {
  font-family: 'Special Elite', 'Courier New', monospace;
  font-size: 13px;
  color: #5c4023;
  letter-spacing: 0.16em;
}
.splash__dots {
  display: inline-flex; gap: 6px; margin-left: 8px;
  vertical-align: middle;
  width: 6px; height: 6px; border-radius: 50%;
  background: #9b5028;
  box-shadow: 0 0 0 1px #5a3a18;
  animation: brass-shine 1.4s ease-in-out infinite;
  position: relative;
}
.splash__dots::before,
.splash__dots::after {
  content: '';
  position: absolute;
  width: 6px; height: 6px; border-radius: 50%;
  background: #9b5028;
  box-shadow: 0 0 0 1px #5a3a18;
  animation: brass-shine 1.4s ease-in-out infinite;
}
.splash__dots::before { left: -12px; animation-delay: 0s; }
.splash__dots::after { right: -12px; animation-delay: 0.4s; }

/* ── Default preloader ─────────────────────────────────── */
.preloader {
  position: fixed; inset: 0; z-index: 9999;
  background: var(--bg);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 28px;
}
.pre-logo { display: flex; align-items: center; gap: 12px; }
.pre-icon {
  width: 48px; height: 48px; border-radius: 14px;
  background: linear-gradient(135deg, var(--accent), #8B5CF6);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 800; color: #fff;
  box-shadow: 0 0 30px rgba(99,102,241,0.5);
  animation: pulse-icon 2s ease-in-out infinite;
}
@keyframes pulse-icon {
  0%,100% { box-shadow: 0 0 20px rgba(99,102,241,0.4); }
  50%     { box-shadow: 0 0 40px rgba(99,102,241,0.7); }
}
.pre-name { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; }
.pre-name span { color: var(--accent-l); }
.pre-status { font-size: 13px; color: var(--t3); letter-spacing: 0.5px; }
.pre-bar {
  width: 220px; height: 2px;
  background: rgba(255,255,255,0.06); border-radius: 1px; overflow: hidden;
}
.pre-fill {
  height: 100%; width: 0;
  background: linear-gradient(90deg, var(--accent), #8B5CF6);
  border-radius: 1px;
  animation: fill-bar 2.5s ease-in-out forwards;
}
@keyframes fill-bar {
  0%{width:0%} 30%{width:35%} 60%{width:65%} 85%{width:88%} 100%{width:100%}
}
.pre-dots {
  display: flex;
  gap: 6px;
  position: relative;
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--accent); opacity: 0.3;
  animation: dotpulse 1.4s infinite;
}
.pre-dots::before,
.pre-dots::after {
  content: '';
  position: absolute;
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--accent);
  opacity: 0.3;
  animation: dotpulse 1.4s infinite;
}
.pre-dots::before { left: -12px; animation-delay: 0s; }
.pre-dots::after { right: -12px; animation-delay: 0.4s; }
@keyframes dotpulse { 0%,60%,100%{opacity:.3} 30%{opacity:1} }

/* ── Responsive styles ──────────────────────────── */

/* Mobile (< 768px) */
@media (max-width: 768px) {
  .splash__stage { transform: scale(0.85); }
  .splash__brand { font-size: 22px; }
  .splash__motto { font-size: 10px; max-width: 260px; }
  .splash__status { font-size: 11px; }

  .preloader { gap: 20px; }
  .pre-logo { transform: scale(0.9); }
  .pre-bar { width: 180px; }
}

/* Small mobile (< 480px) */
@media (max-width: 480px) {
  .splash__stage { transform: scale(0.7); }
  .splash__brand { font-size: 20px; }
  .splash__motto { font-size: 9px; max-width: 220px; }

  .pre-logo { transform: scale(0.8); }
  .pre-bar { width: 160px; }
  .pre-status { font-size: 11px; }
}

/* Mobile landscape */
@media (max-width: 768px) and (orientation: landscape) {
  .splash__stage { transform: scale(0.6); }
  .splash__brand { font-size: 18px; }
  .splash__motto { font-size: 8px; }
}
</style>
