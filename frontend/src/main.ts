import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { persistencePlugin, initStorage } from '@/plugins/persistence'
import App from './App.vue'
import './assets/main.scss'
import './themes/index.scss'

console.log(
  '\n%c ◉ PULSAR AI MANAGER ◉ %c\n',
  'background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; font-size: 16px; font-weight: 800; padding: 8px 20px; border-radius: 8px; letter-spacing: 2px;',
  ''
)
console.log('%c  Менеджер ИИ-чатов  ', 'color: #8b5cf6; font-size: 11px; letter-spacing: 1px;')

initStorage()

const pinia = createPinia()
pinia.use(persistencePlugin)

const app = createApp(App)
app.use(pinia)

app.config.errorHandler = (error) => {
  console.error('[PulsarAI]', (error as Error)?.message ?? 'Неизвестная ошибка')
}

window.addEventListener('unhandledrejection', (event) => {
  console.error('[PulsarAI]', (event.reason as Error)?.message ?? event.reason)
})

window.addEventListener('error', (event) => {
  console.error('[PulsarAI]', event.message)
})

app.mount('#app')
