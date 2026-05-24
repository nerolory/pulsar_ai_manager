<template>
  <div class="preloader">
    <div class="pre-logo">
      <div class="pre-icon">P</div>
      <div class="pre-name">Pulsar<span>AI</span></div>
    </div>
    <div class="pre-bar"><div class="pre-fill" /></div>
    <div class="pre-status">{{ status }}</div>
    <div class="pre-dots">
      <div class="pre-dot" />
      <div class="pre-dot" />
      <div class="pre-dot" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const emit = defineEmits<{ done: [] }>()

const statuses = [
  'Инициализация...',
  'Загрузка конфигурации...',
  'Подключение к сервисам...',
  'Проверка API-ключей...',
  'Готово!',
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
.pre-dots { display: flex; gap: 6px; }
.pre-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--accent); opacity: 0.3;
  animation: dotpulse 1.4s infinite;
}
.pre-dot:nth-child(2) { animation-delay: .2s; }
.pre-dot:nth-child(3) { animation-delay: .4s; }
@keyframes dotpulse { 0%,60%,100%{opacity:.3} 30%{opacity:1} }
</style>
