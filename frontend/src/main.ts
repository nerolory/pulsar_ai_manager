import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { persistencePlugin, initStorage } from '@/plugins/persistence'
import App from './App.vue'
import './assets/main.scss'

initStorage()

const pinia = createPinia()
pinia.use(persistencePlugin)

const app = createApp(App)
app.use(pinia)

app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue error]', info, err)
  console.error('[Vue component]', instance?.$options?.name ?? 'unknown')
}

app.config.warnHandler = (msg, instance, trace) => {
  console.warn('[Vue warn]', msg, trace)
}

window.addEventListener('unhandledrejection', (e) => {
  console.error('[Unhandled Promise]', e.reason)
})

window.addEventListener('error', (e) => {
  console.error('[Global error]', e.message, e.filename, e.lineno)
})

app.mount('#app')
